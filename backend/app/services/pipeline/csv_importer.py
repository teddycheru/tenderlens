"""
CSV Importer Service for importing tenders from various CSV sources.

This service provides flexible CSV import functionality with:
- Configurable field mappings
- Source-based status mapping
- Date parsing with multiple format support
- Duplicate detection by URL
- Category mapping
- Automatic AI processing of imported tenders
"""

import csv
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.tender import Tender, TenderStatus
from app.utils.date_parser import parse_flexible_date

logger = logging.getLogger(__name__)


class CSVImportConfig:
    """Configuration for CSV import operations."""

    def __init__(
        self,
        source_name: str,
        field_mapping: Dict[str, str],
        status_mapping: Optional[Dict[str, TenderStatus]] = None,
        default_status: TenderStatus = TenderStatus.PUBLISHED,
    ):
        """
        Initialize CSV import configuration.

        Args:
            source_name: Name of the data source (e.g., "2merkato", "ethiotenders")
            field_mapping: Mapping from CSV columns to Tender model fields
                Example: {"Title": "title", "Description": "description"}
            status_mapping: Optional mapping of source status values to TenderStatus enum
            default_status: Default status if no mapping found
        """
        self.source_name = source_name
        self.field_mapping = field_mapping
        self.status_mapping = status_mapping or {}
        self.default_status = default_status


