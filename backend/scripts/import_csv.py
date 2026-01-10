#!/usr/bin/env python3
"""
CLI script for importing tenders from CSV files.

Usage:
    python scripts/import_csv.py <csv_file_path> <source_name> [--skip-duplicates]

Examples:
    python scripts/import_csv.py data/2merkato_tenders.csv 2merkato
    python scripts/import_csv.py data/ethiotenders.csv ethiotenders --skip-duplicates
"""

import sys
import argparse
import logging
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.services.pipeline.csv_importer import create_importer_for_source

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point for CSV import script."""
    parser = argparse.ArgumentParser(
        description='Import tenders from CSV files into the database',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Import 2merkato tenders:
    python scripts/import_csv.py 2merkato_tenders.csv 2merkato

  Import with duplicate checking:
    python scripts/import_csv.py data.csv 2merkato --skip-duplicates

  Import with custom batch size:
    python scripts/import_csv.py data.csv 2merkato --batch-size 50

Available sources:
  - 2merkato: Tenders from 2merkato.com
  (More sources can be added in csv_importer.py)
        """
    )

    parser.add_argument(
        'csv_file',
        type=str,
        help='Path to the CSV file to import'
    )

    parser.add_argument(
        'source',
        type=str,
        help='Source name (e.g., 2merkato, ethiotenders)'
    )

    parser.add_argument(
        '--skip-duplicates',
        action='store_true',
        default=True,
        help='Skip tenders with duplicate URLs (default: True)'
    )

    parser.add_argument(
        '--no-skip-duplicates',
        dest='skip_duplicates',
        action='store_false',
        help='Do not skip duplicate URLs'
    )

    parser.add_argument(
        '--batch-size',
        type=int,
        default=100,
        help='Number of records to commit at once (default: 100)'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    # Set verbose logging if requested
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validate CSV file exists
    csv_path = Path(args.csv_file)
    if not csv_path.exists():
        logger.error(f"CSV file not found: {csv_path}")
        sys.exit(1)

    if not csv_path.is_file():
        logger.error(f"Path is not a file: {csv_path}")
        sys.exit(1)

    logger.info(f"Starting import from {csv_path}")
    logger.info(f"Source: {args.source}")
    logger.info(f"Skip duplicates: {args.skip_duplicates}")
    logger.info(f"Batch size: {args.batch_size}")

    # Create database session
    db = SessionLocal()

    try:
        # Create importer for the specified source
        try:
            importer = create_importer_for_source(db, args.source)
        except ValueError as e:
            logger.error(str(e))
            sys.exit(1)

        # Perform the import
        stats = importer.import_from_csv(
            csv_path=csv_path,
            skip_duplicates=args.skip_duplicates,
            batch_size=args.batch_size
        )

        # Print summary
        print("\n" + "=" * 60)
        print("IMPORT SUMMARY")
        print("=" * 60)
        print(f"Total rows processed:  {stats['total']}")
        print(f"Successfully imported: {stats['imported']}")
        print(f"Skipped (duplicates):  {stats['skipped']}")
        print(f"Errors:                {stats['errors']}")

        if stats.get('ai_processing_task_id'):
            print("=" * 60)
            print("AI PROCESSING QUEUED")
            print("=" * 60)
            print(f"Task ID: {stats['ai_processing_task_id']}")
            print("The imported tenders have been queued for AI processing.")
            print("Check Flower dashboard at http://localhost:5555 to monitor progress.")

        print("=" * 60)

        if stats['errors'] > 0:
            print("\nWarning: Some rows failed to import. Check logs for details.")
            sys.exit(1)
        else:
            print("\nImport completed successfully!")
            sys.exit(0)

    except Exception as e:
        logger.error(f"Import failed: {e}", exc_info=True)
        sys.exit(1)

    finally:
        db.close()


if __name__ == '__main__':
    main()
