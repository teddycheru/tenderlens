"""
Tests for the CSV importer service.
"""

import hashlib
import pytest
from pathlib import Path
from datetime import datetime, date

from app.services.pipeline.csv_importer import (
    CSVImportConfig,
    CSVImporter,
    MERKATO_CONFIG,
    create_importer_for_source,
)
from app.models.tender import Tender, TenderStatus


class TestCSVImportConfig:
    """Test cases for CSVImportConfig."""

    def test_config_initialization(self):
        """Test basic config initialization"""
        config = CSVImportConfig(
            source_name="test_source",
            field_mapping={"Title": "title", "Description": "description"},
        )
        assert config.source_name == "test_source"
        assert config.field_mapping == {"Title": "title", "Description": "description"}
        assert config.default_status == TenderStatus.PUBLISHED

    def test_config_with_status_mapping(self):
        """Test config with custom status mapping"""
        status_mapping = {"open": TenderStatus.PUBLISHED}
        config = CSVImportConfig(
            source_name="test",
            field_mapping={},
            status_mapping=status_mapping,
            default_status=TenderStatus.DRAFT,
        )
        assert config.status_mapping == status_mapping
        assert config.default_status == TenderStatus.DRAFT


class TestCSVImporter:
    """Test cases for CSVImporter class."""

    def test_generate_external_id(self, test_db):
        """Test external ID generation from URL"""
        config = CSVImportConfig("test", {})
        importer = CSVImporter(test_db, config)

        url = "https://example.com/tender1"
        external_id = importer._generate_external_id(url)

        # Should be consistent
        assert external_id == importer._generate_external_id(url)

        # Should be SHA256 hash
        expected = hashlib.sha256(url.encode('utf-8')).hexdigest()
        assert external_id == expected

    def test_generate_content_hash(self, test_db):
        """Test content hash generation"""
        config = CSVImportConfig("test", {})
        importer = CSVImporter(test_db, config)

        description = "This is a test description"
        content_hash = importer._generate_content_hash(description)

        # Should be consistent
        assert content_hash == importer._generate_content_hash(description)

        # Should be MD5 hash
        expected = hashlib.md5(description.encode('utf-8')).hexdigest()
        assert content_hash == expected

    def test_generate_content_hash_empty(self, test_db):
        """Test content hash with empty description"""
        config = CSVImportConfig("test", {})
        importer = CSVImporter(test_db, config)

        assert importer._generate_content_hash("") == ""
        assert importer._generate_content_hash(None) == ""

    def test_map_status_default(self, test_db):
        """Test status mapping with default value"""
        config = CSVImportConfig("test", {}, default_status=TenderStatus.DRAFT)
        importer = CSVImporter(test_db, config)

        assert importer._map_status("") == TenderStatus.DRAFT
        assert importer._map_status(None) == TenderStatus.DRAFT
        assert importer._map_status("unknown") == TenderStatus.DRAFT

    def test_map_status_builtin_mappings(self, test_db):
        """Test built-in status mappings"""
        config = CSVImportConfig("test", {})
        importer = CSVImporter(test_db, config)

        assert importer._map_status("open") == TenderStatus.PUBLISHED
        assert importer._map_status("OPEN") == TenderStatus.PUBLISHED
        assert importer._map_status("closed") == TenderStatus.CLOSED
        assert importer._map_status("cancelled") == TenderStatus.CANCELLED

    def test_map_status_custom_mapping(self, test_db):
        """Test custom status mapping"""
        status_mapping = {"active": TenderStatus.PUBLISHED}
        config = CSVImportConfig("test", {}, status_mapping=status_mapping)
        importer = CSVImporter(test_db, config)

        assert importer._map_status("active") == TenderStatus.PUBLISHED

    def test_url_exists_false(self, test_db):
        """Test URL existence check when URL doesn't exist"""
        config = CSVImportConfig("test", {})
        importer = CSVImporter(test_db, config)

        assert importer._url_exists("https://example.com/nonexistent") is False

    def test_url_exists_true(self, test_db):
        """Test URL existence check when URL exists"""
        config = CSVImportConfig("test", {})
        importer = CSVImporter(test_db, config)

        # Create a tender with a URL
        tender = Tender(
            title="Test Tender",
            description="Test Description",
            source_url="https://example.com/tender1",
            source="test",
            external_id="test123",
        )
        test_db.add(tender)
        test_db.commit()

        assert importer._url_exists("https://example.com/tender1") is True

    def test_parse_csv_row_basic(self, test_db):
        """Test parsing a basic CSV row"""
        config = CSVImportConfig(
            "test",
            field_mapping={
                "Title": "title",
                "Description": "description",
                "URL": "source_url",
            },
        )
        importer = CSVImporter(test_db, config)

        row = {
            "Title": "Test Tender",
            "Description": "Test Description",
            "URL": "https://example.com/tender1",
        }

        result = importer._parse_csv_row(row)

        assert result["title"] == "Test Tender"
        assert result["description"] == "Test Description"
        assert result["source_url"] == "https://example.com/tender1"
        assert result["source"] == "test"
        assert "external_id" in result
        assert "content_hash" in result
        assert "scraped_at" in result

    def test_parse_csv_row_with_date(self, test_db):
        """Test parsing CSV row with date fields"""
        config = CSVImportConfig(
            "test",
            field_mapping={
                "Title": "title",
                "Description": "description",
                "Date": "published_date",
            },
        )
        importer = CSVImporter(test_db, config)

        row = {
            "Title": "Test",
            "Description": "Test",
            "Date": "2024-01-15",
        }

        result = importer._parse_csv_row(row)
        assert result["published_date"] == date(2024, 1, 15)

    def test_parse_csv_row_with_category(self, test_db):
        """Test parsing CSV row with Predicted_Category"""
        config = CSVImportConfig(
            "test",
            field_mapping={
                "Title": "title",
                "Description": "description",
                "Category": "category",
            },
        )
        importer = CSVImporter(test_db, config)

        row = {
            "Title": "Test",
            "Description": "Test",
            "Category": "General",
            "Predicted_Category": "IT & Technology",
        }

        result = importer._parse_csv_row(row)
        # Should prefer Predicted_Category
        assert result["category"] == "IT & Technology"

    def test_parse_csv_row_empty_description_fallback(self, test_db):
        """Test that empty description falls back to title"""
        config = CSVImportConfig(
            "test",
            field_mapping={
                "Title": "title",
                "Description": "description",
            },
        )
        importer = CSVImporter(test_db, config)

        row = {
            "Title": "Test Tender Title",
            "Description": "",
        }

        result = importer._parse_csv_row(row)
        assert result["description"] == "Test Tender Title"

    def test_import_from_csv_success(self, test_db, sample_csv_path):
        """Test successful CSV import with batch size of 1 to handle in-CSV duplicates"""
        config = CSVImportConfig(
            "test_source",
            field_mapping={
                "URL": "source_url",
                "Date": "published_date",
                "Title": "title",
                "Predicted_Category": "category",
                "Description": "description",
            },
        )
        importer = CSVImporter(test_db, config)

        # Use batch_size=1 to handle duplicates within the CSV file
        stats = importer.import_from_csv(sample_csv_path, skip_duplicates=True, batch_size=1)

        # Check statistics
        assert stats["total"] == 10  # 10 rows in sample CSV
        # Should import at least some records (some may have invalid dates/missing fields)
        assert stats["imported"] +  stats["skipped"] + stats["errors"] == stats["total"]
        # At least one duplicate should be detected (row 6 is duplicate of row 1)
        assert stats["skipped"] >= 1

        # Check that tenders were actually created (if any were imported)
        tenders = test_db.query(Tender).all()
        assert len(tenders) == stats["imported"]

    def test_import_from_csv_skip_duplicates(self, test_db, temp_csv_file):
        """Test that duplicate URLs are skipped"""
        config = CSVImportConfig(
            "test",
            field_mapping={
                "URL": "source_url",
                "Date": "published_date",
                "Title": "title",
                "Predicted_Category": "category",
                "Description": "description",
            },
        )
        importer = CSVImporter(test_db, config)

        # Import once
        stats1 = importer.import_from_csv(temp_csv_file, skip_duplicates=True)
        assert stats1["imported"] == 2

        # Import again - should skip all
        stats2 = importer.import_from_csv(temp_csv_file, skip_duplicates=True)
        assert stats2["skipped"] == 2
        assert stats2["imported"] == 0

    def test_import_from_csv_batch_processing(self, test_db, sample_csv_path):
        """Test batch processing with small batch size"""
        config = CSVImportConfig(
            "test",
            field_mapping={
                "URL": "source_url",
                "Date": "published_date",
                "Title": "title",
                "Predicted_Category": "category",
                "Description": "description",
            },
        )
        importer = CSVImporter(test_db, config)

        # Import with batch size of 2
        stats = importer.import_from_csv(sample_csv_path, batch_size=2)

        # Should still import successfully
        assert stats["imported"] > 0

    def test_import_missing_required_fields(self, test_db, tmp_path):
        """Test that rows with missing required fields are skipped"""
        # Create CSV with missing title
        csv_path = tmp_path / "invalid.csv"
        csv_content = """URL,Date,Title,Description
https://test.com/t1,2024-01-15,,Missing Title
"""
        csv_path.write_text(csv_content)

        config = CSVImportConfig(
            "test",
            field_mapping={
                "URL": "source_url",
                "Date": "published_date",
                "Title": "title",
                "Description": "description",
            },
        )
        importer = CSVImporter(test_db, config)

        stats = importer.import_from_csv(csv_path)

        # Should be counted as error due to missing title
        assert stats["errors"] > 0
        assert stats["imported"] == 0


