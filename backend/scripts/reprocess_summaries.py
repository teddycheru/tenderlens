#!/usr/bin/env python3
"""
Re-process existing tender summaries with improved GLiNER settings.

This script:
1. Queries tenders with existing summaries
2. Re-generates summaries using improved GLiNER configuration
3. Updates database with new summaries
4. Provides quality metrics before/after

Usage:
    python reprocess_summaries.py [--limit 50] [--dry-run] [--force]
"""

import sys
import os
import argparse
from datetime import datetime
from typing import List, Dict, Optional

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.database import SessionLocal
from app.models.tender import Tender
from app.services.ai.gliner_service import get_gliner_service
from sqlalchemy import select, func
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_summary_quality_metrics(summary: str) -> Dict:
    """Calculate quality metrics for a summary."""
    if not summary:
        return {
            "word_count": 0,
            "char_count": 0,
            "sentence_count": 0,
            "has_structure": False,
        }

    words = summary.split()
    sentences = summary.count('.') + summary.count('!') + summary.count('?')

    return {
        "word_count": len(words),
        "char_count": len(summary),
        "sentence_count": sentences,
        "has_structure": len(words) > 30 and sentences > 1,
    }


def reprocess_summaries(
    db,
    gliner_service,
    limit: int = 50,
    dry_run: bool = False,
    force: bool = False
):
    """
    Re-process tender summaries with improved GLiNER.

    Args:
        db: Database session
        gliner_service: GLiNER service instance
        limit: Maximum number of tenders to process
        dry_run: If True, don't save changes
        force: If True, reprocess even recently processed tenders

    Returns:
        Dictionary with processing statistics
    """
    # Query tenders with existing summaries
    query = select(Tender).where(Tender.ai_processed == True)

    if not force:
        # Exclude recently processed (within last 24 hours)
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(hours=24)
        query = query.where(Tender.ai_processed_at < cutoff)

    query = query.limit(limit)

    tenders = db.execute(query).scalars().all()

    stats = {
        "total_processed": 0,
        "improved": 0,
        "unchanged": 0,
        "failed": 0,
        "avg_words_before": 0,
        "avg_words_after": 0,
        "improvements": []
    }

    total_words_before = 0
    total_words_after = 0

    if not tenders:
        logger.warning("No tenders found to reprocess")
        return stats

    logger.info(f"Found {len(tenders)} tenders to reprocess")

    for idx, tender in enumerate(tenders, 1):
        try:
            logger.info(f"\n[{idx}/{len(tenders)}] Processing: {tender.title[:50]}...")

            # Get old summary metrics
            old_summary = tender.ai_summary or ""
            old_metrics = get_summary_quality_metrics(old_summary)

            # Re-generate summary
            text_content = tender.description or ""
            if not text_content:
                logger.warning(f"  ⚠️  No text content, skipping")
                stats["failed"] += 1
                continue

            new_summary = gliner_service.summarize_tender(text_content, title=tender.title)
            new_metrics = get_summary_quality_metrics(new_summary)

            # Compare
            word_improvement = new_metrics["word_count"] - old_metrics["word_count"]
            structure_improved = (
                not old_metrics["has_structure"] and new_metrics["has_structure"]
            )

            is_improved = (
                word_improvement > 20 or  # Significant word increase
                structure_improved or  # Now has proper sentence structure
                (new_metrics["sentence_count"] > old_metrics["sentence_count"] and
                 new_metrics["word_count"] >= old_metrics["word_count"] * 0.8)  # More sentences
            )

            if is_improved:
                stats["improved"] += 1
                logger.info(f"  ✅ IMPROVED: {old_metrics['word_count']} → {new_metrics['word_count']} words")

                if not dry_run:
                    tender.ai_summary = new_summary
                    tender.ai_processed_at = datetime.utcnow()

                stats["improvements"].append({
                    "title": tender.title[:50],
                    "old_words": old_metrics["word_count"],
                    "new_words": new_metrics["word_count"],
                    "old_sentences": old_metrics["sentence_count"],
                    "new_sentences": new_metrics["sentence_count"],
                })

            else:
                stats["unchanged"] += 1
                logger.info(f"  ℹ️  No improvement needed")
                if not dry_run:
                    # Still update timestamp to mark as re-checked
                    tender.ai_processed_at = datetime.utcnow()

            stats["total_processed"] += 1
            total_words_before += old_metrics["word_count"]
            total_words_after += new_metrics["word_count"]

        except Exception as e:
            logger.error(f"  ❌ ERROR: {str(e)}")
            stats["failed"] += 1
            continue

    # Commit changes if not dry run
    if not dry_run and (stats["improved"] > 0 or stats["unchanged"] > 0):
        try:
            db.commit()
            logger.info(f"\n✅ Successfully saved {stats['improved']} improvements to database")
        except Exception as e:
            logger.error(f"Database commit failed: {e}")
            db.rollback()
            stats["failed"] += stats["improved"]
            stats["improved"] = 0

    # Calculate averages
    if stats["total_processed"] > 0:
        stats["avg_words_before"] = total_words_before // stats["total_processed"]
        stats["avg_words_after"] = total_words_after // stats["total_processed"]

    return stats


def print_report(stats: Dict, dry_run: bool = False):
    """Print processing report."""
    print("\n" + "=" * 100)
    print("📊 SUMMARY REPROCESSING REPORT")
    print("=" * 100)

    if dry_run:
        print("⚠️  DRY RUN - No changes were saved to database")

    print(f"\n📈 Results:")
    print(f"  • Tenders Processed: {stats['total_processed']}")
    print(f"  • Improved Summaries: {stats['improved']}")
    print(f"  • Unchanged: {stats['unchanged']}")
    print(f"  • Failed: {stats['failed']}")

    if stats['total_processed'] > 0:
        print(f"\n📏 Word Count:")
        print(f"  • Average Before: {stats['avg_words_before']} words")
        print(f"  • Average After: {stats['avg_words_after']} words")
        print(f"  • Average Change: +{stats['avg_words_after'] - stats['avg_words_before']} words")

    if stats["improvements"]:
        print(f"\n✅ Sample Improvements:")
        for i, improvement in enumerate(stats["improvements"][:5], 1):
            print(f"\n  {i}. {improvement['title']}")
            print(f"     Words: {improvement['old_words']} → {improvement['new_words']} "
                  f"({improvement['new_words'] - improvement['old_words']:+d})")
            print(f"     Sentences: {improvement['old_sentences']} → {improvement['new_sentences']}")

    print("\n" + "=" * 100)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Re-process tender summaries with improved GLiNER configuration"
    )
    parser.add_argument("--limit", type=int, default=50,
                        help="Maximum tenders to reprocess (default: 50)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Don't save changes to database")
    parser.add_argument("--force", action="store_true",
                        help="Reprocess even recently processed tenders")

    args = parser.parse_args()

    print(f"🔄 TENDER SUMMARY REPROCESSING")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Limit: {args.limit} tenders")
    print(f"Dry Run: {args.dry_run}")
    print("=" * 100)

    db = SessionLocal()
    try:
        # Get GLiNER service
        gliner_service = get_gliner_service()

        if not gliner_service.is_available():
            print("❌ GLiNER service not available")
            return 1

        # Reprocess summaries
        stats = reprocess_summaries(
            db,
            gliner_service,
            limit=args.limit,
            dry_run=args.dry_run,
            force=args.force
        )

        # Print report
        print_report(stats, dry_run=args.dry_run)

        print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return 0

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
