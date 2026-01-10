#!/usr/bin/env python3
"""
Test script to demonstrate improved summary generation.

Compares old vs new summary generation methods on sample tenders.
"""

import sys
import os
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.database import SessionLocal
from app.models.tender import Tender
from app.services.ai.gliner_service import get_gliner_service
from sqlalchemy import select


def test_improved_summaries():
    """Test and compare improved summary generation."""

    db = SessionLocal()
    try:
        # Get GLiNER service
        gliner_service = get_gliner_service()

        if not gliner_service.is_available():
            print("❌ GLiNER service not available")
            return

        # Get sample tenders
        query = select(Tender).where(
            Tender.ai_processed == True,
            Tender.ai_summary != None
        ).limit(5)

        tenders = db.execute(query).scalars().all()

        if not tenders:
            print("❌ No processed tenders found")
            return

        print(f"🧪 TESTING IMPROVED SUMMARY GENERATION")
        print(f"Comparing {len(tenders)} tenders")
        print("=" * 120)

        for idx, tender in enumerate(tenders, 1):
            print(f"\n{'='*120}")
            print(f"📄 TENDER {idx}/{len(tenders)}")
            print(f"{'='*120}")
            print(f"Title: {tender.title}")
            print(f"Category: {tender.category}")

            # Get original summary
            original_summary = tender.ai_summary or "No summary"

            # Generate new summary
            text_content = tender.description or ""
            if not text_content:
                print("⚠️  No text content available")
                continue

            try:
                new_summary = gliner_service.summarize_tender(
                    text_content,
                    title=tender.title
                )
            except Exception as e:
                print(f"❌ Error generating new summary: {e}")
                continue

            # Analyze both
            original_words = len(original_summary.split())
            new_words = len(new_summary.split())
            original_sentences = original_summary.count('.') + original_summary.count('!') + original_summary.count('?')
            new_sentences = new_summary.count('.') + new_summary.count('!') + new_summary.count('?')

            print(f"\n📊 COMPARISON:")
            print(f"  Original: {original_words} words, {original_sentences} sentences")
            print(f"  New:      {new_words} words, {new_sentences} sentences")
            print(f"  Improvement: {new_words - original_words:+d} words, {new_sentences - original_sentences:+d} sentences")

            print(f"\n📝 ORIGINAL SUMMARY:")
            print(f"{'─' * 120}")
            print(original_summary[:500])
            if len(original_summary) > 500:
                print(f"... ({len(original_summary) - 500} more characters)")

            print(f"\n✨ NEW SUMMARY:")
            print(f"{'─' * 120}")
            print(new_summary[:500])
            if len(new_summary) > 500:
                print(f"... ({len(new_summary) - 500} more characters)")

            # Quality assessment
            original_has_structure = original_sentences > 1
            new_has_structure = new_sentences > 1

            print(f"\n🎯 QUALITY ASSESSMENT:")
            print(f"  Original Has Structure: {'✅ Yes' if original_has_structure else '❌ No'}")
            print(f"  New Has Structure: {'✅ Yes' if new_has_structure else '❌ No'}")

            if new_words > original_words * 1.2:
                print(f"  ✅ Better coverage: includes more useful information")
            elif new_words < original_words * 0.8:
                print(f"  ⚠️  Shorter: but may be more concise")
            else:
                print(f"  ℹ️  Similar length")

            if new_has_structure and not original_has_structure:
                print(f"  ✅ Improved readability: now has proper sentence breaks")

        print(f"\n{'='*120}")
        print(f"✅ Testing completed")
        print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()


if __name__ == "__main__":
    print("🔄 IMPROVED SUMMARY GENERATION TEST")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 120)
    test_improved_summaries()
