"""
User preferences service - Business logic for user preferences management.
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from uuid import UUID

from app.models.user_preferences import UserPreferences
from app.models.user import User
from app.schemas.preferences import UserPreferencesUpdate


class UserPreferencesService:
    """
    Service layer for user preferences operations.
    """

    @staticmethod
    def get_preferences(db: Session, user_id: UUID) -> UserPreferences:
        """
        Get user preferences. If they don't exist, create them with defaults.

        Args:
            db: Database session
            user_id: User UUID

        Returns:
            UserPreferences object

        Raises:
            HTTPException 404: If user doesn't exist
        """
        # Check if user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Try to get existing preferences
        preferences = db.query(UserPreferences).filter(
            UserPreferences.user_id == user_id
        ).first()

        # If preferences don't exist, create them with defaults
        if not preferences:
            preferences = UserPreferencesService.create_default_preferences(db, user_id)

        return preferences

    @staticmethod
    def create_default_preferences(db: Session, user_id: UUID) -> UserPreferences:
        """
        Create default preferences for a user.

        Args:
            db: Database session
            user_id: User UUID

        Returns:
            Created UserPreferences object

        Raises:
            HTTPException 500: If creation fails
        """
        try:
            preferences = UserPreferences(user_id=user_id)
            db.add(preferences)
            db.commit()
            db.refresh(preferences)
            return preferences
        except IntegrityError as e:
            db.rollback()
            # Preferences might already exist, try to fetch them
            preferences = db.query(UserPreferences).filter(
                UserPreferences.user_id == user_id
            ).first()
            if preferences:
                return preferences
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create user preferences: {str(e)}"
            )

    @staticmethod
    def update_preferences(
        db: Session,
        user_id: UUID,
        preferences_update: UserPreferencesUpdate
    ) -> UserPreferences:
        """
        Update user preferences.

        Args:
            db: Database session
            user_id: User UUID
            preferences_update: Preferences update data

        Returns:
            Updated UserPreferences object

        Raises:
            HTTPException 404: If user not found
        """
        # Get existing preferences (or create if not exists)
        preferences = UserPreferencesService.get_preferences(db, user_id)

        # Update only provided fields
        update_data = preferences_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(preferences, field, value)

        try:
            db.commit()
            db.refresh(preferences)
            return preferences
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update preferences: {str(e)}"
            )

    @staticmethod
    def delete_preferences(db: Session, user_id: UUID) -> None:
        """
        Delete user preferences (usually called when user is deleted).

        Args:
            db: Database session
            user_id: User UUID
        """
        preferences = db.query(UserPreferences).filter(
            UserPreferences.user_id == user_id
        ).first()

        if preferences:
            db.delete(preferences)
            db.commit()
