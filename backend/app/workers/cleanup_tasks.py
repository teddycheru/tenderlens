"""
Celery tasks for cleanup and maintenance.

Tasks:
- expire_old_tenders_task: Mark tenders with passed deadlines as expired
"""

from app.workers.celery_app import celery_app
from app.models.tender import Tender
from app.models.user_interaction import UserInteraction
from app.database import SessionLocal
from datetime import datetime, timezone
from typing import Dict
import logging

logger = logging.getLogger(__name__)


@celery_app.task(name="expire_old_tenders")
def expire_old_tenders_task() -> Dict:
    """
    Run daily: Mark tenders with passed deadlines as expired.
    Remove from recommendation pool unless saved by users.

    Tender Status Flow:
    - active -> expired (if deadline passed and not saved)
    - active -> expired_saved (if deadline passed but saved by user)

    Returns:
        Dict with cleanup statistics
    """
    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc).date()

        # Find active tenders with passed deadlines
        expired_tenders = db.query(Tender).filter(
            Tender.recommendation_status == 'active',
            Tender.deadline < now
        ).all()

        expired_count = 0
        saved_count = 0

        logger.info(f"Processing {len(expired_tenders)} tenders with passed deadlines")

        for tender in expired_tenders:
            # Check if tender is saved by any user
            is_saved = db.query(UserInteraction).filter(
                UserInteraction.tender_id == tender.id,
                UserInteraction.interaction_type == 'save'
            ).first() is not None

            if is_saved:
                tender.recommendation_status = 'expired_saved'
                saved_count += 1
            else:
                tender.recommendation_status = 'expired'
                expired_count += 1

        db.commit()

        result = {
            "expired": expired_count,
            "expired_saved": saved_count,
            "total_processed": len(expired_tenders),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        logger.info(f"Cleanup completed: {expired_count} expired, {saved_count} saved")
        return result

    except Exception as e:
        logger.error(f"Error during tender cleanup: {e}")
        db.rollback()
        raise e

    finally:
        db.close()
