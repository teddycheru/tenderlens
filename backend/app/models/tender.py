"""
Tender model - Business opportunity listings.
"""

from sqlalchemy import Column, String, Text, Date, DateTime, Enum, Float, ForeignKey, Boolean, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
import uuid
import enum

from app.database import Base


class TenderStatus(str, enum.Enum):
    """Enumeration for tender status."""
    DRAFT = "draft"
    PUBLISHED = "published"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class Tender(Base):
    """
    Tender model for business opportunities (tenders, RFPs, grants).
    """
    __tablename__ = "tenders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=False)

    # Tender metadata
    category = Column(String, nullable=True, index=True)  # e.g., "IT", "Construction", "Healthcare"
    region = Column(String, nullable=True, index=True)    # e.g., "Addis Ababa", "National"
    language = Column(String, default="en", nullable=True)  # Document language (e.g., "en", "am", "or")
    source = Column(String, nullable=True, index=True)    # e.g., "Ministry of Finance", "manual", "scraped"
    source_url = Column(String, unique=True, nullable=True, index=True)  # URL to original tender document
    tor_url = Column(String, nullable=True)  # URL to Terms of Reference or tender documents

    # Budget information
    budget = Column(Float, nullable=True)
    budget_currency = Column(String, default="ETB", nullable=True)

    # Important dates
    published_date = Column(Date, nullable=True, index=True)  # Date when tender was published
    deadline = Column(Date, nullable=True, index=True)        # Tender submission deadline

    # Status
    status = Column(Enum(TenderStatus), default=TenderStatus.PUBLISHED, nullable=False)

    # Pipeline support fields
    external_id = Column(String, unique=True, nullable=True, index=True)  # Hash for deduplication
    content_hash = Column(String, index=True, nullable=True)  # MD5 of description
    data_quality_score = Column(Float, default=100.0)  # Quality score (0-100)

    # Pipeline metadata
    scraped_at = Column(DateTime(timezone=True), nullable=True)
    last_verified_at = Column(DateTime(timezone=True), nullable=True)
    scrape_run_id = Column(ForeignKey("scrape_logs.id"), nullable=True)

    # AI Processing Fields (Phase 2)
    ai_summary = Column(Text, nullable=True)  # GPT-4 generated summary
    ai_processed = Column(Boolean, default=False, nullable=False)  # Processing flag
    ai_processed_at = Column(DateTime(timezone=True), nullable=True)  # When AI processing completed

    # Extracted Entities (JSON structure)
    extracted_entities = Column(JSON, nullable=True)
    # Example structure:
    # {
    #   "deadline": "2024-03-15",
    #   "budget": "5,000,000 ETB",
    #   "requirements": ["ISO certification", "5 years experience"],
    #   "qualifications": ["Licensed contractor", "VAT registered"],
    #   "organizations": ["Ethiopian Roads Authority"],
    #   "locations": ["Addis Ababa", "Dire Dawa"],
    #   "contact_info": {"email": "procurement@example.gov.et", "phone": "+251-11-1234567"}
    # }

    # Document Processing
    raw_text = Column(Text, nullable=True)  # Extracted text from PDF/DOC files
    word_count = Column(Integer, nullable=True)  # Document word count

    # Content Generation Fields (from offline LLM pipeline)
    clean_description = Column(Text, nullable=True)  # LLM-generated clean, well-formatted description
    highlights = Column(Text, nullable=True)  # LLM-generated key highlights/bullet points
    extracted_data = Column(JSON, nullable=True)  # Structured extraction: financial, contact, dates, requirements, specs, organization, addresses
    content_generated_at = Column(DateTime(timezone=True), nullable=True)  # When content was generated
    content_generation_errors = Column(JSON, nullable=True)  # Any errors during content generation

    # Recommendation System Fields
    recommendation_status = Column(String(20), default='active', nullable=True, index=True)  # 'active', 'expired', 'expired_saved', 'historical'
    content_embedding = Column(Vector(1024), nullable=True)  # 1024 for BGE-M3
    embedding_updated_at = Column(DateTime(timezone=True), nullable=True)  # Last embedding update timestamp

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<Tender(id={self.id}, title={self.title}, status={self.status})>"
