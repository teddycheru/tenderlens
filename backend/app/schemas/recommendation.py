"""
Recommendation schemas for API requests and responses.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from app.schemas.tender import TenderResponse


class MatchReason(BaseModel):
    """Reason for a tender recommendation match."""
    type: str = Field(..., description="Type of match (sector_match, keyword_match, etc.)")
    message: str = Field(..., description="Human-readable explanation")
    weight: float = Field(..., description="Score contribution from this reason")


class TenderRecommendation(BaseModel):
    """A tender recommendation with match score and reasons."""
    tender: TenderResponse
    match_score: float = Field(..., ge=0, le=100, description="Overall match score (0-100)")
    match_reasons: List[MatchReason] = Field(..., description="Why this tender was recommended")
    semantic_similarity: float = Field(..., ge=0, le=1, description="Vector similarity (0-1)")
    days_until_deadline: int = Field(..., description="Days remaining until deadline")

    class Config:
        from_attributes = True


class RecommendationResponse(BaseModel):
    """Response containing personalized tender recommendations."""
    recommendations: List[TenderRecommendation]
    total_count: int
    profile_id: str
    profile_completion: float = Field(..., description="Profile completion percentage (0-100)")
    generated_at: datetime


class RecommendationFeedback(BaseModel):
    """User feedback on recommendation quality."""
    interaction_type: str = Field(
        ...,
        description="Type of interaction: relevant, not_relevant, applied, saved, dismissed"
    )
    reason: Optional[str] = Field(
        None,
        description="Optional reason for feedback (e.g., 'not in my region', 'wrong sector')"
    )
    match_score: Optional[float] = Field(
        None,
        description="The match score that was shown to the user"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "interaction_type": "not_relevant",
                "reason": "Budget too high for our company",
                "match_score": 75.5
            }
        }


class SimilarTenderResponse(BaseModel):
    """Response for similar tenders."""
    tender: TenderResponse
    similarity_score: float = Field(..., ge=0, le=1, description="Similarity to reference tender")
    days_until_deadline: int

    class Config:
        from_attributes = True
