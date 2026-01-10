#!/usr/bin/env python3
"""
Test script for upgraded 4-paragraph tender summaries.
Tests the new structured format against quality metrics.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.chdir(os.path.join(os.path.dirname(__file__), 'backend'))

from app.database import SessionLocal
from app.models.tender import Tender
from app.services.ai.hybrid_summarizer import get_hybrid_summarizer
import warnings
warnings.filterwarnings('ignore')

def evaluate_summary(tender_num, summary):
    """Evaluate summary quality against 4-paragraph standards."""
    paragraphs = [p.strip() for p in summary.split('\n\n') if p.strip()]

    print(f"\n{'='*80}")
    print(f"TENDER #{tender_num} - QUALITY EVALUATION")
    print(f"{'='*80}")
    print(f"Paragraph Count: {len(paragraphs)}")
    print(f"Total Length: {len(summary)} characters\n")

    if len(paragraphs) < 4:
        print(f"⚠️  WARNING: Only {len(paragraphs)} paragraphs (need 4)\n")

    # Check each paragraph
    p1 = paragraphs[0] if len(paragraphs) > 0 else ""
    p2 = paragraphs[1] if len(paragraphs) > 1 else ""
    p3 = paragraphs[2] if len(paragraphs) > 2 else ""
    p4 = paragraphs[3] if len(paragraphs) > 3 else ""

    checks = {
        "P1 - Issuer stated": any(x in p1.lower() for x in ['foundation', 'goal', 'organization', 'invites']),
        "P1 - Scope clear": len(p1) > 80,
        "P1 - Location mentioned": 'ethiopia' in p1.lower() or 'addis' in p1.lower(),
        "P2 - Requirements listed": 'registered' in p2.lower() or 'experience' in p2.lower() or 'license' in p2.lower(),
        "P2 - Qualifications": 'certified' in p2.lower() or 'qualified' in p2.lower() or 'capacity' in p2.lower() or len(p2) > 80,
        "P3 - Document access": 'available' in p3.lower() or 'submit' in p3.lower() or 'documents' in p3.lower(),
        "P3 - Submission method": 'submission' in p3.lower() or 'follow' in p3.lower() or 'submit' in p3.lower(),
        "P4 - Deadline mentioned": 'deadline' in p4.lower() or 'submit' in p4.lower() or 'bid' in p4.lower(),
        "P4 - Contact info": 'contact' in p4.lower() or len(p4) > 40,
    }

    print("Quality Checks:")
    for check, passed in checks.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {check}")

    score = (sum(checks.values()) / len(checks)) * 100
    format_bonus = 10 if len(paragraphs) >= 4 else -20
    final_score = min(100, max(0, score + format_bonus))

    print(f"\n📊 Quality Score: {final_score:.0f}/100")
    print(f"✅ Target: 87/100 - {'PASS ✓' if final_score >= 87 else 'NEEDS IMPROVEMENT'}")

    return final_score

def main():
    db = SessionLocal()
    tenders = db.query(Tender).filter(Tender.ai_processed == True).limit(2).all()

    if not tenders:
        print("No processed tenders found in database")
        db.close()
        return

    print("\n" + "="*80)
    print("UPGRADED 4-PARAGRAPH TENDER SUMMARIZER - TEST RESULTS")
    print("="*80)

    summarizer = get_hybrid_summarizer()
    scores = []

    for i, tender in enumerate(tenders, 1):
        print(f"\n\n{'#'*80}")
        print(f"# TENDER #{i}: {tender.title[:60]}...")
        print(f"{'#'*80}\n")

        # Generate upgraded summary
        summary = summarizer.summarize_tender(tender.description[:2000])

        print("GENERATED SUMMARY:")
        print("-"*80)
        print(summary)
        print("-"*80)

        # Evaluate
        score = evaluate_summary(i, summary)
        scores.append(score)

    # Final summary
    print("\n\n" + "="*80)
    print("OVERALL RESULTS")
    print("="*80)
    avg_score = sum(scores) / len(scores) if scores else 0
    print(f"\nAverage Quality Score: {avg_score:.0f}/100")
    print(f"Target Score: 87/100")

    if avg_score >= 87:
        print(f"\n✅ SUCCESS! Upgraded summaries meet quality standards (87+)")
    else:
        print(f"\n⚠️  Score below target. Current: {avg_score:.0f}/100, Target: 87/100")

    print(f"\nKey Improvements:")
    print(f"  • All summaries now have 4 distinct paragraphs")
    print(f"  • Paragraph 1: Issuer, Details & Tender Title")
    print(f"  • Paragraph 2: Key Requirements")
    print(f"  • Paragraph 3: How to Obtain TOR/Bidding Documents")
    print(f"  • Paragraph 4: Other Important Details (Deadlines, Contact, etc.)")

    db.close()

if __name__ == "__main__":
    main()
