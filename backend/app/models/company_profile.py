"""
Company Tender Profile Model

Stores comprehensive business profile data for tender matching and recommendations.
Supports multi-sector Ethiopian business model with progressive profiling.
"""

from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime, ForeignKey,
    DECIMAL, ARRAY, Text
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
import uuid
from datetime import datetime

from app.database import Base


class CompanyTenderProfile(Base):
    """
    Company tender profile for personalized recommendations.

    Tier 1 (Critical): Data collected during onboarding
    Tier 2 (Important): Optional data for improved matching
    Tier 3 (Learned): Data discovered through user behavior
    """
    __tablename__ = "company_tender_profiles"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign Key
    company_id = Column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )

    # Tier 1: Critical Fields (Required during onboarding)
    primary_sector = Column(String(100), nullable=False, index=True)  # Identity/branding
    active_sectors = Column(ARRAY(Text), nullable=False)  # Actual work sectors (max 5)
    sub_sectors = Column(ARRAY(Text), nullable=False)  # Specializations
    preferred_regions = Column(ARRAY(Text), nullable=False)  # Geographic preferences
    keywords = Column(ARRAY(Text), nullable=False)  # Core capabilities (3-10 keywords)

    # Tier 2: Important Fields (Optional, collected in Step 2)
    company_size = Column(String(20))  # 'startup', 'small', 'medium', 'large'
    years_in_operation = Column(String(10))  # '<1', '1-3', '3-5', '5-10', '10+'
    certifications = Column(ARRAY(Text))  # ISO 9001, VAT Registered, etc.
    budget_min = Column(DECIMAL(15, 2))  # Minimum budget in local currency
    budget_max = Column(DECIMAL(15, 2))  # Maximum budget capacity
    budget_currency = Column(String(3), default='ETB')  # Currency code

    # Tier 3: Learned Preferences (Implicit, updated through behavioral learning)
    discovered_interests = Column(
        ARRAY(Text),
        default=list
    )  # New sectors discovered through interactions
    preferred_sources = Column(ARRAY(Text), default=list)  # High-engagement sources
    preferred_languages = Column(ARRAY(Text), default=['en'])  # Detected from usage
    min_deadline_days = Column(Integer)  # Learned from dismiss patterns

    # Matching Configuration
    min_match_threshold = Column(
        DECIMAL(3, 1),
        default=40.0
    )  # Minimum match score to show (0-100)

    scoring_weights = Column(
        JSONB,
        default={
            "active_sectors": 30,
            "sub_sectors": 20,
            "keywords": 25,
            "region": 10,
            "budget": 5,
            "certifications": 5,
            "semantic": 5
        }
    )  # Customizable scoring weights

    # Vector Embeddings (for semantic similarity)
    profile_embedding = Column(Vector(384))  # Generated from keywords + sectors
    embedding_updated_at = Column(DateTime(timezone=True))

    # Metadata
    profile_completed = Column(Boolean, default=False)  # Step 2 completed
    onboarding_step = Column(Integer, default=0)  # Current wizard step (0-2)
    interaction_count = Column(Integer, default=0)  # Total interactions logged
    last_interaction_at = Column(DateTime(timezone=True))  # Last user interaction

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    company = relationship("Company", back_populates="tender_profile")

    def __repr__(self):
        return f"<CompanyTenderProfile(company_id={self.company_id}, primary_sector={self.primary_sector})>"

    @property
    def is_tier1_complete(self) -> bool:
        """Check if Tier 1 (critical) fields are filled"""
        return bool(
            self.primary_sector and
            self.active_sectors and len(self.active_sectors) > 0 and
            self.preferred_regions and len(self.preferred_regions) > 0 and
            self.keywords and len(self.keywords) >= 3
        )

    @property
    def is_tier2_complete(self) -> bool:
        """Check if Tier 2 (important) fields are filled"""
        return bool(
            self.company_size and
            self.years_in_operation and
            self.certifications
        )

    @property
    def completion_percentage(self) -> int:
        """Calculate profile completion percentage"""
        total_fields = 11  # Critical + Important fields
        completed_fields = 0

        # Tier 1 fields (5 fields)
        if self.primary_sector:
            completed_fields += 1
        if self.active_sectors and len(self.active_sectors) > 0:
            completed_fields += 1
        if self.sub_sectors and len(self.sub_sectors) > 0:
            completed_fields += 1
        if self.preferred_regions and len(self.preferred_regions) > 0:
            completed_fields += 1
        if self.keywords and len(self.keywords) >= 3:
            completed_fields += 1

        # Tier 2 fields (6 fields)
        if self.company_size:
            completed_fields += 1
        if self.years_in_operation:
            completed_fields += 1
        if self.certifications and len(self.certifications) > 0:
            completed_fields += 1
        if self.budget_min is not None:
            completed_fields += 1
        if self.budget_max is not None:
            completed_fields += 1
        if self.budget_currency:
            completed_fields += 1

        return int((completed_fields / total_fields) * 100)

    def update_interaction_stats(self):
        """Update interaction metadata"""
        self.interaction_count += 1
        self.last_interaction_at = datetime.utcnow()
