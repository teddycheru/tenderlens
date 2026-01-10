"""
API v1 router aggregation.
"""

from fastapi import APIRouter
from app.api.v1 import (
    auth,
    users,
    companies,
    company_profiles,
    tenders,
    analytics,
    pipeline,
    alerts,
    preferences,
    ai,
    recommendations
)

# Create main API v1 router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(preferences.router, tags=["Preferences"])
api_router.include_router(companies.router, prefix="/companies", tags=["Companies"])
api_router.include_router(company_profiles.router, tags=["Company Profile"])
api_router.include_router(tenders.router, prefix="/tenders", tags=["Tenders"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
api_router.include_router(analytics.router, tags=["Analytics"])
api_router.include_router(pipeline.router, tags=["Pipeline"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI"])
api_router.include_router(recommendations.router, tags=["Recommendations"])
