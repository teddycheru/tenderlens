"""
User API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_active_user
from app.schemas.user import UserResponse, UserUpdate, PasswordChange, Message
from app.services.user_service import UserService
from app.models.user import User

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user's profile.

    Args:
        current_user: Current authenticated user

    Returns:
        User profile data
    """
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_my_profile(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update current user's profile.

    Args:
        user_data: User update data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Updated user profile data

    Raises:
        HTTPException 400: If email already exists
    """
    updated_user = UserService.update_user(db, current_user.id, user_data)
    return updated_user


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_account(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete (deactivate) current user's account.

    This performs a soft delete by setting is_active to False.

    Args:
        db: Database session
        current_user: Current authenticated user
    """
    UserService.delete_user(db, current_user.id)


@router.post("/me/change-password", response_model=Message)
async def change_my_password(
    password_data: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Change current user's password.

    Args:
        password_data: Current and new password
        db: Database session
        current_user: Current authenticated user

    Returns:
        Success message

    Raises:
        HTTPException 400: If current password is incorrect
    """
    UserService.change_password(
        db,
        current_user.id,
        password_data.current_password,
        password_data.new_password
    )
    return {"message": "Password changed successfully"}
