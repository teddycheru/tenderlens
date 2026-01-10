"""
Pydantic schemas for company-related requests and responses.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime


# ==================== Request Schemas ====================

class CompanyCreate(BaseModel):
    """
    Schema for company creation request.
    """
    name: str = Field(..., min_length=2, max_length=200, description="Company name")
    industry: Optional[str] = Field(None, max_length=100, description="Industry sector")
    description: Optional[str] = Field(None, max_length=1000, description="Company description")
    preferences: Dict[str, Any] = Field(default_factory=dict, description="Company preferences (keywords, locations, etc.)")


class CompanyUpdate(BaseModel):
    """
    Schema for company update request.
    """
    name: Optional[str] = Field(None, min_length=2, max_length=200, description="Company name")
    industry: Optional[str] = Field(None, max_length=100, description="Industry sector")
    description: Optional[str] = Field(None, max_length=1000, description="Company description")
    preferences: Optional[Dict[str, Any]] = Field(None, description="Company preferences")


# ==================== Response Schemas ====================

class CompanyResponse(BaseModel):
    """
    Schema for company response.
    """
    id: UUID
    name: str
    industry: Optional[str]
    description: Optional[str]
    preferences: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
