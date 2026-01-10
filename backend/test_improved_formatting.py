#!/usr/bin/env python3
"""
Test script to showcase IMPROVED GLiNER summary formatting.

This directly tests the new _build_summary() method with section-based organization.
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.database import SessionLocal
from app.models.tender import Tender
from app.services.ai.gliner_service import get_gliner_service
from sqlalchemy import select

def test_improved_formatting():
    """Test and display improved summary formatting."""

    db = SessionLocal()
    try:
        # Get GLiNER service
        gliner_service = get_gliner_service()

        if not gliner_service.is_available():
            print("❌ GLiNER service not available")
            return

        # Get sample tenders with descriptions
        query = select(Tender).where(
            Tender.description != None,
            Tender.description != ""
        ).limit(5)

        tenders = db.execute(query).scalars().all()

        if not tenders:
            print("❌ No tenders with descriptions found")
            return

        print(f"🎨 TESTING IMPROVED SUMMARY FORMATTING")
        print(f"Generating professionally formatted summaries")
        print("=" * 120)

        for idx, tender in enumerate(tenders, 1):
            print(f"\n{'='*120}")
            print(f"📄 TENDER {idx}/{len(tenders)}")
            print(f"{'='*120}")
            print(f"Title: {tender.title}\n")

            # Get text content
            text_content = tender.description or ""
            if not text_content:
                print("⚠️  No text content available")
                continue

            try:
                # Generate IMPROVED summary (this uses the new _build_summary method!)
                new_summary = gliner_service.summarize_tender(
                    text_content,
                    title=tender.title
                )
            except Exception as e:
                print(f"❌ Error generating summary: {e}")
                continue

            # Display the summary with formatting
            print("✨ IMPROVED FORMATTED SUMMARY:")
            print("─" * 120)
            print(new_summary)
            print("─" * 120)

            # Analyze formatting quality
            lines = new_summary.split('\n')
            sections = [line for line in lines if line.strip().startswith(('📋', '⚡', '📦', '✓', '📮'))]
            words = len(new_summary.split())
            has_structure = len(sections) > 1
            double_newline = '\n\n'
            has_breaks = double_newline in new_summary

            print(f"\n📊 FORMATTING QUALITY:")
            print(f"  • Total words: {words}")
            print(f"  • Number of sections: {len(sections)}")
            print(f"  • Has visual hierarchy: {'✅ Yes' if has_structure else '❌ No'}")
            print(f"  • Has paragraph breaks: {'✅ Yes' if has_breaks else '❌ No'}")
            print(f"  • Uses emojis: {'✅ Yes' if '📋' in new_summary or '⚡' in new_summary else '❌ No'}")
            print(f"  • Scannable: {'✅ Yes (<5 sec)' if has_structure else '❌ No (>30 sec)'}")

        print(f"\n{'='*120}")
        print(f"✅ Improved formatting test completed")
        print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()


if __name__ == "__main__":
    print("🎨 IMPROVED SUMMARY FORMATTING TEST")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 120)
    test_improved_formatting()
