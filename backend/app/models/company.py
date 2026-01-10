"""
Company model - Business/organization management.
"""

from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base


class Company(Base):
    """
    Company model for business profiles and preferences.
    """
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, index=True, nullable=False)
    industry = Column(String, nullable=True)
    description = Column(Text, nullable=True)

    # JSON field for flexible company preferences
    # Example: {"keywords": ["software", "IT"], "locations": ["Ethiopia", "Kenya"]}
    preferences = Column(JSON, default={}, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    users = relationship("User", back_populates="company", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="company", cascade="all, delete-orphan")
    tender_profile = relationship("CompanyTenderProfile", back_populates="company", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Company(id={self.id}, name={self.name}, industry={self.industry})>"
