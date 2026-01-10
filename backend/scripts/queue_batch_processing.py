#!/usr/bin/env python3
"""
Queue batch processing of unprocessed tenders using Celery.
This is the async way - non-blocking task queueing.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal
from app.models.tender import Tender
from app.workers.ai_tasks import process_tender_ai_task

def queue_batch_processing():
    """Queue all unprocessed tenders for async processing."""
    db = SessionLocal()
    try:
        # Get all unprocessed tenders
        unprocessed = db.query(Tender).filter(
            Tender.ai_processed == False
        ).all()

        total = len(unprocessed)
        print(f"\nQueueing {total} tenders for async AI processing...")
        print("=" * 70)

        if total == 0:
            print("✓ No unprocessed tenders found. All done!")
            return

        task_ids = []
        for idx, tender in enumerate(unprocessed, 1):
            tender_id = str(tender.id)
            try:
                # Queue the task
                task = process_tender_ai_task.delay(tender_id)
                task_ids.append(task.id)
                print(f"[{idx}/{total}] Queued: {tender.title[:50]}... (Task: {task.id[:8]}...)")
            except Exception as e:
                print(f"[{idx}/{total}] FAILED to queue: {str(e)[:50]}")

        print("\n" + "=" * 70)
        print(f"✓ Successfully queued {len(task_ids)} tenders for async processing")
        print(f"\nTask IDs: {task_ids[:3]}..." if len(task_ids) > 3 else f"\nTask IDs: {task_ids}")
        print(f"\nMonitor progress at: http://localhost:5555")
        print("Tasks will process in the background via Celery workers")

    finally:
        db.close()


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("TENDER BATCH QUEUEING (ASYNC)")
    print("=" * 70)

    queue_batch_processing()
