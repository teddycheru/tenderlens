"""
Company Tender Profile Schemas

Pydantic schemas for company profile management and onboarding.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict
from datetime import datetime
from uuid import UUID
from decimal import Decimal


# ==================== Base Schemas ====================

class CompanyProfileBase(BaseModel):
    """Base schema with common profile fields"""
    # Tier 1: Critical fields (required during Step 1)
    primary_sector: str = Field(..., min_length=1, max_length=100, description="Primary business sector for identity")
    active_sectors: List[str] = Field(..., min_items=1, max_items=5, description="Active work sectors (max 5)")
    sub_sectors: List[str] = Field(default_factory=list, description="Specializations within sectors")
    preferred_regions: List[str] = Field(..., min_items=1, max_items=5, description="Preferred regions")
    keywords: List[str] = Field(..., min_items=3, max_items=10, description="Core capabilities keywords")

    # Tier 2: Important fields (optional in Step 2)
    company_size: Optional[str] = Field(None, description="Company size: startup, small, medium, large")
    years_in_operation: Optional[str] = Field(None, description="Years in operation: <1, 1-3, 3-5, 5-10, 10+")
    certifications: Optional[List[str]] = Field(default_factory=list, description="Certifications and qualifications")
    budget_min: Optional[Decimal] = Field(None, ge=0, description="Minimum tender budget")
    budget_max: Optional[Decimal] = Field(None, ge=0, description="Maximum tender budget capacity")
    budget_currency: str = Field(default="ETB", max_length=3, description="Budget currency code")

    @field_validator('active_sectors')
    @classmethod
    def validate_active_sectors(cls, v):
        if len(v) > 5:
            raise ValueError("Maximum 5 active sectors allowed")
        if len(v) < 1:
            raise ValueError("At least 1 active sector required")
        return v

    @field_validator('keywords')
    @classmethod
    def validate_keywords(cls, v):
        if len(v) < 3:
            raise ValueError("Minimum 3 keywords required")
        if len(v) > 10:
            raise ValueError("Maximum 10 keywords allowed")
        return v

    @field_validator('company_size')
    @classmethod
    def validate_company_size(cls, v):
        if v and v not in ['startup', 'small', 'medium', 'large']:
            raise ValueError("Company size must be: startup, small, medium, or large")
        return v

    @field_validator('years_in_operation')
    @classmethod
    def validate_years(cls, v):
        if v and v not in ['<1', '1-3', '3-5', '5-10', '10+']:
            raise ValueError("Years must be: <1, 1-3, 3-5, 5-10, or 10+")
        return v

    @field_validator('budget_max')
    @classmethod
    def validate_budget_range(cls, v, info):
        budget_min = info.data.get('budget_min')
        if v and budget_min and v < budget_min:
            raise ValueError("Budget max must be greater than budget min")
        return v


# ==================== Create Schemas ====================

class CompanyProfileCreate(CompanyProfileBase):
    """Schema for creating a new company profile (onboarding)"""
    pass


class CompanyProfileCreateStep1(BaseModel):
    """Schema for Step 1 of onboarding (critical fields only)"""
    primary_sector: str = Field(..., min_length=1, max_length=100)
    active_sectors: List[str] = Field(..., min_items=1, max_items=5)
    sub_sectors: List[str] = Field(default_factory=list)
    preferred_regions: List[str] = Field(..., min_items=1, max_items=5)
    keywords: List[str] = Field(..., min_items=3, max_items=10)


class CompanyProfileCreateStep2(BaseModel):
    """Schema for Step 2 of onboarding (optional refinement)"""
    company_size: Optional[str] = None
    years_in_operation: Optional[str] = None
    certifications: Optional[List[str]] = Field(default_factory=list)
    budget_min: Optional[Decimal] = Field(None, ge=0)
    budget_max: Optional[Decimal] = Field(None, ge=0)
    budget_currency: str = Field(default="ETB", max_length=3)


# ==================== Update Schemas ====================

class CompanyProfileUpdate(BaseModel):
    """Schema for updating an existing company profile"""
    # All fields optional for partial updates
    primary_sector: Optional[str] = Field(None, min_length=1, max_length=100)
    active_sectors: Optional[List[str]] = Field(None, min_items=1, max_items=5)
    sub_sectors: Optional[List[str]] = None
    preferred_regions: Optional[List[str]] = Field(None, min_items=1, max_items=5)
    keywords: Optional[List[str]] = Field(None, min_items=3, max_items=10)
    company_size: Optional[str] = None
    years_in_operation: Optional[str] = None
    certifications: Optional[List[str]] = None
    budget_min: Optional[Decimal] = Field(None, ge=0)
    budget_max: Optional[Decimal] = Field(None, ge=0)
    budget_currency: Optional[str] = Field(None, max_length=3)

    # Allow updating learned preferences manually
    discovered_interests: Optional[List[str]] = None
    preferred_sources: Optional[List[str]] = None
    preferred_languages: Optional[List[str]] = None
    min_deadline_days: Optional[int] = Field(None, ge=0)

    # Allow updating matching settings
    min_match_threshold: Optional[Decimal] = Field(None, ge=0, le=100)
    scoring_weights: Optional[Dict[str, float]] = None


# ==================== Response Schemas ====================

class CompanyProfileResponse(CompanyProfileBase):
    """Schema for company profile responses"""
    id: UUID
    company_id: UUID

    # Tier 3: Learned preferences (read-only in response)
    discovered_interests: List[str] = Field(default_factory=list)
    preferred_sources: List[str] = Field(default_factory=list)
    preferred_languages: List[str] = Field(default=['en'])
    min_deadline_days: Optional[int] = None

    # Matching configuration
    min_match_threshold: Decimal = Field(default=Decimal('40.0'))
    scoring_weights: Dict[str, float] = Field(
        default_factory=lambda: {
            "active_sectors": 30,
            "sub_sectors": 20,
            "keywords": 25,
            "region": 10,
            "budget": 5,
            "certifications": 5,
            "semantic": 5
        }
    )

    # Metadata
    profile_completed: bool = Field(default=False)
    onboarding_step: int = Field(default=0)
    interaction_count: int = Field(default=0)
    last_interaction_at: Optional[datetime] = None
    embedding_updated_at: Optional[datetime] = None

    # Timestamps
    created_at: datetime
    updated_at: datetime

    # Computed properties
    completion_percentage: int = Field(default=0, description="Profile completion %")
    is_tier1_complete: bool = Field(default=False, description="Critical fields complete")
    is_tier2_complete: bool = Field(default=False, description="Important fields complete")

    class Config:
        from_attributes = True


class CompanyProfileSummary(BaseModel):
    """Lightweight profile summary for lists"""
    id: UUID
    company_id: UUID
    primary_sector: str
    active_sectors: List[str]
    profile_completed: bool
    completion_percentage: int
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Options Schema ====================

class ProfileOptions(BaseModel):
    """Available options for profile fields (for dropdowns)"""
    sectors: List[str] = Field(..., description="Available business sectors")
    regions: List[str] = Field(..., description="Available Ethiopian regions")
    certifications: List[str] = Field(..., description="Common certifications")
    company_sizes: List[str] = Field(
        default=['startup', 'small', 'medium', 'large'],
        description="Company size options"
    )
    years_options: List[str] = Field(
        default=['<1', '1-3', '3-5', '5-10', '10+'],
        description="Years in operation options"
    )
    keyword_suggestions: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Keyword suggestions by sector"
    )


# ==================== Interaction Schemas ====================

class UserInteractionCreate(BaseModel):
    """Schema for creating a user interaction"""
    tender_id: UUID
    interaction_type: str = Field(..., description="view, save, apply, dismiss, rate_positive, rate_negative")
    time_spent_seconds: Optional[int] = Field(None, ge=0)
    feedback_reason: Optional[str] = Field(None, max_length=500)

    @field_validator('interaction_type')
    @classmethod
    def validate_interaction_type(cls, v):
        valid_types = ['view', 'save', 'apply', 'dismiss', 'rate_positive', 'rate_negative']
        if v not in valid_types:
            raise ValueError(f"Interaction type must be one of: {', '.join(valid_types)}")
        return v


class UserInteractionResponse(BaseModel):
    """Schema for user interaction responses"""
    id: UUID
    user_id: UUID
    tender_id: UUID
    interaction_type: str
    interaction_weight: Decimal
    time_spent_seconds: Optional[int] = None
    match_score_at_time: Optional[Decimal] = None
    tender_category: Optional[str] = None
    tender_region: Optional[str] = None
    tender_budget: Optional[Decimal] = None
    feedback_reason: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class InteractionStats(BaseModel):
    """Statistics about user interactions"""
    total_interactions: int
    views_count: int
    saves_count: int
    applies_count: int
    dismisses_count: int
    positive_rates_count: int
    negative_rates_count: int
    avg_time_spent: Optional[float] = None
    most_engaged_categories: List[str] = Field(default_factory=list)
    most_engaged_regions: List[str] = Field(default_factory=list)


# ==================== Behavioral Learning Schemas ====================

class LearnedInsight(BaseModel):
    """Schema for behavioral learning insights"""
    insight_type: str = Field(..., description="discovered_interest, keyword_suggestion, budget_adjustment, etc.")
    message: str = Field(..., description="User-friendly message")
    suggested_value: str | List[str] | Dict = Field(..., description="Suggested value to add/update")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score 0-1")
    interaction_count: int = Field(..., description="Number of interactions analyzed")


class ProfileRecommendations(BaseModel):
    """Recommendations for profile improvement"""
    insights: List[LearnedInsight]
    completion_tips: List[str] = Field(default_factory=list, description="Tips to complete profile")
    estimated_improvement: Optional[str] = Field(None, description="E.g., '15 more tenders'")
