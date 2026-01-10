"""
Pytest configuration and shared fixtures for TenderLens tests.
"""

import os
import sys
from pathlib import Path
from uuid import uuid4, UUID as PyUUID

import pytest
from sqlalchemy import create_engine, event, types
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.dialects import sqlite, postgresql

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))


# Register UUID type for SQLite BEFORE importing models
class GUID(types.TypeDecorator):
    """Platform-independent GUID type.

    Uses CHAR(36) in SQLite, storing as string with hyphens.
    """
    impl = types.CHAR
    cache_ok = True

    def __init__(self, as_uuid=False):
        """Initialize GUID type.

        Args:
            as_uuid: Ignored, for compatibility with PostgreSQL UUID
        """
        super().__init__()
        self.as_uuid = as_uuid

    def load_dialect_impl(self, dialect):
        if dialect.name == 'sqlite':
            return dialect.type_descriptor(types.CHAR(36))
        else:
            return dialect.type_descriptor(types.CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'sqlite':
            return str(value)
        else:
            return str(value) if value else None

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'sqlite':
            if isinstance(value, str):
                try:
                    return PyUUID(value)
                except (ValueError, AttributeError):
                    return value
            return value
        else:
            return value


# Register ARRAY type for SQLite
import json


class JSONEncodedArray(types.TypeDecorator):
    """Platform-independent ARRAY type.

    Uses JSON TEXT in SQLite, storing arrays as JSON strings.
    """
    impl = types.TEXT
    cache_ok = True

    def __init__(self, item_type=None):
        """Initialize ARRAY type.

        Args:
            item_type: Ignored, for compatibility with PostgreSQL ARRAY
        """
        super().__init__()
        self.item_type = item_type

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, list):
            return json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is None:
            return []
        if isinstance(value, str):
            try:
                return json.loads(value)
            except (ValueError, TypeError):
                return []
        return value if value is not None else []


# Monkey patch PostgreSQL types with SQLite-compatible versions before importing models
_original_uuid = postgresql.UUID
_original_array = postgresql.ARRAY
postgresql.UUID = GUID
postgresql.ARRAY = JSONEncodedArray

# Now import models after patching
from app.database import Base
from app.models.tender import Tender
from app.models.company import Company
from app.models.user import User
from app.models.alert import Alert

# Restore original types after import
postgresql.UUID = _original_uuid
postgresql.ARRAY = _original_array


@pytest.fixture(scope="function")
def test_db():
    """
    Create an in-memory SQLite database for testing.

    Uses custom GUID type to handle PostgreSQL UUID in SQLite.
    """
    # Create in-memory database
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create tables (in order due to foreign keys)
    Company.__table__.create(bind=engine, checkfirst=True)
    User.__table__.create(bind=engine, checkfirst=True)
    Tender.__table__.create(bind=engine, checkfirst=True)
    Alert.__table__.create(bind=engine, checkfirst=True)

    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()

    yield db

    # Cleanup (drop in reverse order due to foreign keys)
    db.close()
    Alert.__table__.drop(bind=engine, checkfirst=True)
    Tender.__table__.drop(bind=engine, checkfirst=True)
    User.__table__.drop(bind=engine, checkfirst=True)
    Company.__table__.drop(bind=engine, checkfirst=True)


@pytest.fixture(scope="session")
def sample_csv_path():
    """
    Return path to sample CSV fixture file.
    """
    return Path(__file__).parent / "fixtures" / "sample_tenders.csv"


@pytest.fixture(scope="function")
def temp_csv_file(tmp_path):
    """
    Create a temporary CSV file for testing.
    """
    csv_path = tmp_path / "test_tenders.csv"
    csv_content = """URL,Date,Title,Company,Predicted_Category,Description
https://test.com/t1,2024-01-15,Test Tender 1,Test Company,IT & Technology,Test description 1
https://test.com/t2,2024-01-16,Test Tender 2,Test Company 2,Construction & Infrastructure,Test description 2
"""
    csv_path.write_text(csv_content)
    return csv_path
