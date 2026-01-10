"""
User preferences model for storing notification and application preferences.
"""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from app.database import Base


class UserPreferences(Base):
    """
    User preferences model for storing per-user settings.

    This model stores both notification preferences and application preferences
    for each user. If preferences don't exist for a user, defaults will be used.
    """
    __tablename__ = "user_preferences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)

    # Notification preferences
    email_notifications = Column(Boolean, default=True, nullable=False)
    new_tender_alerts = Column(Boolean, default=True, nullable=False)
    deadline_reminders = Column(Boolean, default=True, nullable=False)
    weekly_digest = Column(Boolean, default=False, nullable=False)

    # Application preferences
    language = Column(String(10), default="en-US", nullable=False)
    timezone = Column(String(50), default="UTC", nullable=False)
    date_format = Column(String(20), default="MM/DD/YYYY", nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = relationship("User", back_populates="preferences")

    def __repr__(self):
        return f"<UserPreferences(user_id={self.user_id}, email_notifications={self.email_notifications})>"
