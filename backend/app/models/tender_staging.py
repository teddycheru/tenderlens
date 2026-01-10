# backend/app/models/tender_staging.py
"""
Staging table for raw scraped tender data before validation.
All scraped data lands here first before being processed into production.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Boolean, Float
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.sql import func
from app.database import Base


class TenderStaging(Base):
    """
    Temporary staging table for raw scraped data.
    Data remains here until validated and moved to production.
    """
    __tablename__ = "tender_staging"

    id = Column(Integer, primary_key=True, index=True)

    # Source information
    source_id = Column(String, nullable=False, index=True)  # e.g., "ministry_finance_et"
    source_name = Column(String, nullable=False)
    source_url = Column(String, nullable=True)              # Original page URL
    scrape_run_id = Column(Integer, nullable=True, index=True)  # Link to scrape_log

    # Raw scraped data (as-is, minimal processing)
    raw_data = Column(JSON, nullable=False)

    # Processing status
    status = Column(String, default="pending", nullable=False, index=True)
    # Status values: "pending", "validated", "transformed", "loaded", "failed", "duplicate"

    # Validation & transformation tracking
    validation_errors = Column(JSON, nullable=True)      # List of validation errors
    transformation_errors = Column(JSON, nullable=True)  # Transformation errors

    # Deduplication tracking
    is_duplicate = Column(Boolean, default=False, index=True)
    duplicate_of_tender_id = Column(PG_UUID(as_uuid=True), nullable=True)
    duplicate_reason = Column(String, nullable=True)
    duplicate_similarity_score = Column(Float, nullable=True)

    # Data quality
    quality_score = Column(Float, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    validated_at = Column(DateTime(timezone=True), nullable=True)
    transformed_at = Column(DateTime(timezone=True), nullable=True)
    processed_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<TenderStaging(id={self.id}, source={self.source_id}, status={self.status})>"
