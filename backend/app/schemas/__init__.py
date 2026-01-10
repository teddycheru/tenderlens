"""
Pydantic schemas package for request/response validation.
"""

from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserLogin,
    Token,
    TokenPayload,
    RefreshTokenRequest,
    Message
)

from app.schemas.company import (
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse
)

from app.schemas.tender import (
    TenderCreate,
    TenderUpdate,
    TenderResponse,
    TenderFilter,
    TenderListResponse,
    TenderStatus
)

from app.schemas.alert import (
    AlertCreate,
    AlertUpdate,
    AlertResponse,
    AlertListResponse
)

from app.schemas.company_profile import (
    CompanyProfileCreate,
    CompanyProfileCreateStep1,
    CompanyProfileCreateStep2,
    CompanyProfileUpdate,
    CompanyProfileResponse,
    CompanyProfileSummary,
    ProfileOptions,
    UserInteractionCreate,
    UserInteractionResponse,
    InteractionStats,
    LearnedInsight,
    ProfileRecommendations
)

__all__ = [
    # User schemas
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserLogin",
    "Token",
    "TokenPayload",
    "RefreshTokenRequest",
    "Message",
    # Company schemas
    "CompanyCreate",
    "CompanyUpdate",
    "CompanyResponse",
    # Tender schemas
    "TenderCreate",
    "TenderUpdate",
    "TenderResponse",
    "TenderFilter",
    "TenderListResponse",
    "TenderStatus",
    # Alert schemas
    "AlertCreate",
    "AlertUpdate",
    "AlertResponse",
    "AlertListResponse",
    # Company Profile schemas
    "CompanyProfileCreate",
    "CompanyProfileCreateStep1",
    "CompanyProfileCreateStep2",
    "CompanyProfileUpdate",
    "CompanyProfileResponse",
    "CompanyProfileSummary",
    "ProfileOptions",
    # Interaction schemas
    "UserInteractionCreate",
    "UserInteractionResponse",
    "InteractionStats",
    "LearnedInsight",
    "ProfileRecommendations",
]
