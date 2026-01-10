"""
Celery tasks for asynchronous AI processing.
"""

import asyncio
from typing import List, Dict
from app.workers.celery_app import celery_app
from app.database import SessionLocal
from app.models.tender import Tender


@celery_app.task(name="process_tender_ai", bind=True, max_retries=3)
def process_tender_ai_task(self, tender_id: str, doc_url: str = None, force_reprocess: bool = False) -> Dict:
    """
    Async task to process tender with AI.

    Args:
        tender_id: Tender UUID
        doc_url: Optional document URL to process
        force_reprocess: Force reprocessing even if already processed

    Returns:
        Processing result dictionary

    Raises:
        Exception: If processing fails after retries
    """
    db = SessionLocal()
    try:
        from app.services.ai.ai_service import ai_service

        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                ai_service.process_tender_document(db, tender_id, doc_url, force_reprocess)
            )
            return result
        finally:
            loop.close()

    except Exception as e:
        # Retry on failure
        print(f"AI processing error for tender {tender_id}: {e}")
        if self.request.retries < self.max_retries:
            # Exponential backoff: 10s, 30s, 90s
            countdown = 10 * (3 ** self.request.retries)
            raise self.retry(exc=e, countdown=countdown)
        else:
            return {
                "tender_id": tender_id,
                "error": str(e),
                "status": "failed"
            }
    finally:
        db.close()


@celery_app.task(name="batch_process_tenders")
def batch_process_tenders_task(tender_ids: List[str]) -> Dict:
    """
    Process multiple tenders in batch.

    Args:
        tender_ids: List of tender UUIDs

    Returns:
        Dictionary with batch processing results
    """
    results = []
    task_ids = []

    for tender_id in tender_ids:
        # Queue individual tasks
        task = process_tender_ai_task.delay(tender_id)
        task_ids.append(task.id)

    return {
        "total": len(tender_ids),
        "task_ids": task_ids,
        "status": "queued"
    }


@celery_app.task(name="process_unprocessed_tenders")
def process_unprocessed_tenders_task(limit: int = 10) -> Dict:
    """
    Automatically process unprocessed tenders.

    This can be scheduled to run periodically to process new tenders.

    Args:
        limit: Maximum number of tenders to process

    Returns:
        Dictionary with processing results
    """
    db = SessionLocal()
    try:
        # Find unprocessed tenders
        unprocessed_tenders = db.query(Tender).filter(
            Tender.ai_processed == False
        ).limit(limit).all()

        tender_ids = [str(tender.id) for tender in unprocessed_tenders]

        if tender_ids:
            return batch_process_tenders_task(tender_ids)
        else:
            return {
                "total": 0,
                "message": "No unprocessed tenders found"
            }

    finally:
        db.close()


@celery_app.task(name="reprocess_tender_ai")
def reprocess_tender_ai_task(tender_id: str) -> Dict:
    """
    Force reprocessing of a tender (ignores cache).

    Args:
        tender_id: Tender UUID

    Returns:
        Processing result dictionary
    """
    db = SessionLocal()
    try:
        from app.services.ai.ai_service import ai_service

        # Invalidate cache first
        ai_service.invalidate_cache(tender_id)

        # Reprocess
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                ai_service.process_tender_document(db, tender_id, force_reprocess=True)
            )
            return result
        finally:
            loop.close()

    except Exception as e:
        return {
            "tender_id": tender_id,
            "error": str(e),
            "status": "failed"
        }
    finally:
        db.close()
