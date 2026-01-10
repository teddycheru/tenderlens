#!/usr/bin/env python3
"""
Setup script to:
1. Drop existing tenders table
2. Run migrations to create new schema with content generation fields
3. Import pre-processed tender data from JSON
"""

import os
import sys
import subprocess
from pathlib import Path
from sqlalchemy import text
from app.database import SessionLocal, engine
from app.services.pipeline.json_content_importer import JSONContentImporter

def confirm_action(message: str) -> bool:
    """Ask user for confirmation."""
    response = input(f"\n⚠️  {message} (yes/no): ").strip().lower()
    return response == 'yes'

def drop_tenders_table():
    """Drop the tenders table if it exists."""
    print("\n" + "="*80)
    print("STEP 1: DROP EXISTING TENDERS TABLE")
    print("="*80)

    if not confirm_action("Drop the existing 'tenders' table? This will delete all existing tender records."):
        print("Skipping table drop.")
        return False

    try:
        with engine.connect() as connection:
            # Drop table if exists
            connection.execute(text("DROP TABLE IF EXISTS tenders CASCADE"))
            connection.commit()
            print("✅ Tenders table dropped successfully")
            return True
    except Exception as e:
        print(f"❌ Error dropping table: {e}")
        return False

def run_migrations():
    """Create database schema from SQLAlchemy models."""
    print("\n" + "="*80)
    print("STEP 2: CREATE DATABASE SCHEMA")
    print("="*80)

    try:
        from app.database import Base, engine
        from app.models import tender, user, company, alert

        print("Creating database schema from models...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database schema created successfully")
        return True

    except Exception as e:
        print(f"❌ Error creating schema: {e}")
        import traceback
        traceback.print_exc()
        return False

def import_json_data():
    """Import pre-processed tender data from JSON."""
    print("\n" + "="*80)
    print("STEP 3: IMPORT PROCESSED TENDER DATA")
    print("="*80)

    json_path = Path('content_pipeline/output/processed_tenders.json')

    if not json_path.exists():
        print(f"❌ JSON file not found: {json_path}")
        return False

    try:
        db = SessionLocal()
        importer = JSONContentImporter(db)

        print(f"Importing from: {json_path}")
        stats = importer.import_from_json(json_path)

        print("\n" + "="*80)
        print("IMPORT RESULTS")
        print("="*80)
        print(f"Total tenders in JSON:     {stats['total']}")
        print(f"Successfully updated:      {stats['updated']}")
        print(f"Skipped (already exists):  {stats['skipped']}")
        print(f"Errors:                    {stats['errors']}")
        print(f"With generated content:    {stats['generated_count']}")

        db.close()

        if stats['updated'] > 0:
            print(f"\n✅ Successfully imported {stats['updated']} tenders!")
            return True
        else:
            print(f"\n⚠️  No tenders were imported")
            return False

    except Exception as e:
        print(f"❌ Error importing data: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_import():
    """Verify the import by showing sample records."""
    print("\n" + "="*80)
    print("STEP 4: VERIFY IMPORT")
    print("="*80)

    try:
        db = SessionLocal()
        from app.models.tender import Tender

        count = db.query(Tender).count()
        print(f"Total tender records in database: {count}")

        if count > 0:
            # Get first tender with generated content
            tender = db.query(Tender).filter(
                Tender.content_generated_at.isnot(None)
            ).first()

            if tender:
                print(f"\n✅ Sample tender with generated content:")
                print(f"   ID: {tender.id}")
                print(f"   Title: {tender.title[:80]}...")
                print(f"   Category: {tender.category}")
                print(f"   Region: {tender.region}")
                print(f"   Has clean_description: {bool(tender.clean_description)}")
                print(f"   Has highlights: {bool(tender.highlights)}")
                print(f"   Has extracted_data: {bool(tender.extracted_data)}")
                print(f"   Generated at: {tender.content_generated_at}")

                if tender.extracted_data:
                    print(f"\n   Extracted Data Keys:")
                    for key in tender.extracted_data.keys():
                        print(f"   - {key}")

        db.close()
        return True

    except Exception as e:
        print(f"❌ Error verifying import: {e}")
        return False

def main():
    """Run the complete setup process."""
    print("\n" + "="*80)
    print("CONTENT PIPELINE DATABASE SETUP")
    print("="*80)
    print("\nThis script will:")
    print("1. Drop the existing 'tenders' table")
    print("2. Run Alembic migrations to create new schema")
    print("3. Import 190+ processed tenders from JSON")
    print("4. Verify the import")

    steps_completed = 0

    # Step 1: Drop table
    if drop_tenders_table():
        steps_completed += 1
    else:
        print("Setup cancelled.")
        return

    # Step 2: Run migrations
    if run_migrations():
        steps_completed += 1
    else:
        print("❌ Migration failed. Setup incomplete.")
        return

    # Step 3: Import data
    if import_json_data():
        steps_completed += 1
    else:
        print("❌ Import failed. Setup incomplete.")
        return

    # Step 4: Verify
    if verify_import():
        steps_completed += 1

    # Summary
    print("\n" + "="*80)
    print("SETUP COMPLETE")
    print("="*80)
    print(f"\n✅ All {steps_completed}/4 steps completed successfully!")
    print("\nNext steps:")
    print("1. Start the backend: python -m uvicorn app.main:app --reload")
    print("2. Access API docs: http://localhost:8000/docs")
    print("3. Fetch tenders: GET /api/v1/tenders/")
    print("4. Frontend can now access all generated content and extracted data")

if __name__ == '__main__':
    main()