class TestMerkatoConfig:
    """Test cases for predefined MERKATO_CONFIG."""

    def test_merkato_config_exists(self):
        """Test that MERKATO_CONFIG is properly defined"""
        assert MERKATO_CONFIG is not None
        assert MERKATO_CONFIG.source_name == "2merkato"
        assert "Title" in MERKATO_CONFIG.field_mapping
        assert "Description" in MERKATO_CONFIG.field_mapping
        assert "URL" in MERKATO_CONFIG.field_mapping

    def test_merkato_config_field_mappings(self):
        """Test MERKATO_CONFIG field mappings"""
        expected_mappings = {
            "Title": "title",
            "Description": "description",
            "URL": "source_url",
            "Region": "region",
            "Closing Date": "deadline",
            "Published On": "published_date",
            "Predicted_Category": "category",
        }
        assert MERKATO_CONFIG.field_mapping == expected_mappings


class TestCreateImporterFactory:
    """Test cases for create_importer_for_source factory function."""

    def test_create_merkato_importer(self, test_db):
        """Test creating importer for 2merkato source"""
        importer = create_importer_for_source(test_db, "2merkato")

        assert isinstance(importer, CSVImporter)
        assert importer.config.source_name == "2merkato"

    def test_create_importer_unknown_source(self, test_db):
        """Test that unknown source raises ValueError"""
        with pytest.raises(ValueError, match="Unknown source"):
            create_importer_for_source(test_db, "unknown_source")

    def test_create_importer_error_message(self, test_db):
        """Test that error message includes available sources"""
        try:
            create_importer_for_source(test_db, "invalid")
        except ValueError as e:
            assert "2merkato" in str(e)


