"""
User preferences schemas for request/response validation.
"""

from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional


class UserPreferencesBase(BaseModel):
    """Base schema for user preferences."""
    email_notifications: bool = Field(default=True, description="Enable email notifications")
    new_tender_alerts: bool = Field(default=True, description="Receive alerts for new tenders")
    deadline_reminders: bool = Field(default=True, description="Receive deadline reminders")
    weekly_digest: bool = Field(default=False, description="Receive weekly summary digest")
    language: str = Field(default="en-US", max_length=10, description="User interface language")
    timezone: str = Field(default="UTC", max_length=50, description="User timezone")
    date_format: str = Field(default="MM/DD/YYYY", max_length=20, description="Preferred date format")


class UserPreferencesUpdate(BaseModel):
    """Schema for updating user preferences (all fields optional)."""
    email_notifications: Optional[bool] = None
    new_tender_alerts: Optional[bool] = None
    deadline_reminders: Optional[bool] = None
    weekly_digest: Optional[bool] = None
    language: Optional[str] = Field(None, max_length=10)
    timezone: Optional[str] = Field(None, max_length=50)
    date_format: Optional[str] = Field(None, max_length=20)

    class Config:
        from_attributes = True


class UserPreferencesResponse(UserPreferencesBase):
    """Schema for user preferences response."""
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
