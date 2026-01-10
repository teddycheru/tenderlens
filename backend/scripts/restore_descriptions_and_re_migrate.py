#!/usr/bin/env python3
"""
Restore original tender descriptions with proper capitalization and structure,
then re-migrate summaries using the improved hybrid summarizer.

This script:
1. Loads the CSV with original HTML descriptions
2. Cleans HTML while preserving capitalization and structure
3. Updates database descriptions
4. Re-runs summary generation
"""

import csv
import re
import sys
from html import unescape
from pathlib import Path
from app.database import SessionLocal
from app.models.tender import Tender

def clean_html_preserve_structure(html_text: str) -> str:
    """
    Clean HTML while preserving:
    - Original capitalization
    - Paragraph structure
    - List structure
    - All meaningful content
    """
    if not html_text:
        return ""
    
    # Decode HTML entities
    text = unescape(html_text)
    
    # Replace HTML block elements with newlines
    text = re.sub(r'</p>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</li>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</div>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</ul>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</ol>', '\n', text, flags=re.IGNORECASE)
    
    # Replace list items with bullet points
    text = re.sub(r'<li[^>]*>', '• ', text, flags=re.IGNORECASE)
    
    # Remove all remaining HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Clean up whitespace while preserving paragraphs
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        line = re.sub(r'\s+', ' ', line)  # Multiple spaces to single
        if line:  # Only keep non-empty lines
            cleaned_lines.append(line)
    
    text = '\n'.join(cleaned_lines)
    
    # Remove excessive blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()


def restore_descriptions_from_csv(csv_path: str, limit: int = None) -> dict:
    """
    Load descriptions from CSV and clean them.
    
    Args:
        csv_path: Path to CSV file with original descriptions
        limit: Max number of tenders to process (None = all)
    
    Returns:
        Dict mapping tender title -> cleaned description
    """
    descriptions = {}
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if limit and i >= limit:
                break
            
            title = row.get('Title', '').strip()
            desc_html = row.get('Description', '')
            
            if title and desc_html:
                desc_clean = clean_html_preserve_structure(desc_html)
                descriptions[title] = desc_clean
    
    return descriptions


def main():
    """Main restoration and re-migration process."""

    # Try multiple paths
    csv_file = None
    for path in [
        '2merkato_tenders_all-columns.csv',
        '/app/2merkato_tenders_all-columns.csv',
    ]:
        if Path(path).exists():
            csv_file = path
            break

    if not csv_file:
        print(f"❌ CSV file not found in any of:")
        print(f"   - 2merkato_tenders_all-columns.csv")
        print(f"   - /app/2merkato_tenders_all-columns.csv")
        sys.exit(1)
    
    print(f"\n{'='*80}")
    print("RESTORING TENDER DESCRIPTIONS FROM ORIGINAL CSV")
    print(f"{'='*80}\n")
    
    # Load cleaned descriptions from CSV
    print("1️⃣ Loading descriptions from CSV...")
    descriptions = restore_descriptions_from_csv(csv_file)
    print(f"   ✓ Loaded {len(descriptions)} descriptions from CSV\n")
    
    # Connect to database
    db = SessionLocal()
    
    try:
        print("2️⃣ Updating database descriptions...")
        
        # Find tenders by title and update their descriptions
        updated_count = 0
        not_found_count = 0
        
        for csv_title, clean_desc in descriptions.items():
            # Search for tender by title (partial match, case-insensitive)
            tender = db.query(Tender).filter(
                Tender.title.ilike(f"%{csv_title[:50]}%")
            ).first()
            
            if tender:
                tender.description = clean_desc
                updated_count += 1
                
                if updated_count % 10 == 0:
                    print(f"   Updated {updated_count} tenders...")
            else:
                not_found_count += 1
                if not_found_count <= 5:  # Show first 5 not found
                    print(f"   ⚠️ Not found: {csv_title[:60]}")
        
        db.commit()
        print(f"   ✓ Updated {updated_count} tenders")
        if not_found_count > 0:
            print(f"   ⚠️ {not_found_count} tenders not found in database\n")
        
        # Now re-run summary generation
        print("3️⃣ Re-generating summaries with restored descriptions...")
        
        from app.services.ai.hybrid_summarizer import hybrid_summarizer
        
        # Get all tenders that need re-summarization
        tenders = db.query(Tender).filter(Tender.description.isnot(None)).all()
        
        resummary_count = 0
        for tender in tenders[:50]:  # Process first 50 as sample
            try:
                summary = hybrid_summarizer.summarize_tender(tender.description)
                tender.ai_summary = summary
                resummary_count += 1
                
                if resummary_count % 5 == 0:
                    print(f"   Re-summarized {resummary_count} tenders...")
            except Exception as e:
                print(f"   ❌ Error summarizing {tender.title[:50]}: {e}")
        
        db.commit()
        print(f"   ✓ Re-generated {resummary_count} summaries\n")
        
        # Sample and display results
        print("4️⃣ Sample results from restored data:\n")
        
        sample_tenders = db.query(Tender).filter(
            Tender.description.isnot(None)
        ).limit(3).all()
        
        for i, tender in enumerate(sample_tenders, 1):
            print(f"TENDER {i}:")
            print(f"Title: {tender.title[:70]}")
            print(f"Description (first 500 chars):\n{tender.description[:500]}\n")
            print(f"Summary (first 400 chars):\n{tender.ai_summary[:400] if tender.ai_summary else 'No summary'}\n")
            print("-" * 80 + "\n")
        
        print(f"\n{'='*80}")
        print("✅ RESTORATION COMPLETE")
        print(f"{'='*80}\n")
        print(f"Updated descriptions: {updated_count}")
        print(f"Re-generated summaries: {resummary_count}")
        print(f"\nNext steps:")
        print(f"1. Verify quality of restored summaries in the terminal above")
        print(f"2. Run: python3 -c 'from app.database import SessionLocal")
        print(f"        from app.models.tender import Tender")
        print(f"        db = SessionLocal()")
        print(f"        t = db.query(Tender).filter(Tender.ai_summary.isnot(None)).count()")
        print(f"        print(f\"Total summaries: {{t}}\")'")
        print(f"3. To re-migrate all: python3 migrate_summaries_to_hybrid.py")
        
    except Exception as e:
        print(f"\n❌ Error during restoration: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()

