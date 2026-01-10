#!/usr/bin/env python3
"""
Direct synchronous batch processing of all tenders.
Processes tenders directly without async queue - ensures reliable completion.
"""

import sys
import os
import asyncio
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.tender import Tender
from app.services.ai.ai_service import ai_service


async def process_all_tenders():
    """Synchronously process all unprocessed tenders."""
    db = SessionLocal()
    try:
        # Get all unprocessed tenders
        unprocessed = db.query(Tender).filter(
            Tender.ai_processed == False
        ).all()

        total = len(unprocessed)
        print(f"\n{'='*80}")
        print(f"DIRECT SYNCHRONOUS TENDER PROCESSING")
        print(f"{'='*80}")
        print(f"Total unprocessed tenders: {total}\n")

        if total == 0:
            print("✓ All tenders already processed!")
            return

        successful = 0
        failed = 0
        failed_list = []

        for idx, tender in enumerate(unprocessed, 1):
            tender_id = str(tender.id)
            title = tender.title[:50]
            progress = f"[{idx:2d}/{total}]"

            try:
                print(f"{progress} Processing: {title}...", end=" ", flush=True)
                start = time.time()

                # Process the tender
                result = await ai_service.process_tender_document(
                    db=db,
                    tender_id=tender_id,
                    force_reprocess=False
                )

                elapsed = time.time() - start

                # Verify it was actually processed
                db.refresh(tender)
                if tender.ai_processed and tender.ai_summary:
                    summary_len = len(tender.ai_summary)
                    has_overview = "OVERVIEW" in tender.ai_summary
                    print(f"✓ OK ({summary_len} chars, {elapsed:.1f}s) [HAS OVERVIEW: {has_overview}]")
                    successful += 1
                else:
                    print(f"✗ FAILED - No summary stored")
                    failed += 1
                    failed_list.append((tender_id, "No summary in DB"))

            except Exception as e:
                print(f"✗ ERROR: {str(e)[:60]}")
                failed += 1
                failed_list.append((tender_id, str(e)[:60]))

        # Final summary
        print(f"\n{'='*80}")
        print(f"PROCESSING COMPLETE")
        print(f"{'='*80}")
        print(f"Total processed:    {total}")
        print(f"✓ Successful:       {successful} ({successful*100//total}%)")
        print(f"✗ Failed:           {failed} ({failed*100//total}%)")

        if failed > 0:
            print(f"\nFailed tenders:")
            for tender_id, error in failed_list[:10]:
                print(f"  • {tender_id}: {error}")
            if len(failed_list) > 10:
                print(f"  ... and {len(failed_list) - 10} more")

        # Final database check
        print(f"\n{'='*80}")
        print(f"FINAL DATABASE STATUS")
        print(f"{'='*80}")
        total_count = db.query(Tender).count()
        processed_count = db.query(Tender).filter(Tender.ai_processed == True).count()
        print(f"Total tenders in DB:   {total_count}")
        print(f"Processed:             {processed_count}")
        print(f"Still unprocessed:     {total_count - processed_count}")

    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(process_all_tenders())
