"""
User service - Business logic for user profile management.
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from uuid import UUID

from app.models.user import User
from app.schemas.user import UserUpdate
from app.core.security import get_password_hash, verify_password


class UserService:
    """
    Service class for user-related operations.
    """

    @staticmethod
    def get_user(db: Session, user_id: UUID) -> User:
        """
        Get user by ID.

        Args:
            db: Database session
            user_id: User UUID

        Returns:
            User

        Raises:
            HTTPException 404: If user not found
        """
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return user

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> User:
        """
        Get user by email.

        Args:
            db: Database session
            email: User email

        Returns:
            User

        Raises:
            HTTPException 404: If user not found
        """
        user = db.query(User).filter(User.email == email).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return user

    @staticmethod
    def update_user(
        db: Session,
        user_id: UUID,
        user_data: UserUpdate
    ) -> User:
        """
        Update user profile.

        Args:
            db: Database session
            user_id: User UUID
            user_data: User update data

        Returns:
            Updated user

        Raises:
            HTTPException 404: If user not found
            HTTPException 400: If email already exists
        """
        user = UserService.get_user(db, user_id)

        # Check if email is being updated and if it already exists
        if user_data.email and user_data.email != user.email:
            existing_user = db.query(User).filter(User.email == user_data.email).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )

        # Update fields
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def delete_user(db: Session, user_id: UUID) -> None:
        """
        Delete user (soft delete by setting is_active to False).

        Args:
            db: Database session
            user_id: User UUID

        Raises:
            HTTPException 404: If user not found
        """
        user = UserService.get_user(db, user_id)
        user.is_active = False
        db.commit()

    @staticmethod
    def change_password(
        db: Session,
        user_id: UUID,
        current_password: str,
        new_password: str
    ) -> None:
        """
        Change user password.

        Args:
            db: Database session
            user_id: User UUID
            current_password: Current password for verification
            new_password: New password to set

        Raises:
            HTTPException 404: If user not found
            HTTPException 400: If current password is incorrect
        """
        user = UserService.get_user(db, user_id)

        # Verify current password
        if not verify_password(current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )

        # Hash and set new password
        user.hashed_password = get_password_hash(new_password)
        db.commit()