class TestIntegration:
    """Integration tests with real CSV data."""

    def test_full_import_workflow(self, test_db, temp_csv_file):
        """Test complete import workflow from CSV to database"""
        # Create custom config similar to MERKATO for testing
        config = CSVImportConfig(
            "2merkato",
            field_mapping={
                "URL": "source_url",
                "Date": "published_date",
                "Title": "title",
                "Predicted_Category": "category",
                "Description": "description",
            },
        )
        importer = CSVImporter(test_db, config)

        # Import CSV
        stats = importer.import_from_csv(temp_csv_file, skip_duplicates=True)

        # Verify statistics
        assert stats["total"] > 0
        assert stats["imported"] + stats["skipped"] + stats["errors"] == stats["total"]

        # Verify data in database
        tenders = test_db.query(Tender).all()
        assert len(tenders) == stats["imported"]

        # Check first tender has required fields (if any imported)
        if len(tenders) > 0:
            tender = tenders[0]
            assert tender.title is not None
            assert tender.description is not None
            assert tender.source == "2merkato"
            assert tender.external_id is not None
            assert tender.scraped_at is not None

    def test_reimport_detects_duplicates(self, test_db, temp_csv_file):
        """Test that re-importing the same CSV detects duplicates"""
        config = CSVImportConfig(
            "2merkato",
            field_mapping={
                "URL": "source_url",
                "Date": "published_date",
                "Title": "title",
                "Predicted_Category": "category",
                "Description": "description",
            },
        )
        importer = CSVImporter(test_db, config)

        # First import
        stats1 = importer.import_from_csv(temp_csv_file)
        imported_count = stats1["imported"]

        # Second import
        stats2 = importer.import_from_csv(temp_csv_file)

        # All previously imported records should be skipped
        assert stats2["skipped"] >= imported_count