class CSVImporter:
    """Service for importing tenders from CSV files."""

    def __init__(self, db: Session, config: CSVImportConfig):
        """
        Initialize the CSV importer.

        Args:
            db: Database session
            config: Import configuration
        """
        self.db = db
        self.config = config

    def _generate_external_id(self, url: str) -> str:
        """
        Generate a unique external ID based on the source URL.

        Args:
            url: Source URL of the tender

        Returns:
            SHA256 hash of the URL
        """
        return hashlib.sha256(url.encode('utf-8')).hexdigest()

    def _generate_content_hash(self, description: str) -> str:
        """
        Generate a content hash for deduplication.

        Args:
            description: Tender description

        Returns:
            MD5 hash of the description
        """
        if not description:
            return ""
        return hashlib.md5(description.encode('utf-8')).hexdigest()

    def _map_status(self, source_status: str) -> TenderStatus:
        """
        Map source status string to TenderStatus enum.

        Args:
            source_status: Status string from the source

        Returns:
            Mapped TenderStatus value
        """
        if not source_status:
            return self.config.default_status

        # Check if there's a specific mapping
        status_lower = source_status.lower().strip()
        if status_lower in self.config.status_mapping:
            return self.config.status_mapping[status_lower]

        # Default mapping logic
        if status_lower == "open":
            return TenderStatus.PUBLISHED
        elif status_lower == "closed":
            return TenderStatus.CLOSED
        elif status_lower == "cancelled":
            return TenderStatus.CANCELLED
        else:
            return self.config.default_status

    def _url_exists(self, url: str) -> bool:
        """
        Check if a tender with the given URL already exists.

        Args:
            url: URL to check

        Returns:
            True if URL exists, False otherwise
        """
        existing = self.db.query(Tender).filter(Tender.source_url == url).first()
        return existing is not None

    def _parse_csv_row(self, row: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """
        Parse a CSV row into tender data.

        Args:
            row: Dictionary containing CSV row data

        Returns:
            Dictionary of tender fields or None if row is invalid
        """
        tender_data = {}

        # Map fields according to configuration
        for csv_field, model_field in self.config.field_mapping.items():
            value = row.get(csv_field, "").strip()

            # Handle date fields
            if model_field in ["published_date", "deadline"]:
                tender_data[model_field] = parse_flexible_date(value)

            # Handle status field
            elif model_field == "status":
                tender_data[model_field] = self._map_status(value)

            # Handle category - use Predicted_Category if available
            elif model_field == "category":
                # Check if there's a Predicted_Category field
                predicted_category = row.get("Predicted_Category", "").strip()
                tender_data[model_field] = predicted_category if predicted_category else value

            # Handle other string fields
            else:
                tender_data[model_field] = value if value else None

        # Handle empty description - use title as fallback
        if not tender_data.get("description") and tender_data.get("title"):
            logger.debug(f"Using title as description fallback for: {tender_data['title'][:50]}")
            tender_data["description"] = tender_data["title"]

        # Add source information
        tender_data["source"] = self.config.source_name

        # Generate external_id from URL
        if "source_url" in tender_data and tender_data["source_url"]:
            tender_data["external_id"] = self._generate_external_id(tender_data["source_url"])

        # Generate content hash from description
        if "description" in tender_data and tender_data["description"]:
            tender_data["content_hash"] = self._generate_content_hash(tender_data["description"])

        # Add scraped_at timestamp
        tender_data["scraped_at"] = datetime.utcnow()

        return tender_data

    def import_from_csv(
        self,
        csv_path: Path,
        skip_duplicates: bool = True,
        batch_size: int = 100,
        auto_process_ai: bool = True,
    ) -> Dict[str, Any]:
        """
        Import tenders from a CSV file.

        Args:
            csv_path: Path to the CSV file
            skip_duplicates: If True, skip records with duplicate URLs
            batch_size: Number of records to commit at once
            auto_process_ai: If True, queue imported tenders for AI processing

        Returns:
            Dictionary with import statistics:
                - total: Total rows processed
                - imported: Successfully imported
                - skipped: Skipped (duplicates)
                - errors: Failed to import
                - ai_processing_task_id: Task ID if AI processing was queued
        """
        stats = {
            "total": 0,
            "imported": 0,
            "skipped": 0,
            "errors": 0,
            "imported_tender_ids": [],  # Track IDs for AI processing
            "ai_processing_task_id": None,
            "ai_queued_count": 0,
        }

        logger.info(f"Starting CSV import from {csv_path} for source '{self.config.source_name}'")

        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                batch = []

                for row in reader:
                    stats["total"] += 1

                    try:
                        # Parse the row
                        tender_data = self._parse_csv_row(row)

                        if not tender_data:
                            logger.warning(f"Row {stats['total']} could not be parsed")
                            stats["errors"] += 1
                            continue

                        # Validate required fields
                        if not tender_data.get("title"):
                            logger.warning(f"Row {stats['total']} missing required field 'title'")
                            stats["errors"] += 1
                            continue

                        if not tender_data.get("description"):
                            logger.warning(f"Row {stats['total']} missing required field 'description'")
                            stats["errors"] += 1
                            continue

                        # Check for duplicates
                        if skip_duplicates and tender_data.get("source_url"):
                            if self._url_exists(tender_data["source_url"]):
                                logger.debug(f"Skipping duplicate URL: {tender_data['source_url']}")
                                stats["skipped"] += 1
                                continue

                        # Create tender object
                        tender = Tender(**tender_data)
                        batch.append(tender)

                        # Commit in batches
                        if len(batch) >= batch_size:
                            self.db.add_all(batch)
                            self.db.commit()
                            # Track newly imported tender IDs for AI processing
                            for tender_obj in batch:
                                stats["imported_tender_ids"].append(str(tender_obj.id))
                            stats["imported"] += len(batch)
                            logger.info(f"Imported batch of {len(batch)} tenders")
                            batch = []

                    except Exception as e:
                        logger.error(f"Error processing row {stats['total']}: {e}")
                        stats["errors"] += 1
                        continue

                # Commit remaining batch
                if batch:
                    self.db.add_all(batch)
                    self.db.commit()
                    # Track newly imported tender IDs for AI processing
                    for tender_obj in batch:
                        stats["imported_tender_ids"].append(str(tender_obj.id))
                    stats["imported"] += len(batch)
                    logger.info(f"Imported final batch of {len(batch)} tenders")

        except Exception as e:
            logger.error(f"Error reading CSV file {csv_path}: {e}")
            self.db.rollback()
            raise

        logger.info(
            f"CSV import completed: {stats['imported']} imported, "
            f"{stats['skipped']} skipped, {stats['errors']} errors "
            f"out of {stats['total']} total rows"
        )

        # Auto-process imported tenders with AI if requested
        if auto_process_ai and stats['imported'] > 0 and stats.get('imported_tender_ids'):
            try:
                from app.workers.ai_tasks import batch_process_tenders_task

                # Queue ONLY the newly imported tenders for AI processing
                # This is more efficient than processing all unprocessed tenders
                tender_ids = stats['imported_tender_ids']
                logger.info(f"🤖 Queuing AI processing for {len(tender_ids)} newly imported tenders")

                task = batch_process_tenders_task.delay(tender_ids)
                stats['ai_processing_task_id'] = task.id
                stats['ai_queued_count'] = len(tender_ids)
                logger.info(f"✅ Queued batch AI processing task {task.id} for {len(tender_ids)} imported tenders")
            except Exception as e:
                logger.warning(f"Failed to queue AI processing: {e}")
                stats['ai_processing_task_id'] = None
                stats['ai_queued_count'] = 0

        return stats


# Predefined configurations for common sources
MERKATO_CONFIG = CSVImportConfig(
    source_name="2merkato",
    field_mapping={
        "Title": "title",
        "Description": "description",  # Using raw description (not Description_clean) for data quality
        "URL": "source_url",
        "Region": "region",
        "Closing Date": "deadline",
        "Published On": "published_date",
        "Predicted_Category": "category",
        "Language": "language",
        "TOR Download Link": "tor_url",
    },
    # Use PUBLISHED status for imported tenders to make them visible in UI
    # Historical/closed tenders use CLOSED status
    default_status=TenderStatus.PUBLISHED,
    status_mapping={
        "open": TenderStatus.PUBLISHED,
        "closed": TenderStatus.CLOSED,  # Use proper CLOSED status for historical tenders
    }
)


def create_importer_for_source(db: Session, source: str) -> CSVImporter:
    """
    Factory function to create an importer for a specific source.

    Args:
        db: Database session
        source: Source name (e.g., "2merkato")

    Returns:
        Configured CSVImporter instance

    Raises:
        ValueError: If source is not recognized
    """
    configs = {
        "2merkato": MERKATO_CONFIG,
        # Add more source configurations here as needed
    }

    if source not in configs:
        raise ValueError(f"Unknown source: {source}. Available sources: {list(configs.keys())}")

    return CSVImporter(db, configs[source])
