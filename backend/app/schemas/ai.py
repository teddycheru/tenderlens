"""
AI-related Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional


class AIProcessRequest(BaseModel):
    """Request schema for AI processing."""
    tender_id: str = Field(..., description="Tender UUID to process")
    force_reprocess: bool = Field(default=False, description="Force reprocessing even if cached")
    doc_url: Optional[str] = Field(None, description="Optional document URL to process")


class AIProcessResponse(BaseModel):
    """Response schema for AI processing."""
    tender_id: str
    summary: Optional[str] = None
    entities: Optional[Dict] = None
    quick_scan: Optional[str] = None
    task_id: Optional[str] = Field(None, description="Celery task ID for async processing")
    cached: bool = Field(default=False, description="Whether result was from cache")
    processing_time_ms: int = Field(default=0, description="Processing time in milliseconds")


class QuickScanRequest(BaseModel):
    """Request schema for quick scan generation."""
    title: str = Field(..., description="Tender title")
    description: str = Field(..., description="Tender description")


class QuickScanResponse(BaseModel):
    """Response schema for quick scan."""
    quick_scan: str


class EntityExtractionResponse(BaseModel):
    """Response schema for extracted entities."""
    deadline: Optional[str] = Field(None, description="Deadline date (ISO format)")
    budget: Optional[str] = Field(None, description="Budget/value with currency")
    requirements: List[str] = Field(default_factory=list, description="Key requirements")
    qualifications: List[str] = Field(default_factory=list, description="Qualifications needed")
    organizations: List[str] = Field(default_factory=list, description="Mentioned organizations")
    locations: List[str] = Field(default_factory=list, description="Mentioned locations")
    contact_info: Optional[Dict] = Field(None, description="Contact information (email, phone)")


class AIStatusResponse(BaseModel):
    """Response schema for AI processing status."""
    tender_id: str
    ai_processed: bool
    ai_processed_at: Optional[str] = None
    has_summary: bool
    has_entities: bool
    word_count: Optional[int] = None


class BatchProcessRequest(BaseModel):
    """Request schema for batch processing."""
    tender_ids: List[str] = Field(..., description="List of tender UUIDs to process")


class BatchProcessResponse(BaseModel):
    """Response schema for batch processing."""
    total: int = Field(..., description="Total number of tenders queued")
    task_ids: List[str] = Field(..., description="List of Celery task IDs")
    status: str = Field(default="queued", description="Batch processing status")
