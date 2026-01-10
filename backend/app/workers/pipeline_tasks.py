# backend/app/workers/pipeline_tasks.py
"""
Celery tasks for pipeline operations.
"""

from celery import Task
from app.celery_app import celery_app
from app.database import SessionLocal
from app.models.tender_staging import TenderStaging
from datetime import datetime, timedelta


@celery_app.task(name="app.workers.pipeline_tasks.cleanup_old_staging")
def cleanup_old_staging(days: int = 30) -> dict:
    """
    Clean up old staging records (older than specified days).

    Args:
        days: Number of days to keep staging records

    Returns:
        Cleanup summary
    """
    db = SessionLocal()

    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Delete old staging records
        deleted_count = db.query(TenderStaging).filter(
            TenderStaging.created_at < cutoff_date,
            TenderStaging.status.in_(["loaded", "duplicate", "failed"])
        ).delete()

        db.commit()

        return {
            "status": "success",
            "records_deleted": deleted_count,
            "cutoff_date": cutoff_date.isoformat()
        }

    except Exception as e:
        db.rollback()
        return {
            "status": "failed",
            "error": str(e)
        }
    finally:
        db.close()
