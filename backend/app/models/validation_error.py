# backend/app/models/validation_error.py
"""
Track all validation errors for monitoring and debugging.
Helps identify data quality issues and scraper problems.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class ValidationError(Base):
    """
    Log of all validation errors encountered during pipeline processing.
    Used for debugging and improving scrapers/validation rules.
    """
    __tablename__ = "validation_errors"

    id = Column(Integer, primary_key=True, index=True)

    # Reference to staging record
    staging_id = Column(Integer, ForeignKey("tender_staging.id"), nullable=True, index=True)
    scrape_run_id = Column(Integer, nullable=True, index=True)

    # Error details
    error_type = Column(String, nullable=False, index=True)
    # Error types: "required_field", "invalid_format", "out_of_range",
    # "business_rule", "type_error", "constraint_violation"

    field_name = Column(String, nullable=True)
    error_message = Column(Text, nullable=False)
    raw_value = Column(String, nullable=True)

    # Severity level
    severity = Column(String, default="error", nullable=False, index=True)
    # Severity levels: "warning", "error", "critical"

    # Context for debugging
    context = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    def __repr__(self):
        return f"<ValidationError(id={self.id}, type={self.error_type}, field={self.field_name})>"
