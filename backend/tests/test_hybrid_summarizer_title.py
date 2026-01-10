#!/usr/bin/env python3
"""
Test the improved hybrid summarizer with title extraction.
"""

import random
from app.database import SessionLocal
from app.models.tender import Tender
from app.services.ai.hybrid_summarizer import hybrid_summarizer

db = SessionLocal()

# Get 5 random tenders
tenders = db.query(Tender).filter(Tender.description.isnot(None)).all()
selected = random.sample(tenders, min(5, len(tenders)))

print(f"\n{'='*90}")
print("TESTING IMPROVED HYBRID SUMMARIZER (with Title + Description)")
print(f"{'='*90}\n")

for i, tender in enumerate(selected, 1):
    print(f"{'─'*90}")
    print(f"TENDER {i}: {tender.title[:70]}")
    print(f"{'─'*90}")
    
    # Generate summary using improved method (now with title)
    try:
        summary = hybrid_summarizer.summarize_tender(
            text=tender.description,
            title=tender.title,  # NEW: Pass title to summarizer
            max_words=200
        )
        
        print(f"\n📋 SUMMARY:")
        print(summary)
        print(f"\n✓ Summary Length: {len(summary)} chars")
        
    except Exception as e:
        print(f"\n❌ Error generating summary: {e}")
    
    print()

db.close()

