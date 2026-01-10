#!/usr/bin/env python3
"""
Load processed tenders from JSON (output of content_pipeline) into the database.

Usage:
    python scripts/load_processed_json.py <json_file_path>

Example:
    python scripts/load_processed_json.py content_pipeline/output/processed_tenders.json
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.models.tender import Tender, TenderStatus
from sqlalchemy.exc import IntegrityError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_date(date_str: str) -> datetime:
    """Parse date string to datetime object"""
    if not date_str:
        return None
    try:
        # Try ISO format first
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except:
        try:
            # Try other common formats
            return datetime.strptime(date_str, "%Y-%m-%d")
        except:
            return None


def load_tender_to_db(db, tender_data: Dict[str, Any], source: str = "content_pipeline") -> bool:
    """
    Load a single tender into the database

    Args:
        db: Database session
        tender_data: Processed tender data
        source: Source identifier

    Returns:
        True if successful, False otherwise
    """
    try:
        original = tender_data.get('original', {})
        extracted = tender_data.get('extracted', {})
        generated = tender_data.get('generated', {})

        # Extract dates
        dates = extracted.get('dates', {})
        closing_date = parse_date(dates.get('closing_date'))
        published_date = parse_date(dates.get('published_date'))

        # Extract financial data
        financial = extracted.get('financial', {})

        # Create tender object
        tender = Tender(
            title=original.get('title', '')[:255],  # Limit to 255 chars
            description=original.get('description', '') or extracted.get('cleaned_text', '') or '',
            category=original.get('category'),
            region=original.get('region'),
            language=original.get('language', 'en'),
            source=source,
            source_url=original.get('url'),
            deadline=closing_date.date() if closing_date else None,
            published_date=published_date.date() if published_date else None,
            status=TenderStatus.PUBLISHED if original.get('status') == 'Open' else TenderStatus.CLOSED,

            # AI Processing fields
            clean_description=generated.get('clean_description'),
            highlights=generated.get('highlights'),
            extracted_data=extracted,  # Store all extracted data as JSON

            # Additional metadata
            external_id=tender_data.get('id'),
            ai_processed=bool(generated),
            ai_processed_at=datetime.now() if generated else None,
        )

        db.add(tender)
        db.commit()
        return True

    except IntegrityError as e:
        db.rollback()
        if 'unique constraint' in str(e).lower():
            logger.debug(f"Skipping duplicate tender: {original.get('url')}")
            return False
        else:
            logger.error(f"Database integrity error: {e}")
            return False
    except Exception as e:
        db.rollback()
        logger.error(f"Error loading tender: {e}")
        logger.debug(f"Tender data: {tender_data}")
        return False


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python scripts/load_processed_json.py <json_file_path>")
        sys.exit(1)

    json_file = Path(sys.argv[1])

    if not json_file.exists():
        logger.error(f"JSON file not found: {json_file}")
        sys.exit(1)

    logger.info(f"Loading processed tenders from: {json_file}")

    # Load JSON
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f"Failed to load JSON: {e}")
        sys.exit(1)

    tenders = data.get('tenders', [])
    metadata = data.get('metadata', {})

    logger.info(f"Found {len(tenders)} tenders in JSON")
    logger.info(f"Metadata: {metadata}")

    # Create database session
    db = SessionLocal()

    stats = {
        'total': len(tenders),
        'imported': 0,
        'skipped': 0,
        'errors': 0
    }

    try:
        for i, tender_data in enumerate(tenders):
            if (i + 1) % 10 == 0:
                logger.info(f"Processing tender {i + 1}/{len(tenders)}")

            success = load_tender_to_db(db, tender_data)

            if success:
                stats['imported'] += 1
            else:
                stats['skipped'] += 1

        # Print summary
        print("\n" + "=" * 60)
        print("IMPORT SUMMARY")
        print("=" * 60)
        print(f"Total tenders in JSON:  {stats['total']}")
        print(f"Successfully imported:  {stats['imported']}")
        print(f"Skipped (duplicates):   {stats['skipped']}")
        print(f"Errors:                 {stats['errors']}")
        print("=" * 60)

        if stats['imported'] > 0:
            logger.info("Import completed successfully!")
            sys.exit(0)
        else:
            logger.warning("No new tenders were imported")
            sys.exit(0)

    except Exception as e:
        logger.error(f"Import failed: {e}", exc_info=True)
        sys.exit(1)
    finally:
        db.close()


if __name__ == '__main__':
    main()
