"""
Celery tasks for embedding generation.

Tasks:
- generate_tender_embedding_task: Generate embedding for a single tender
- generate_profile_embedding_task: Generate embedding for a company profile
- batch_generate_embeddings_task: Generate embeddings for multiple tenders
"""

from app.workers.celery_app import celery_app
from app.services.embedding_service import embedding_service
from app.models.tender import Tender
from app.models.company_profile import CompanyTenderProfile
from app.database import SessionLocal
from datetime import datetime, timezone
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


@celery_app.task(
    name="generate_tender_embedding",
    bind=True,
    max_retries=3,
    default_retry_delay=60
)
def generate_tender_embedding_task(self, tender_id: str) -> Dict:
    """
    Generate embedding for a newly created or updated tender.

    Args:
        tender_id: UUID of the tender

    Returns:
        Dict with status and embedding info
    """
    db = SessionLocal()
    try:
        tender = db.query(Tender).filter(Tender.id == tender_id).first()
        if not tender:
            logger.error(f"Tender {tender_id} not found")
            return {"error": "Tender not found", "tender_id": tender_id}

        # Generate embedding
        logger.info(f"Generating embedding for tender {tender_id}")
        embedding = embedding_service.generate_tender_embedding(tender)

        # Update tender
        tender.content_embedding = embedding
        tender.embedding_updated_at = datetime.now(timezone.utc)
        tender.recommendation_status = 'active'

        db.commit()

        logger.info(f"Successfully generated embedding for tender {tender_id}")
        return {
            "tender_id": str(tender_id),
            "status": "success",
            "embedding_dimensions": len(embedding)
        }

    except Exception as e:
        logger.error(f"Error generating embedding for tender {tender_id}: {e}")
        db.rollback()
        # Retry on failure
        raise self.retry(exc=e)

    finally:
        db.close()


@celery_app.task(
    name="generate_profile_embedding",
    bind=True,
    max_retries=3,
    default_retry_delay=60
)
def generate_profile_embedding_task(self, profile_id: str) -> Dict:
    """
    Generate embedding for a company profile.

    Args:
        profile_id: UUID of the company profile

    Returns:
        Dict with status and embedding info
    """
    db = SessionLocal()
    try:
        profile = db.query(CompanyTenderProfile).filter(
            CompanyTenderProfile.id == profile_id
        ).first()

        if not profile:
            logger.error(f"Profile {profile_id} not found")
            return {"error": "Profile not found", "profile_id": profile_id}

        # Generate embedding
        logger.info(f"Generating embedding for profile {profile_id}")
        embedding = embedding_service.generate_profile_embedding(profile)

        # Update profile
        profile.profile_embedding = embedding
        profile.embedding_updated_at = datetime.now(timezone.utc)

        db.commit()

        logger.info(f"Successfully generated embedding for profile {profile_id}")
        return {
            "profile_id": str(profile_id),
            "status": "success",
            "embedding_dimensions": len(embedding)
        }

    except Exception as e:
        logger.error(f"Error generating embedding for profile {profile_id}: {e}")
        db.rollback()
        raise self.retry(exc=e)

    finally:
        db.close()


@celery_app.task(name="batch_generate_embeddings")
def batch_generate_embeddings_task(
    tender_ids: List[str] = None,
    batch_size: int = 100,
    process_historical: bool = False
) -> Dict:
    """
    Generate embeddings for multiple tenders in batches.

    Useful for:
    - Initial setup with historical data
    - Re-processing after model upgrades
    - Backfilling missing embeddings

    Args:
        tender_ids: Specific tender IDs to process. If None, processes all without embeddings.
        batch_size: Number of tenders to queue at once
        process_historical: Include historical tenders (default: False, only active)

    Returns:
        Dict with batch processing status
    """
    db = SessionLocal()
    try:
        # If no specific IDs provided, find tenders without embeddings
        if tender_ids is None:
            query = db.query(Tender).filter(
                Tender.content_embedding.is_(None)
            )

            # Filter by status unless processing historical data
            if not process_historical:
                query = query.filter(
                    Tender.recommendation_status == 'active'
                )

            tender_ids = [str(t.id) for t in query.all()]

        total_tenders = len(tender_ids)
        logger.info(f"Batch processing {total_tenders} tenders in batches of {batch_size}")

        # Process in batches to avoid overwhelming the system
        task_ids = []
        for i in range(0, total_tenders, batch_size):
            batch = tender_ids[i:i+batch_size]

            # Queue tasks for this batch
            for tender_id in batch:
                task = generate_tender_embedding_task.delay(tender_id)
                task_ids.append(task.id)

            logger.info(f"Queued batch {i//batch_size + 1}: {len(batch)} tenders")

        return {
            "status": "queued",
            "total_tenders": total_tenders,
            "batches": (total_tenders + batch_size - 1) // batch_size,
            "task_ids": task_ids[:10],  # Return first 10 for monitoring
            "message": f"Queued {total_tenders} tenders for embedding generation"
        }

    except Exception as e:
        logger.error(f"Batch embedding generation failed: {str(e)}")
        raise e

    finally:
        db.close()
