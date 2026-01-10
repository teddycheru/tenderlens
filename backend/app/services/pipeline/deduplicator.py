# backend/app/services/pipeline/deduplicator.py
"""
Deduplication service using multiple strategies to detect duplicate tenders.
"""

from typing import Dict, Tuple, Optional
from sqlalchemy.orm import Session
from Levenshtein import ratio as levenshtein_ratio
from datetime import timedelta

from app.models.tender import Tender
from app.models.duplicate_log import DuplicateLog


class TenderDeduplicator:
    """Multi-strategy deduplication for tenders."""

    def __init__(self, fuzzy_threshold: float = 0.85):
        self.fuzzy_threshold = fuzzy_threshold

    def check_duplicate(
        self,
        db: Session,
        tender_data: Dict
    ) -> Tuple[bool, Optional[Dict]]:
        """
        Check if tender is a duplicate using multiple strategies.

        Returns:
            (is_duplicate, duplicate_info)
        """

        # Strategy 1: Hash-based exact match (external_id)
        if tender_data.get('external_id'):
            exact_match = db.query(Tender).filter(
                Tender.external_id == tender_data['external_id']
            ).first()

            if exact_match:
                return True, {
                    "method": "hash_exact",
                    "tender_id": exact_match.id,
                    "score": 1.0,
                    "details": {"matched_field": "external_id"}
                }

        # Strategy 2: URL match
        if tender_data.get('source_url'):
            url_match = db.query(Tender).filter(
                Tender.source_url == tender_data['source_url']
            ).first()

            if url_match:
                return True, {
                    "method": "url_match",
                    "tender_id": url_match.id,
                    "score": 1.0,
                    "details": {"matched_field": "source_url"}
                }

        # Strategy 3: Fuzzy title matching
        fuzzy_match = self._fuzzy_title_match(db, tender_data)
        if fuzzy_match:
            return True, fuzzy_match

        return False, None

    def _fuzzy_title_match(self, db: Session, tender_data: Dict) -> Optional[Dict]:
        """
        Check for similar titles using fuzzy matching.
        """
        title = tender_data.get('title', '')
        if not title or len(title) < 10:
            return None

        # Get candidates: similar deadline (±2 days) and same category
        deadline = tender_data.get('deadline')
        category = tender_data.get('category')

        query = db.query(Tender)

        # Filter by deadline range if available
        if deadline:
            query = query.filter(
                Tender.deadline >= deadline - timedelta(days=2),
                Tender.deadline <= deadline + timedelta(days=2)
            )

        # Filter by category if available
        if category:
            query = query.filter(Tender.category == category)

        # Limit to recent tenders (last 90 days)
        candidates = query.limit(100).all()

        # Check fuzzy similarity
        best_match = None
        best_score = 0.0

        for candidate in candidates:
            similarity = levenshtein_ratio(title.lower(), candidate.title.lower())

            if similarity > self.fuzzy_threshold and similarity > best_score:
                best_score = similarity
                best_match = candidate

        if best_match:
            return {
                "method": "fuzzy_title",
                "tender_id": best_match.id,
                "score": best_score,
                "details": {
                    "title_similarity": best_score,
                    "original_title": title,
                    "matched_title": best_match.title
                }
            }

        return None

    def log_duplicate(
        self,
        db: Session,
        staging_id: int,
        duplicate_info: Dict
    ):
        """Log detected duplicate for monitoring."""
        duplicate_log = DuplicateLog(
            staging_id=staging_id,
            existing_tender_id=duplicate_info['tender_id'],
            detection_method=duplicate_info['method'],
            similarity_score=duplicate_info['score'],
            match_details=duplicate_info.get('details', {}),
            action="skipped",
            confidence=duplicate_info['score']
        )
        db.add(duplicate_log)
        db.commit()


tender_deduplicator = TenderDeduplicator()
