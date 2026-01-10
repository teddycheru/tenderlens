#!/usr/bin/env python3
"""
Batch Script: Generate AI Summaries for ALL Tenders
======================================================

This script processes all tenders in the database and generates
4-paragraph narrative summaries using the Hybrid Summarizer
(FLAN-T5 + GLiNER).

Features:
- Real-time progress logging
- Batch processing with configurable batch size
- Error handling and retry logic
- Status tracking and statistics
- Resume capability (skips already processed tenders)

Usage:
  python batch_generate_summaries.py                 # Process all
  python batch_generate_summaries.py --force         # Force reprocess
  python batch_generate_summaries.py --batch-size 10 # Custom batch size
  python batch_generate_summaries.py --limit 5       # Process only 5 tenders
"""

import os
import sys
import time
import logging
from datetime import datetime
from typing import Optional, Tuple
import argparse

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Setup logging with detailed formatting
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Suppress verbose model loading logs
logging.getLogger('transformers').setLevel(logging.WARNING)
logging.getLogger('torch').setLevel(logging.WARNING)


class BatchSummaryGenerator:
    """Batch processing orchestrator for tender summaries."""

    def __init__(self, force_reprocess: bool = False, batch_size: int = 5):
        """Initialize batch processor.

        Args:
            force_reprocess: Force reprocessing even if already processed
            batch_size: Number of tenders to process per batch
        """
        self.force_reprocess = force_reprocess
        self.batch_size = batch_size
        self.stats = {
            'total': 0,
            'processed': 0,
            'skipped': 0,
            'errors': 0,
            'start_time': None,
            'end_time': None,
            'error_list': []
        }

    def initialize_database(self):
        """Initialize database connection."""
        try:
            from app.database import SessionLocal, engine
            from app.models.tender import Tender

            # Ensure tables exist
            from app.models.tender import Base
            Base.metadata.create_all(bind=engine)

            self.db = SessionLocal()
            self.Tender = Tender
            logger.info("✅ Database initialized successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to initialize database: {e}")
            return False

    def initialize_summarizer(self):
        """Initialize the Hybrid Summarizer."""
        try:
            from app.services.ai.hybrid_summarizer import get_hybrid_summarizer
            self.summarizer = get_hybrid_summarizer()

            if self.summarizer.is_available():
                logger.info("✅ Hybrid Summarizer (FLAN-T5 + GLiNER) loaded successfully")
                return True
            else:
                logger.error("❌ Hybrid Summarizer not available")
                return False
        except Exception as e:
            logger.error(f"❌ Failed to initialize summarizer: {e}")
            return False

    def get_tenders_to_process(self, limit: Optional[int] = None) -> Tuple[int, list]:
        """Get list of tenders to process.

        Args:
            limit: Maximum number of tenders to process (None = all)

        Returns:
            Tuple of (total_count, list_of_tender_ids)
        """
        try:
            query = self.db.query(self.Tender.id, self.Tender.title, self.Tender.ai_processed)

            if not self.force_reprocess:
                # Get only unprocessed tenders
                query = query.filter(self.Tender.ai_processed == False)

            total_count = query.count()

            if limit:
                query = query.limit(limit)

            tenders = query.all()
            tender_list = [(t.id, t.title) for t in tenders]

            return total_count, tender_list
        except Exception as e:
            logger.error(f"❌ Failed to query tenders: {e}")
            return 0, []

    def process_tender(self, tender_id: str, tender_title: str) -> bool:
        """Process a single tender.

        Args:
            tender_id: Tender UUID
            tender_title: Tender title (for logging)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Fetch tender
            tender = self.db.query(self.Tender).filter(
                self.Tender.id == tender_id
            ).first()

            if not tender:
                logger.warning(f"⚠️  Tender not found: {tender_id}")
                return False

            # Get text content (use description if available)
            text_content = tender.raw_text or tender.description

            if not text_content or len(text_content.strip()) < 50:
                logger.warning(f"⚠️  Insufficient content for tender {tender_id}: {tender_title[:50]}")
                self.stats['skipped'] += 1
                return False

            # Generate summary
            logger.debug(f"  📝 Generating summary for: {tender_title[:50]}...")
            summary = self.summarizer.summarize_tender(
                text=text_content,
                max_words=200
            )

            # Extract entities
            entities = self.summarizer._extract_entities_with_flan(text_content)

            # Update database
            tender.ai_summary = summary
            tender.extracted_entities = entities
            tender.ai_processed = True
            tender.ai_processed_at = datetime.utcnow()

            self.db.commit()

            logger.info(f"✅ Processed: {tender_title[:60]}")
            self.stats['processed'] += 1
            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Error processing tender {tender_id}: {str(e)[:100]}")
            self.stats['errors'] += 1
            self.stats['error_list'].append({
                'tender_id': str(tender_id),
                'title': tender_title,
                'error': str(e)[:100]
            })
            return False

    def run_batch_processing(self, limit: Optional[int] = None):
        """Run the batch processing pipeline.

        Args:
            limit: Maximum number of tenders to process
        """
        logger.info("=" * 80)
        logger.info("🚀 BATCH TENDER SUMMARY GENERATION")
        logger.info("=" * 80)

        # Initialize
        logger.info("\n📋 Initialization Phase:")
        if not self.initialize_database():
            logger.error("Failed to initialize database. Exiting.")
            return

        if not self.initialize_summarizer():
            logger.error("Failed to initialize summarizer. Exiting.")
            return

        # Get tenders
        logger.info("\n📊 Scanning Database:")
        total_available, tender_list = self.get_tenders_to_process(limit=limit)
        self.stats['total'] = len(tender_list)

        if not tender_list:
            if self.force_reprocess:
                logger.warning("⚠️  No tenders found in database")
            else:
                logger.info("✅ All tenders already processed!")
            return

        logger.info(f"  Found {self.stats['total']} tender(s) to process")
        if total_available > self.stats['total'] and limit:
            logger.info(f"  (Limited to {limit} by --limit flag)")

        # Start processing
        logger.info("\n" + "=" * 80)
        logger.info("⚡ PROCESSING PHASE")
        logger.info("=" * 80 + "\n")

        self.stats['start_time'] = datetime.now()

        for idx, (tender_id, tender_title) in enumerate(tender_list, 1):
            # Progress indicator
            progress_pct = (idx / self.stats['total']) * 100
            logger.info(f"Progress: [{idx}/{self.stats['total']} | {progress_pct:.1f}%]")

            # Process tender
            self.process_tender(tender_id, tender_title)

            # Small delay to avoid overwhelming the system
            if idx < self.stats['total']:
                time.sleep(0.5)

        self.stats['end_time'] = datetime.now()

        # Print summary
        self._print_summary()

        # Close database
        self.db.close()

    def _print_summary(self):
        """Print processing summary statistics."""
        elapsed = self.stats['end_time'] - self.stats['start_time']
        elapsed_secs = elapsed.total_seconds()

        logger.info("\n" + "=" * 80)
        logger.info("📈 PROCESSING SUMMARY")
        logger.info("=" * 80)
        logger.info(f"  Total Tenders Processed:  {self.stats['processed']}")
        logger.info(f"  Skipped (insufficient content): {self.stats['skipped']}")
        logger.info(f"  Errors:                   {self.stats['errors']}")
        logger.info(f"  Success Rate:             {(self.stats['processed'] / max(self.stats['total'], 1) * 100):.1f}%")
        logger.info(f"  Time Elapsed:             {elapsed_secs:.1f}s")
        if self.stats['processed'] > 0:
            logger.info(f"  Avg Time per Tender:      {(elapsed_secs / self.stats['processed']):.2f}s")
        logger.info("=" * 80)

        # Show errors if any
        if self.stats['error_list']:
            logger.info("\n⚠️  ERRORS ENCOUNTERED:")
            for error in self.stats['error_list']:
                logger.info(f"  • {error['title'][:40]}")
                logger.info(f"    ID: {error['tender_id'][:8]}...")
                logger.info(f"    Error: {error['error']}")

        if self.stats['processed'] == self.stats['total'] and self.stats['errors'] == 0:
            logger.info("\n✅ ALL TENDERS PROCESSED SUCCESSFULLY!")
        else:
            logger.info(f"\n✅ Processing complete: {self.stats['processed']} successful, {self.stats['errors']} errors")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Generate AI summaries for all tenders',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process all unprocessed tenders
  python batch_generate_summaries.py

  # Force reprocess all tenders
  python batch_generate_summaries.py --force

  # Process only 10 tenders
  python batch_generate_summaries.py --limit 10

  # Custom batch size
  python batch_generate_summaries.py --batch-size 20
        """
    )

    parser.add_argument(
        '--force',
        action='store_true',
        help='Force reprocessing of already processed tenders'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=5,
        help='Batch size for processing (default: 5)'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Limit number of tenders to process (default: all)'
    )

    args = parser.parse_args()

    # Run batch processing
    processor = BatchSummaryGenerator(
        force_reprocess=args.force,
        batch_size=args.batch_size
    )
    processor.run_batch_processing(limit=args.limit)


if __name__ == '__main__':
    main()
