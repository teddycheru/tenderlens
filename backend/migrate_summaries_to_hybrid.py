#!/usr/bin/env python3
"""
Migration script to upgrade existing tender summaries to use Hybrid (FLAN-T5 + GLiNER) approach.

This script:
1. Finds all tenders with existing summaries
2. Invalidates their cache
3. Reprocesses them with the new Hybrid approach
4. Tracks migration progress and results

Usage:
    python migrate_summaries_to_hybrid.py [--limit N] [--force]

    --limit N: Only migrate N tenders (default: all)
    --force: Force reprocess even if already processed with hybrid approach
"""

import asyncio
import sys
import time
from datetime import datetime
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.tender import Tender
from app.services.ai.ai_service import ai_service
from app.services.cache import cache_service


class MigrationStats:
    def __init__(self):
        self.total = 0
        self.processed = 0
        self.succeeded = 0
        self.failed = 0
        self.skipped = 0
        self.start_time = None
        self.failed_ids = []

    def start(self):
        self.start_time = datetime.now()

    def get_elapsed(self):
        if self.start_time:
            return (datetime.now() - self.start_time).total_seconds()
        return 0

    def get_rate(self):
        elapsed = self.get_elapsed()
        if elapsed > 0:
            return self.processed / elapsed
        return 0

    def print_summary(self):
        elapsed = self.get_elapsed()
        rate = self.get_rate()
        print("\n" + "="*60)
        print("MIGRATION SUMMARY")
        print("="*60)
        print(f"Total tenders found:    {self.total}")
        print(f"Successfully migrated:  {self.succeeded}")
        print(f"Failed:                 {self.failed}")
        print(f"Skipped:                {self.skipped}")
        print(f"Time elapsed:           {elapsed:.1f}s")
        print(f"Processing rate:        {rate:.2f} tenders/sec")
        print("="*60)

        if self.failed_ids:
            print(f"\nFailed tender IDs ({len(self.failed_ids)}):")
            for tid in self.failed_ids[:10]:
                print(f"  - {tid}")
            if len(self.failed_ids) > 10:
                print(f"  ... and {len(self.failed_ids) - 10} more")


async def migrate_tender(db: Session, tender_id: str, force: bool = False) -> dict:
    """
    Migrate a single tender to hybrid approach.

    Args:
        db: Database session
        tender_id: Tender UUID
        force: Force reprocess even if already processed

    Returns:
        Migration result dict with status and details
    """
    try:
        tender = db.query(Tender).filter(Tender.id == tender_id).first()
        if not tender:
            return {"tender_id": tender_id, "status": "skipped", "reason": "Tender not found"}

        if not tender.ai_summary and not force:
            return {"tender_id": tender_id, "status": "skipped", "reason": "No existing summary"}

        # Invalidate cache to force reprocessing
        cache_service.invalidate_tender_cache(tender_id)

        # Reprocess with new hybrid approach
        result = await ai_service.process_tender_document(
            db,
            tender_id,
            force_reprocess=True
        )

        return {
            "tender_id": tender_id,
            "status": "success",
            "summary_length": len(result.get("summary", "")),
            "has_entities": bool(result.get("entities")),
            "processing_time_ms": result.get("processing_time_ms", 0)
        }

    except Exception as e:
        return {
            "tender_id": tender_id,
            "status": "failed",
            "error": str(e)
        }


async def migrate_all_tenders(limit: int = None, force: bool = False):
    """
    Migrate all tenders to hybrid approach.

    Args:
        limit: Maximum number of tenders to process (None = all)
        force: Force reprocess all tenders
    """
    db = SessionLocal()
    stats = MigrationStats()
    stats.start()

    try:
        # Get all tenders that have summaries (or all if force=True)
        if force:
            query = db.query(Tender)
        else:
            query = db.query(Tender).filter(Tender.ai_summary.isnot(None))

        if limit:
            query = query.limit(limit)

        tenders = query.all()
        stats.total = len(tenders)

        print(f"\n🚀 Starting migration to Hybrid (FLAN-T5 + GLiNER) approach")
        print(f"Tenders to migrate:     {stats.total}")
        print(f"Force reprocess:        {force}")
        print("="*60)

        # Process in batches to avoid overwhelming system
        batch_size = 5
        for i in range(0, len(tenders), batch_size):
            batch = tenders[i:i+batch_size]

            # Process batch concurrently
            tasks = [migrate_tender(db, str(t.id), force) for t in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            for result in results:
                if isinstance(result, Exception):
                    stats.failed += 1
                    stats.failed_ids.append("unknown")
                    print(f"❌ Error: {result}")
                else:
                    stats.processed += 1
                    tender_id = result["tender_id"]
                    status = result["status"]

                    if status == "success":
                        stats.succeeded += 1
                        summary_len = result.get("summary_length", 0)
                        time_ms = result.get("processing_time_ms", 0)
                        print(f"✅ {i + results.index(result) + 1}/{stats.total}: {tender_id[:8]}... ({summary_len} chars, {time_ms}ms)")
                    elif status == "skipped":
                        stats.skipped += 1
                        reason = result.get("reason", "unknown")
                        print(f"⏭️  {i + results.index(result) + 1}/{stats.total}: {tender_id[:8]}... (skipped: {reason})")
                    else:  # failed
                        stats.failed += 1
                        stats.failed_ids.append(tender_id)
                        error = result.get("error", "unknown")
                        print(f"❌ {i + results.index(result) + 1}/{stats.total}: {tender_id[:8]}... (error: {error})")

            # Commit after each batch
            db.commit()

        # Print final summary
        stats.print_summary()

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        raise
    finally:
        db.close()


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Migrate tender summaries to Hybrid approach")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of tenders to migrate")
    parser.add_argument("--force", action="store_true", help="Force reprocess all tenders")

    args = parser.parse_args()

    print("🔄 Hybrid Summarization Migration")
    print("Upgrading tender summaries from single models to Hybrid (FLAN-T5 + GLiNER)")

    try:
        asyncio.run(migrate_all_tenders(limit=args.limit, force=args.force))
        print("\n✅ Migration completed successfully!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
