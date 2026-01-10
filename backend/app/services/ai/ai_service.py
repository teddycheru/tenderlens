"""
Main AI service orchestrator for tender processing.
"""

from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, Optional
import httpx

from app.models.tender import Tender
from app.services.ai.document_parser import document_parser
from app.services.ai.summarizer import summarizer
from app.services.ai.entity_extractor import entity_extractor
from app.services.cache import cache_service
from app.core.ai_config import ai_settings


class AIService:
    """
    Main AI orchestration service.
    Coordinates document parsing, summarization, and entity extraction.
    """

    async def process_tender_document(
        self,
        db: Session,
        tender_id: str,
        doc_url: Optional[str] = None,
        force_reprocess: bool = False
    ) -> Dict:
        """
        Full AI processing pipeline for a tender.

        Pipeline:
        1. Check cache for existing results (unless force_reprocess)
        2. Download document if URL provided
        3. Extract text from document
        4. Generate AI summary
        5. Extract entities
        6. Cache results
        7. Update database

        Args:
            db: Database session
            tender_id: Tender UUID
            doc_url: Optional document URL to process
            force_reprocess: Force reprocessing even if cached

        Returns:
            Dictionary with processing results

        Raises:
            ValueError: If tender not found
            Exception: If processing fails
        """
        tender = db.query(Tender).filter(Tender.id == tender_id).first()
        if not tender:
            raise ValueError(f"Tender not found: {tender_id}")

        result = {
            "tender_id": str(tender_id),
            "summary": None,
            "entities": None,
            "quick_scan": None,
            "cached": False,
            "processing_time_ms": 0
        }

        start_time = datetime.now()

        # Check cache first (unless force reprocess)
        if not force_reprocess:
            cache_key_summary = cache_service.cache_key_tender_summary(str(tender_id))
            cache_key_entities = cache_service.cache_key_tender_entities(str(tender_id))

            cached_summary = cache_service.get(cache_key_summary)
            cached_entities = cache_service.get(cache_key_entities)

            if cached_summary and cached_entities:
                result["summary"] = cached_summary
                result["entities"] = cached_entities
                result["quick_scan"] = cached_summary[:100] + "..." if len(cached_summary) > 100 else cached_summary
                result["cached"] = True
                result["processing_time_ms"] = int((datetime.now() - start_time).total_seconds() * 1000)
                return result

        # Step 1: Get text content
        text_content = ""

        # Use doc_url if provided, otherwise use tender's doc_url
        url_to_use = doc_url or (tender.doc_url if hasattr(tender, 'doc_url') else None)

        if url_to_use:
            # Download and parse document
            try:
                async with httpx.AsyncClient(timeout=ai_settings.AI_TIMEOUT) as client:
                    response = await client.get(url_to_use)
                    response.raise_for_status()
                    file_content = response.content
                    filename = url_to_use.split('/')[-1]

                    text_content = document_parser.extract_text(file_content, filename)
                    tender.raw_text = text_content
                    tender.word_count = document_parser.get_word_count(text_content)
            except Exception as e:
                print(f"Document download/parse error: {e}")
                # Fallback to description
                text_content = tender.description or ""
        else:
            # Use existing description
            text_content = tender.description or ""

        if not text_content:
            raise ValueError("No text content available for processing")

        # Step 2: Generate summary
        if summarizer.is_available():
            try:
                # FIX #3 & #6: Pass CSV fields for accurate summaries
                # Format deadline/closing_date if available
                closing_date_str = None
                if tender.deadline:
                    closing_date_str = tender.deadline.strftime("%B %d, %Y") if hasattr(tender.deadline, 'strftime') else str(tender.deadline)

                # Format published_date if available
                published_date_str = None
                if tender.published_date:
                    published_date_str = tender.published_date.strftime("%B %d, %Y") if hasattr(tender.published_date, 'strftime') else str(tender.published_date)

                # Pass both title and description plus CSV fields to summarizer for better extraction
                summary = summarizer.summarize_tender(
                    text_content,
                    title=tender.title,
                    closing_date=closing_date_str,  # FIX #3: Pass closing date
                    region=tender.region,  # FIX #6: Pass region
                    category=tender.category,  # FIX #6: Pass category
                    published_date=published_date_str,  # FIX #6: Pass published date
                    tor_url=tender.tor_url,  # Pass TOR download link
                    language=tender.language  # Pass document language
                )
                tender.ai_summary = summary
                result["summary"] = summary

                # Cache summary
                cache_key_summary = cache_service.cache_key_tender_summary(str(tender_id))
                cache_service.set(cache_key_summary, summary, ttl=ai_settings.AI_CACHE_TTL)
            except Exception as e:
                print(f"Summarization error: {e}")
                result["summary"] = f"Summary generation failed: {str(e)}"
        else:
            result["summary"] = "AI summarization not available (API key not configured)"

        # Step 3: Extract entities
        if entity_extractor.is_available():
            try:
                entities = entity_extractor.extract_entities(text_content)
                tender.extracted_entities = entities
                result["entities"] = entities

                # Cache entities
                cache_key_entities = cache_service.cache_key_tender_entities(str(tender_id))
                cache_service.set(cache_key_entities, entities, ttl=ai_settings.AI_CACHE_TTL)
            except Exception as e:
                print(f"Entity extraction error: {e}")
                result["entities"] = {}
        else:
            result["entities"] = {}
            print("Entity extraction not available (spaCy model not loaded)")

        # Step 4: Generate quick scan
        if summarizer.is_available() and result["summary"]:
            try:
                quick_scan = summarizer.quick_scan(tender.title, tender.description or "")
                result["quick_scan"] = quick_scan

                # Cache quick scan
                cache_key_quick_scan = cache_service.cache_key_tender_quick_scan(str(tender_id))
                cache_service.set(cache_key_quick_scan, quick_scan, ttl=ai_settings.AI_CACHE_TTL)
            except Exception as e:
                print(f"Quick scan error: {e}")
                # Fallback to truncated summary
                result["quick_scan"] = result["summary"][:100] if result["summary"] else ""

        # Update tender AI processing status
        tender.ai_processed = True
        tender.ai_processed_at = datetime.utcnow()
        db.commit()

        result["processing_time_ms"] = int((datetime.now() - start_time).total_seconds() * 1000)
        return result

    def process_quick_scan_only(
        self,
        db: Session,
        tender_id: str
    ) -> str:
        """
        Generate only quick scan for tender card (lightweight operation).

        Args:
            db: Database session
            tender_id: Tender UUID

        Returns:
            Quick scan text

        Raises:
            ValueError: If tender not found
        """
        # Check cache first
        cache_key = cache_service.cache_key_tender_quick_scan(str(tender_id))
        cached_quick_scan = cache_service.get(cache_key)
        if cached_quick_scan:
            return cached_quick_scan

        tender = db.query(Tender).filter(Tender.id == tender_id).first()
        if not tender:
            raise ValueError(f"Tender not found: {tender_id}")

        # If already has AI summary, use that
        if tender.ai_summary:
            quick_scan = tender.ai_summary[:100] + "..." if len(tender.ai_summary) > 100 else tender.ai_summary
            cache_service.set(cache_key, quick_scan, ttl=ai_settings.AI_CACHE_TTL)
            return quick_scan

        # Generate new quick scan
        if summarizer.is_available():
            try:
                quick_scan = summarizer.quick_scan(tender.title, tender.description or "")
                cache_service.set(cache_key, quick_scan, ttl=ai_settings.AI_CACHE_TTL)
                return quick_scan
            except Exception as e:
                print(f"Quick scan generation failed: {e}")
                return "AI processing unavailable"
        else:
            return "AI not configured"

    def get_processing_status(self, db: Session, tender_id: str) -> Dict:
        """
        Get AI processing status for a tender.

        Args:
            db: Database session
            tender_id: Tender UUID

        Returns:
            Dictionary with processing status

        Raises:
            ValueError: If tender not found
        """
        tender = db.query(Tender).filter(Tender.id == tender_id).first()
        if not tender:
            raise ValueError(f"Tender not found: {tender_id}")

        return {
            "tender_id": str(tender_id),
            "ai_processed": tender.ai_processed,
            "ai_processed_at": tender.ai_processed_at.isoformat() if tender.ai_processed_at else None,
            "has_summary": bool(tender.ai_summary),
            "has_entities": bool(tender.extracted_entities),
            "word_count": tender.word_count
        }

    def invalidate_cache(self, tender_id: str) -> bool:
        """
        Invalidate all cached AI results for a tender.

        Args:
            tender_id: Tender UUID

        Returns:
            True if successful, False otherwise
        """
        return cache_service.invalidate_tender_cache(str(tender_id))


# Global AI service instance - initialized lazily to avoid blocking app startup
_ai_service_instance = None

def get_ai_service():
    """
    Get or initialize AI service lazily.

    This prevents blocking app startup when AI models are initializing.
    The service is loaded on first use instead of at import time.
    """
    global _ai_service_instance
    if _ai_service_instance is None:
        _ai_service_instance = AIService()
    return _ai_service_instance

# For backwards compatibility, create a property-like object
class _LazyAIService:
    """Lazy loader for AI service."""
    def __getattr__(self, name):
        return getattr(get_ai_service(), name)

ai_service = _LazyAIService()
