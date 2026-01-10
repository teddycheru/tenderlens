"""
User Interaction Model

Tracks all user interactions with tenders for behavioral learning and
recommendation improvement.
"""

from sqlalchemy import (
    Column, String, Integer, ForeignKey, DateTime,
    Text, DECIMAL, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from typing import Literal

from app.database import Base


# Interaction type constants
INTERACTION_VIEW = "view"
INTERACTION_SAVE = "save"
INTERACTION_APPLY = "apply"
INTERACTION_DISMISS = "dismiss"
INTERACTION_RATE_POSITIVE = "rate_positive"
INTERACTION_RATE_NEGATIVE = "rate_negative"

# Interaction weights for recommendation scoring
INTERACTION_WEIGHTS = {
    INTERACTION_VIEW: 0.1,
    INTERACTION_SAVE: 0.5,
    INTERACTION_APPLY: 1.0,
    INTERACTION_DISMISS: -0.3,
    INTERACTION_RATE_POSITIVE: 0.8,
    INTERACTION_RATE_NEGATIVE: -0.8,
}


class UserInteraction(Base):
    """
    Track user interactions with tenders for behavioral learning.

    Interaction Types:
    - view: User viewed tender details (weight: 0.1)
    - save: User bookmarked/saved tender (weight: 0.5)
    - apply: User initiated application (weight: 1.0) - strongest signal
    - dismiss: User marked "not interested" (weight: -0.3)
    - rate_positive: User gave thumbs up (weight: 0.8)
    - rate_negative: User gave thumbs down (weight: -0.8)
    """
    __tablename__ = "user_interactions"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign Keys
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    tender_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tenders.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Interaction Data
    interaction_type = Column(
        String(20),
        nullable=False,
        index=True
    )  # view, save, apply, dismiss, rate_positive, rate_negative

    interaction_weight = Column(
        DECIMAL(3, 2),
        nullable=False
    )  # Numeric weight for scoring

    # Context at Time of Interaction
    time_spent_seconds = Column(Integer)  # How long user viewed the tender
    match_score_at_time = Column(DECIMAL(5, 2))  # What was the match score shown

    # Tender Snapshot (for analysis if tender is deleted)
    tender_category = Column(String(100))
    tender_region = Column(String(100))
    tender_budget = Column(DECIMAL(15, 2))

    # Feedback
    feedback_reason = Column(Text)  # Optional: "too expensive", "wrong region", etc.

    # Timestamp
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User")
    tender = relationship("Tender")

    # Unique constraint: one interaction type per user-tender pair
    __table_args__ = (
        UniqueConstraint(
            'user_id', 'tender_id', 'interaction_type',
            name='unique_user_tender_interaction'
        ),
    )

    def __repr__(self):
        return (
            f"<UserInteraction(user_id={self.user_id}, tender_id={self.tender_id}, "
            f"type={self.interaction_type}, weight={self.interaction_weight})>"
        )

    @classmethod
    def get_weight_for_type(cls, interaction_type: str) -> float:
        """Get the weight for a given interaction type"""
        return INTERACTION_WEIGHTS.get(interaction_type, 0.0)

    @property
    def is_positive(self) -> bool:
        """Check if this is a positive interaction"""
        return self.interaction_weight > 0

    @property
    def is_negative(self) -> bool:
        """Check if this is a negative interaction"""
        return self.interaction_weight < 0

    def to_dict(self) -> dict:
        """Convert to dictionary for analytics"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "tender_id": str(self.tender_id),
            "interaction_type": self.interaction_type,
            "interaction_weight": float(self.interaction_weight),
            "time_spent_seconds": self.time_spent_seconds,
            "match_score_at_time": float(self.match_score_at_time) if self.match_score_at_time else None,
            "tender_category": self.tender_category,
            "tender_region": self.tender_region,
            "tender_budget": float(self.tender_budget) if self.tender_budget else None,
            "feedback_reason": self.feedback_reason,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
