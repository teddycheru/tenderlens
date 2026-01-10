#!/usr/bin/env python3
"""
Batch process all unprocessed tenders with improved AI summaries.
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.tender import Tender
from app.services.ai.ai_service import ai_service


async def batch_process_tenders():
    """Process all unprocessed tenders with improved hybrid summarizer."""
    db = SessionLocal()
    try:
        # Get all unprocessed tenders
        unprocessed = db.query(Tender).filter(
            Tender.ai_processed == False
        ).all()

        total = len(unprocessed)
        print(f"\nStarting batch processing of {total} unprocessed tenders...")
        print("=" * 70)

        if total == 0:
            print("No unprocessed tenders found. All tenders are already processed!")
            return

        processed_count = 0
        failed_count = 0
        errors = []

        for idx, tender in enumerate(unprocessed, 1):
            tender_id = str(tender.id)
            progress = f"[{idx}/{total}]"

            try:
                print(f"{progress} Processing: {tender.title[:60]}...", end=" ", flush=True)

                # Process tender with AI
                result = await ai_service.process_tender_document(
                    db=db,
                    tender_id=tender_id,
                    force_reprocess=False
                )

                # Check if it was successful
                if tender.ai_summary and tender.ai_processed:
                    summary_preview = tender.ai_summary[:60].replace('\n', ' ')
                    print(f"✓ OK ({len(tender.ai_summary)} chars)")
                    print(f"     Summary: {summary_preview}...")
                    processed_count += 1
                else:
                    print(f"✗ FAILED - No summary generated")
                    failed_count += 1
                    errors.append((tender_id, "No summary generated"))

            except Exception as e:
                print(f"✗ ERROR: {str(e)[:50]}")
                failed_count += 1
                errors.append((tender_id, str(e)))

        print("\n" + "=" * 70)
        print(f"BATCH PROCESSING COMPLETE")
        print(f"  Total processed: {total}")
        print(f"  ✓ Successful: {processed_count}")
        print(f"  ✗ Failed: {failed_count}")

        if errors:
            print(f"\nFailed tenders:")
            for tender_id, error in errors[:5]:
                print(f"  - {tender_id}: {error[:50]}")
            if len(errors) > 5:
                print(f"  ... and {len(errors) - 5} more")

    finally:
        db.close()


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("TENDER BATCH AI PROCESSING")
    print("=" * 70)

    asyncio.run(batch_process_tenders())
