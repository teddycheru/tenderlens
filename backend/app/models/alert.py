"""
Alert model - User-defined notification rules for matching tenders.
"""

from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base


# Association table for many-to-many relationship between Tender and Alert
TenderAlert = Table(
    "tender_alerts",
    Base.metadata,
    Column("tender_id", UUID(as_uuid=True), ForeignKey("tenders.id"), primary_key=True),
    Column("alert_id", UUID(as_uuid=True), ForeignKey("alerts.id"), primary_key=True),
    Column("matched_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
)


class Alert(Base):
    """
    Alert model for personalized tender notifications.
    Users can define rules (keywords, location, budget) to match relevant tenders.
    """
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False)

    # Foreign key to Company
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    # Alert filters
    keywords = Column(ARRAY(String), nullable=False, default=[])
    location_filter = Column(String, nullable=True)
    category_filter = Column(String, nullable=True)
    min_budget = Column(Float, nullable=True)
    max_budget = Column(Float, nullable=True)

    # Alert status
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    company = relationship("Company", back_populates="alerts")

    def __repr__(self):
        return f"<Alert(id={self.id}, name={self.name}, company_id={self.company_id}, is_active={self.is_active})>"
