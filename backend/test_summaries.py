#!/usr/bin/env python3
"""
Test script to evaluate GLiNER-generated tender summaries from the database.
This script queries tenders with AI summaries and provides quality analysis.
"""

import sys
import os
from datetime import datetime
from typing import Optional

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.database import SessionLocal
from app.models.tender import Tender
from sqlalchemy import select

def test_tender_summaries():
    """Query and test tender summaries from database."""

    db = SessionLocal()
    try:
        # Query tenders with AI summaries
        query = select(Tender).where(
            Tender.ai_processed == True,
            Tender.ai_summary != None
        ).limit(20)

        results = db.execute(query).scalars().all()

        if not results:
            print("❌ No processed tenders with summaries found in database.")
            print("\nTrying to find any tenders at all...")
            all_tenders = db.execute(select(Tender).limit(5)).scalars().all()
            if all_tenders:
                print(f"✓ Found {len(all_tenders)} tenders in database")
                for tender in all_tenders:
                    print(f"\n  - Title: {tender.title}")
                    print(f"    AI Processed: {tender.ai_processed}")
                    print(f"    Has Summary: {tender.ai_summary is not None}")
                    if tender.ai_summary:
                        print(f"    Summary: {tender.ai_summary[:100]}...")
            else:
                print("❌ No tenders found at all")
            return

        print(f"✅ Found {len(results)} processed tenders with summaries\n")
        print("=" * 100)

        # Analyze each tender's summary
        summary_stats = {
            'total': len(results),
            'total_words': 0,
            'avg_words': 0,
            'summaries_analyzed': 0,
            'very_short': 0,  # < 20 words
            'short': 0,  # 20-50 words
            'medium': 0,  # 50-100 words
            'long': 0,  # > 100 words
        }

        for idx, tender in enumerate(results, 1):
            print(f"\n📄 TENDER {idx}/{len(results)}")
            print(f"{'─' * 100}")
            print(f"Title: {tender.title}")
            print(f"ID: {tender.id}")
            print(f"Status: {tender.status}")
            print(f"Published: {tender.published_date}")
            print(f"Deadline: {tender.deadline}")
            print(f"Processed At: {tender.ai_processed_at}")
            print(f"Category: {tender.category}")
            print(f"Region: {tender.region}")

            if tender.ai_summary:
                words = len(tender.ai_summary.split())
                summary_stats['total_words'] += words
                summary_stats['summaries_analyzed'] += 1

                # Categorize by length
                if words < 20:
                    summary_stats['very_short'] += 1
                    length_category = "⚠️  VERY SHORT"
                elif words < 50:
                    summary_stats['short'] += 1
                    length_category = "📝 SHORT"
                elif words < 100:
                    summary_stats['medium'] += 1
                    length_category = "✓ MEDIUM"
                else:
                    summary_stats['long'] += 1
                    length_category = "📖 LONG"

                print(f"\n📋 SUMMARY ({words} words) - {length_category}")
                print(f"{'─' * 100}")
                # Print full summary
                print(tender.ai_summary)

                # Quality metrics
                print(f"\n📊 QUALITY METRICS:")
                print(f"  • Word Count: {words}")
                print(f"  • Character Count: {len(tender.ai_summary)}")
                print(f"  • Sentences: {tender.ai_summary.count('.')}")
                print(f"  • Has entities extracted: {tender.extracted_entities is not None}")
                if tender.extracted_entities:
                    print(f"  • Extracted Entities: {list(tender.extracted_entities.keys())}")
                print(f"  • Raw text available: {tender.raw_text is not None}")
                if tender.raw_text:
                    print(f"  • Raw text word count: {len(tender.raw_text.split())}")
            else:
                print("❌ No summary available")

        # Print summary statistics
        print(f"\n\n{'=' * 100}")
        print("📊 SUMMARY STATISTICS")
        print(f"{'=' * 100}")

        if summary_stats['summaries_analyzed'] > 0:
            summary_stats['avg_words'] = summary_stats['total_words'] // summary_stats['summaries_analyzed']

        print(f"Total Tenders Analyzed: {summary_stats['total']}")
        print(f"Tenders with Summaries: {summary_stats['summaries_analyzed']}")
        print(f"Total Words Generated: {summary_stats['total_words']}")
        print(f"Average Words per Summary: {summary_stats['avg_words']}")

        print(f"\n📏 Summary Length Distribution:")
        print(f"  • Very Short (< 20 words): {summary_stats['very_short']} ({summary_stats['very_short']/len(results)*100:.1f}%)")
        print(f"  • Short (20-50 words): {summary_stats['short']} ({summary_stats['short']/len(results)*100:.1f}%)")
        print(f"  • Medium (50-100 words): {summary_stats['medium']} ({summary_stats['medium']/len(results)*100:.1f}%)")
        print(f"  • Long (> 100 words): {summary_stats['long']} ({summary_stats['long']/len(results)*100:.1f}%)")

        # Quality assessment
        print(f"\n🎯 QUALITY ASSESSMENT:")
        if summary_stats['very_short'] > len(results) * 0.3:
            print(f"  ⚠️  Many summaries are very short - GLiNER may need tuning")
        elif summary_stats['avg_words'] < 40:
            print(f"  ⚠️  Average summary length is short - consider GLiNER settings")
        else:
            print(f"  ✅ Summary length appears reasonable")

        print(f"\n" + "=" * 100)

    except Exception as e:
        print(f"❌ Error querying database: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    print("🔍 TENDER SUMMARY QUALITY TEST")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 100)
    test_tender_summaries()
    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
