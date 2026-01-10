"""
User preferences API endpoints.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_active_user
from app.models.user import User
from app.schemas.preferences import UserPreferencesResponse, UserPreferencesUpdate
from app.services.user_preferences_service import UserPreferencesService

router = APIRouter()


@router.get("/users/me/preferences", response_model=UserPreferencesResponse)
async def get_my_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user's preferences.

    Returns preferences if they exist, or creates them with defaults if they don't.

    Args:
        db: Database session
        current_user: Currently authenticated user

    Returns:
        User preferences
    """
    preferences = UserPreferencesService.get_preferences(db, current_user.id)
    return preferences


@router.put("/users/me/preferences", response_model=UserPreferencesResponse)
async def update_my_preferences(
    preferences_update: UserPreferencesUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update current user's preferences.

    Only provided fields will be updated. Other fields will remain unchanged.

    Args:
        preferences_update: Preference fields to update
        db: Database session
        current_user: Currently authenticated user

    Returns:
        Updated user preferences
    """
    preferences = UserPreferencesService.update_preferences(
        db,
        current_user.id,
        preferences_update
    )
    return preferences
