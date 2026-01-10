"""
Pydantic schemas for alert-related requests and responses.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime


# ==================== Request Schemas ====================

class AlertCreate(BaseModel):
    """
    Schema for alert creation request.
    """
    name: str = Field(..., min_length=3, max_length=200, description="Alert name")
    keywords: List[str] = Field(default=[], description="Keywords to match in tender title/description")
    location_filter: Optional[str] = Field(None, max_length=100, description="Location/region filter")
    category_filter: Optional[str] = Field(None, max_length=100, description="Category filter")
    min_budget: Optional[float] = Field(None, ge=0, description="Minimum budget filter")
    max_budget: Optional[float] = Field(None, ge=0, description="Maximum budget filter")
    is_active: bool = Field(default=True, description="Whether the alert is active")


class AlertUpdate(BaseModel):
    """
    Schema for alert update request.
    """
    name: Optional[str] = Field(None, min_length=3, max_length=200, description="Alert name")
    keywords: Optional[List[str]] = Field(None, description="Keywords to match in tender title/description")
    location_filter: Optional[str] = Field(None, max_length=100, description="Location/region filter")
    category_filter: Optional[str] = Field(None, max_length=100, description="Category filter")
    min_budget: Optional[float] = Field(None, ge=0, description="Minimum budget filter")
    max_budget: Optional[float] = Field(None, ge=0, description="Maximum budget filter")
    is_active: Optional[bool] = Field(None, description="Whether the alert is active")


# ==================== Response Schemas ====================

class AlertResponse(BaseModel):
    """
    Schema for alert response.
    """
    id: UUID
    name: str
    company_id: UUID
    keywords: List[str]
    location_filter: Optional[str]
    category_filter: Optional[str]
    min_budget: Optional[float]
    max_budget: Optional[float]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AlertListResponse(BaseModel):
    """
    Schema for paginated alert list response.
    """
    total: int = Field(..., description="Total number of alerts")
    items: List[AlertResponse] = Field(..., description="List of alerts")
    skip: int = Field(..., description="Number of records skipped")
    limit: int = Field(..., description="Number of records returned")
