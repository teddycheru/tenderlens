# backend/app/models/duplicate_log.py
"""
Track duplicate detection for analysis, tuning, and manual review.
Helps optimize deduplication strategies and identify false positives.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.sql import func
from app.database import Base


class DuplicateLog(Base):
    """
    Log of detected duplicates for monitoring deduplication accuracy.
    Used to tune fuzzy matching thresholds and review edge cases.
    """
    __tablename__ = "duplicate_logs"

    id = Column(Integer, primary_key=True, index=True)

    # Duplicate detection info
    staging_id = Column(Integer, nullable=False, index=True)
    existing_tender_id = Column(PG_UUID(as_uuid=True), nullable=False, index=True)

    # Detection method
    detection_method = Column(String, nullable=False, index=True)
    # Methods: "hash_exact", "fuzzy_title", "url_match", "manual", "ml_model"

    # Matching metrics
    similarity_score = Column(Float, nullable=True)
    confidence = Column(Float, default=1.0)

    # What matched (detailed breakdown)
    match_details = Column(JSON, nullable=True)

    # Action taken
    action = Column(String, default="skipped", nullable=False)
    # Actions: "skipped", "merged", "updated", "flagged_for_review"

    # Manual review
    reviewed = Column(Boolean, default=False)
    review_notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    def __repr__(self):
        return f"<DuplicateLog(id={self.id}, method={self.detection_method}, score={self.similarity_score})>"
