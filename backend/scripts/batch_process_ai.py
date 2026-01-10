#!/usr/bin/env python3
"""
Batch AI Processing Script

Process multiple tenders with AI (summarization + entity extraction) in bulk.

Usage:
    python scripts/batch_process_ai.py --all                    # Process all unprocessed tenders
    python scripts/batch_process_ai.py --limit 100              # Process 100 unprocessed tenders
    python scripts/batch_process_ai.py --reprocess              # Reprocess ALL tenders (overwrites)
    python scripts/batch_process_ai.py --ids id1,id2,id3        # Process specific tender IDs
    python scripts/batch_process_ai.py --category IT            # Process all unprocessed in category
    python scripts/batch_process_ai.py --recent 7               # Process unprocessed from last 7 days

Features:
    - Queues tenders for async Celery processing
    - Shows progress and task IDs
    - Non-blocking - returns immediately with task info
    - Can be run while app is running
    - Supports filtering by category, region, date range
"""

import os
import sys
import argparse
import logging
from datetime import datetime, timedelta

# Setup Django/SQLAlchemy context
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models.tender import Tender
from app.workers.ai_tasks import batch_process_tenders_task

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BatchAIProcessor:
    """Process multiple tenders with AI in batch."""

    def __init__(self):
        """Initialize database session."""
        engine = create_engine(settings.DATABASE_URL)
        self.Session = sessionmaker(bind=engine)
        self.db = self.Session()

    def get_tenders(self, filter_type: str, limit: int = None, **kwargs) -> list:
        """
        Get tenders based on filter type.

        Args:
            filter_type: Type of filter ('all', 'limit', 'reprocess', 'ids', 'category', 'recent')
            limit: Maximum number of tenders to return
            **kwargs: Additional filter parameters

        Returns:
            List of tender IDs to process
        """
        query = self.db.query(Tender)

        if filter_type == "all":
            # All unprocessed tenders
            logger.info("📋 Finding all unprocessed tenders...")
            query = query.filter(Tender.ai_processed == False)

        elif filter_type == "limit":
            # Limit number of unprocessed tenders
            limit_count = kwargs.get("count", 100)
            logger.info(f"📋 Finding up to {limit_count} unprocessed tenders...")
            query = query.filter(Tender.ai_processed == False)

        elif filter_type == "reprocess":
            # All tenders (will reprocess even if already processed)
            logger.info("📋 Finding ALL tenders for reprocessing...")
            # No filter - get all

        elif filter_type == "ids":
            # Specific tender IDs
            tender_ids = kwargs.get("ids", [])
            logger.info(f"📋 Finding {len(tender_ids)} specific tenders...")
            query = query.filter(Tender.id.in_(tender_ids))

        elif filter_type == "category":
            # Category filter
            category = kwargs.get("category")
            logger.info(f"📋 Finding unprocessed tenders in category '{category}'...")
            query = query.filter(
                (Tender.ai_processed == False) &
                (Tender.category == category)
            )

        elif filter_type == "recent":
            # Recent tenders (unprocessed from last N days)
            days = kwargs.get("days", 7)
            since_date = datetime.utcnow() - timedelta(days=days)
            logger.info(f"📋 Finding unprocessed tenders from last {days} days...")
            query = query.filter(
                (Tender.ai_processed == False) &
                (Tender.created_at >= since_date)
            )

        # Apply limit if specified
        if limit and limit_count > 0:
            query = query.limit(limit_count)

        # Order by created_at to process newest first
        query = query.order_by(Tender.created_at.desc())

        tenders = query.all()
        return [str(tender.id) for tender in tenders]

    def process(self, tender_ids: list) -> dict:
        """
        Queue tenders for AI processing.

        Args:
            tender_ids: List of tender IDs to process

        Returns:
            Processing result with task IDs and metadata
        """
        if not tender_ids:
            logger.warning("⚠️  No tenders to process")
            return {"queued": 0, "message": "No tenders matched the filter"}

        logger.info(f"🤖 Queueing {len(tender_ids)} tenders for AI processing...")

        try:
            # Queue batch processing task
            task = batch_process_tenders_task.delay(tender_ids)

            logger.info(f"✅ Task queued successfully!")
            logger.info(f"   Task ID: {task.id}")
            logger.info(f"   Tenders to process: {len(tender_ids)}")
            logger.info("")
            logger.info("📊 Processing will happen in background...")
            logger.info("   Monitor progress with: celery -A app.workers.celery_app inspect active")
            logger.info("   Or view at: http://localhost:5555 (if Flower is running)")

            return {
                "queued": len(tender_ids),
                "task_id": task.id,
                "tender_ids": tender_ids[:10],  # Show first 10 in output
                "total_tenders": len(tender_ids),
                "message": f"✅ Queued {len(tender_ids)} tenders for AI processing"
            }

        except Exception as e:
            logger.error(f"❌ Failed to queue AI processing: {e}")
            return {"queued": 0, "error": str(e)}

    def close(self):
        """Close database session."""
        self.db.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Batch AI processing for tenders",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/batch_process_ai.py --all              # Process all unprocessed
  python scripts/batch_process_ai.py --limit 50         # Process 50 unprocessed
  python scripts/batch_process_ai.py --reprocess        # Reprocess all tenders
  python scripts/batch_process_ai.py --category IT      # Process unprocessed in IT category
  python scripts/batch_process_ai.py --recent 7         # Process unprocessed from last 7 days
  python scripts/batch_process_ai.py --ids uuid1,uuid2  # Process specific IDs
        """
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Process all unprocessed tenders"
    )

    parser.add_argument(
        "--limit",
        type=int,
        metavar="N",
        help="Process up to N unprocessed tenders (default: 100)"
    )

    parser.add_argument(
        "--reprocess",
        action="store_true",
        help="Reprocess ALL tenders (overwrites existing summaries)"
    )

    parser.add_argument(
        "--ids",
        type=str,
        metavar="ID1,ID2,...",
        help="Process specific tender IDs (comma-separated)"
    )

    parser.add_argument(
        "--category",
        type=str,
        metavar="CATEGORY",
        help="Process unprocessed tenders in specific category"
    )

    parser.add_argument(
        "--recent",
        type=int,
        metavar="DAYS",
        help="Process unprocessed tenders from last N days"
    )

    args = parser.parse_args()

    # Determine which mode to run
    processor = BatchAIProcessor()

    try:
        if args.all:
            tender_ids = processor.get_tenders("all")

        elif args.limit:
            tender_ids = processor.get_tenders("limit", count=args.limit)

        elif args.reprocess:
            tender_ids = processor.get_tenders("reprocess")

        elif args.ids:
            ids_list = [id.strip() for id in args.ids.split(",")]
            tender_ids = processor.get_tenders("ids", ids=ids_list)

        elif args.category:
            tender_ids = processor.get_tenders("category", category=args.category)

        elif args.recent:
            tender_ids = processor.get_tenders("recent", days=args.recent)

        else:
            # Default: process 100 unprocessed tenders
            tender_ids = processor.get_tenders("limit", count=100)

        # Process the tenders
        result = processor.process(tender_ids)

        # Print result
        if "error" not in result:
            print(f"\n✅ Successfully queued {result['queued']} tenders")
            print(f"Task ID: {result['task_id']}")
        else:
            print(f"\n❌ Error: {result['error']}")
            sys.exit(1)

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        sys.exit(1)

    finally:
        processor.close()


if __name__ == "__main__":
    main()
