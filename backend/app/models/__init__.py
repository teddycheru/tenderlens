"""
Database models for TenderLens.
"""

from app.models.user import User
from app.models.user_preferences import UserPreferences
from app.models.company import Company
from app.models.tender import Tender
from app.models.alert import Alert, TenderAlert
from app.models.tender_staging import TenderStaging
from app.models.validation_error import ValidationError
from app.models.duplicate_log import DuplicateLog
from app.models.scrape_log import ScrapeLog
from app.models.company_profile import CompanyTenderProfile
from app.models.user_interaction import UserInteraction, INTERACTION_WEIGHTS

__all__ = [
    "User",
    "UserPreferences",
    "Company",
    "Tender",
    "Alert",
    "TenderAlert",
    "TenderStaging",
    "ValidationError",
    "DuplicateLog",
    "ScrapeLog",
    "CompanyTenderProfile",
    "UserInteraction",
    "INTERACTION_WEIGHTS"
]
