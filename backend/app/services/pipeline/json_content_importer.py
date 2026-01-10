"""
JSON Content Importer Service for importing processed tender content from the offline LLM pipeline.

This service reads the output from the content-generator script (process_tenders.py)
and imports the generated content (summaries, clean descriptions, highlights, extracted data)
into the database.

The workflow is:
1. Run content-generator/process_tenders.py on CSV file → generates processed_tenders.json
2. Use this importer to load the JSON into the database
3. Frontend reads the processed data from the database
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.tender import Tender, TenderStatus
from app.utils.date_parser import parse_flexible_date

logger = logging.getLogger(__name__)


class JSONContentImporter:
    """Service for importing processed tender content from JSON files."""

    def __init__(self, db: Session):
        """
        Initialize the JSON content importer.

        Args:
            db: Database session
        """
        self.db = db

    def _find_or_create_tender(self, original_data: Dict[str, Any]) -> Optional[Tender]:
        """
        Find or create a tender based on the URL in the original data.

        Args:
            original_data: Original tender data from JSON (contains 'url' field)

        Returns:
            Tender object or None if not found and cannot be created
        """
        url = original_data.get('url')
        if not url:
            logger.warning("No URL found in original data")
            return None

        # Try to find existing tender by URL
        existing_tender = self.db.query(Tender).filter(Tender.source_url == url).first()
        if existing_tender:
            return existing_tender

        # If tender doesn't exist, we need to create it from the original data
        # This happens when we're importing processed content for new tenders
        try:
            tender_data = {
                'title': original_data.get('title', 'Unknown'),
                'description': original_data.get('description', ''),
                'source_url': url,
                'category': original_data.get('category'),
                'region': original_data.get('region'),
                'language': original_data.get('language', 'en'),
                'source': original_data.get('source', 'content-generator'),
                'status': TenderStatus.PUBLISHED,
                'published_date': parse_flexible_date(original_data.get('published_on', '')),
                'scraped_at': datetime.utcnow(),
            }

            # Handle deadline/closing date
            closing_date = original_data.get('closing_date_raw')
            if closing_date:
                tender_data['deadline'] = parse_flexible_date(closing_date)

            tender = Tender(**tender_data)
            self.db.add(tender)
            self.db.commit()
            logger.info(f"Created new tender: {tender.id} from URL: {url}")
            return tender

        except Exception as e:
            logger.error(f"Error creating tender from original data: {e}")
            return None

    def import_from_json(
        self,
        json_path: Path,
        skip_if_already_generated: bool = True,
        batch_size: int = 50,
    ) -> Dict[str, Any]:
        """
        Import processed tender content from JSON file.

        The JSON file should be in the format output by content-generator/process_tenders.py:
        {
            "metadata": {...},
            "tenders": [
                {
                    "id": "tender_000000",
                    "original": {...},
                    "extracted": {...},
                    "generated": {...},
                    "processing_status": "success"
                },
                ...
            ]
        }

        Args:
            json_path: Path to the JSON file from content-generator
            skip_if_already_generated: If True, skip tenders that already have generated content
            batch_size: Number of records to update at once

        Returns:
            Dictionary with import statistics:
                - total: Total tenders in JSON
                - updated: Successfully updated
                - skipped: Skipped (already generated or not found)
                - errors: Failed to update
                - generated_count: Number of tenders with new generated content
        """
        stats = {
            "total": 0,
            "updated": 0,
            "skipped": 0,
            "errors": 0,
            "generated_count": 0,
            "updated_tender_ids": [],
        }

        logger.info(f"Starting JSON content import from {json_path}")

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            tenders_list = data.get('tenders', [])
            metadata = data.get('metadata', {})

            logger.info(f"Importing content for {len(tenders_list)} tenders")
            logger.info(f"Metadata: {metadata}")

            batch_count = 0
            for tender_json in tenders_list:
                stats["total"] += 1

                try:
                    # Find or create the tender
                    original_data = tender_json.get('original', {})
                    tender = self._find_or_create_tender(original_data)

                    if not tender:
                        logger.warning(f"Could not find or create tender from JSON entry {stats['total']}")
                        stats["skipped"] += 1
                        continue

                    # Skip if already has generated content
                    if skip_if_already_generated and tender.content_generated_at:
                        logger.debug(f"Skipping tender {tender.id} - already has generated content")
                        stats["skipped"] += 1
                        continue

                    # Extract generated content
                    generated_data = tender_json.get('generated', {})
                    extracted_data = tender_json.get('extracted', {})
                    processing_status = tender_json.get('processing_status', 'unknown')

                    # Update tender with generated content
                    tender.clean_description = generated_data.get('clean_description')
                    tender.highlights = generated_data.get('highlights')
                    tender.extracted_data = extracted_data
                    tender.content_generated_at = datetime.utcnow()

                    # Store any generation errors
                    generation_errors = generated_data.get('generation_errors', [])
                    if generation_errors:
                        tender.content_generation_errors = generation_errors

                    # Also update ai_summary if available (for compatibility)
                    if generated_data.get('summary') and not tender.ai_summary:
                        tender.ai_summary = generated_data.get('summary')

                    self.db.add(tender)
                    batch_count += 1
                    stats["generated_count"] += 1
                    stats["updated_tender_ids"].append(str(tender.id))

                    # Commit in batches
                    if batch_count >= batch_size:
                        self.db.commit()
                        logger.info(f"Imported batch of {batch_count} tenders")
                        batch_count = 0
                        stats["updated"] += batch_count

                except Exception as e:
                    logger.error(f"Error processing tender {stats['total']}: {e}")
                    stats["errors"] += 1
                    continue

            # Commit remaining batch
            if batch_count > 0:
                self.db.commit()
                logger.info(f"Imported final batch of {batch_count} tenders")
                stats["updated"] += batch_count

        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON file {json_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error reading JSON file {json_path}: {e}")
            self.db.rollback()
            raise

        logger.info(
            f"JSON import completed: {stats['updated']} updated, "
            f"{stats['skipped']} skipped, {stats['errors']} errors "
            f"out of {stats['total']} total tenders"
        )

        return stats

    def import_from_directory(
        self,
        directory: Path,
        pattern: str = "processed_tenders.json",
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Import processed content from all matching JSON files in a directory.

        Args:
            directory: Directory to search for JSON files
            pattern: File pattern to match (default: "processed_tenders.json")
            **kwargs: Additional arguments to pass to import_from_json

        Returns:
            List of import statistics for each file
        """
        results = []
        json_files = list(directory.glob(pattern))

        logger.info(f"Found {len(json_files)} JSON files matching pattern '{pattern}'")

        for json_file in json_files:
            logger.info(f"Processing {json_file.name}...")
            try:
                stats = self.import_from_json(json_file, **kwargs)
                results.append({
                    "file": str(json_file),
                    "stats": stats
                })
            except Exception as e:
                logger.error(f"Failed to import {json_file}: {e}")
                results.append({
                    "file": str(json_file),
                    "error": str(e)
                })

        return results


def create_content_importer(db: Session) -> JSONContentImporter:
    """
    Factory function to create a JSON content importer.

    Args:
        db: Database session

    Returns:
        Configured JSONContentImporter instance
    """
    return JSONContentImporter(db)
