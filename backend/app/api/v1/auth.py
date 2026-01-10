"""
Authentication API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_active_user
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    Token,
    AuthResponse,
    RefreshTokenRequest,
    Message
)
from app.services.auth_service import AuthService
from app.models.user import User

router = APIRouter()


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user.

    Args:
        user_data: User registration data
        db: Database session

    Returns:
        Created user data with JWT tokens

    Raises:
        HTTPException 400: If email already exists
        HTTPException 404: If company_id provided but company doesn't exist
    """
    user = AuthService.create_user(db, user_data)

    # Create tokens
    access_token, refresh_token = AuthService.create_user_tokens(user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user
    }


@router.post("/login", response_model=AuthResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login with email and password to receive JWT tokens.

    Uses OAuth2PasswordRequestForm which expects:
    - username: User's email address
    - password: User's password

    Args:
        form_data: OAuth2 login form data
        db: Database session

    Returns:
        Access token, refresh token, and user data

    Raises:
        HTTPException 401: If credentials are invalid
        HTTPException 403: If user is inactive
    """
    # Authenticate user (username field contains email)
    user = AuthService.authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    # Create tokens
    access_token, refresh_token = AuthService.create_user_tokens(user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user
    }


@router.post("/login/json", response_model=AuthResponse)
async def login_json(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Login with JSON payload (alternative to form-based login).

    Args:
        credentials: User login credentials (email and password)
        db: Database session

    Returns:
        Access token, refresh token, and user data

    Raises:
        HTTPException 401: If credentials are invalid
        HTTPException 403: If user is inactive
    """
    # Authenticate user
    user = AuthService.authenticate_user(db, credentials.email, credentials.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    # Create tokens
    access_token, refresh_token = AuthService.create_user_tokens(user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using a refresh token.

    Args:
        token_data: Refresh token request data
        db: Database session

    Returns:
        New access token and the same refresh token

    Raises:
        HTTPException 401: If refresh token is invalid
        HTTPException 403: If user is inactive
    """
    # Generate new access token
    new_access_token = AuthService.refresh_access_token(db, token_data.refresh_token)

    return {
        "access_token": new_access_token,
        "refresh_token": token_data.refresh_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current authenticated user information.

    This is a protected endpoint that requires a valid JWT access token.

    Args:
        current_user: Current authenticated user (from JWT token)

    Returns:
        Current user data

    Raises:
        HTTPException 401: If token is invalid or missing
        HTTPException 403: If user is inactive
    """
    return current_user


@router.post("/logout", response_model=Message)
async def logout(
    current_user: User = Depends(get_current_active_user)
):
    """
    Logout endpoint (placeholder for client-side token deletion).

    In JWT-based authentication, logout is typically handled client-side
    by deleting the stored tokens. This endpoint exists for consistency
    and could be extended to implement token blacklisting if needed.

    Args:
        current_user: Current authenticated user

    Returns:
        Logout success message
    """
    return {
        "message": "Successfully logged out. Please delete tokens on client side."
    }
