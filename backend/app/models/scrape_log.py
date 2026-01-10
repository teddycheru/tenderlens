# backend/app/models/scrape_log.py
"""
Track scraping runs and pipeline metrics.
"""

from sqlalchemy import Column, Integer, String, DateTime, JSON, Float
from sqlalchemy.sql import func
from app.database import Base


class ScrapeLog(Base):
    """
    Log of scraping runs with pipeline performance metrics.
    """
    __tablename__ = "scrape_logs"

    id = Column(Integer, primary_key=True, index=True)

    # Basic info
    source = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False, index=True)  # "success", "failed", "partial"

    # Basic metrics
    tenders_found = Column(Integer, default=0)
    tenders_new = Column(Integer, default=0)
    tenders_updated = Column(Integer, default=0)

    # Pipeline metrics
    tenders_validated = Column(Integer, default=0)
    tenders_validation_failed = Column(Integer, default=0)
    tenders_duplicate = Column(Integer, default=0)
    tenders_transformed = Column(Integer, default=0)
    tenders_loaded = Column(Integer, default=0)

    # Performance metrics
    extraction_time_seconds = Column(Float, nullable=True)
    validation_time_seconds = Column(Float, nullable=True)
    transformation_time_seconds = Column(Float, nullable=True)
    deduplication_time_seconds = Column(Float, nullable=True)
    loading_time_seconds = Column(Float, nullable=True)
    total_pipeline_time_seconds = Column(Float, nullable=True)

    # Data quality metrics
    data_quality_score = Column(Float, nullable=True)
    quality_metrics = Column(JSON, nullable=True)

    # Error tracking
    errors = Column(JSON, nullable=True)
    extra_metadata = Column(JSON, nullable=True)

    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    def duration_seconds(self):
        if self.completed_at and self.started_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    def __repr__(self):
        return f"<ScrapeLog(id={self.id}, source={self.source}, status={self.status})>"
