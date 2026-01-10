"""
Pydantic schemas for user-related requests and responses.
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime


# ==================== Authentication Schemas ====================

class UserLogin(BaseModel):
    """
    Schema for user login request.
    """
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password (min 8 characters)")


class UserCreate(BaseModel):
    """
    Schema for user registration request.
    """
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password (min 8 characters)")
    full_name: str = Field(..., min_length=2, max_length=100, description="User full name")
    company_id: Optional[UUID] = Field(None, description="Optional company ID to associate with")
    company_name: Optional[str] = Field(None, description="Optional company name (will be ignored if company_id is provided)")


class UserUpdate(BaseModel):
    """
    Schema for user profile update request.
    """
    full_name: Optional[str] = Field(None, min_length=2, max_length=100, description="User full name")
    email: Optional[EmailStr] = Field(None, description="User email address")
    phone: Optional[str] = Field(None, max_length=20, description="User phone number")


class PasswordChange(BaseModel):
    """
    Schema for password change request.
    """
    current_password: str = Field(..., min_length=1, description="Current password")
    new_password: str = Field(..., min_length=8, description="New password (min 8 characters)")


# ==================== Response Schemas ====================

class UserResponse(BaseModel):
    """
    Schema for user response (excludes sensitive data).
    """
    id: UUID
    email: EmailStr
    full_name: str
    phone: Optional[str]
    is_active: bool
    is_superuser: bool
    company_id: Optional[UUID]
    role: str = "user"  # Default role, can be extended later
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserInDB(UserResponse):
    """
    Schema for user data including hashed password (internal use only).
    """
    hashed_password: str


# ==================== Token Schemas ====================

class Token(BaseModel):
    """
    Schema for JWT token response.
    """
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")


class AuthResponse(BaseModel):
    """
    Schema for authentication response (includes user data and tokens).
    """
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    user: UserResponse = Field(..., description="Authenticated user data")


class TokenPayload(BaseModel):
    """
    Schema for JWT token payload.
    """
    sub: str = Field(..., description="Subject (user ID)")
    exp: int = Field(..., description="Expiration timestamp")
    type: str = Field(..., description="Token type (access or refresh)")


class RefreshTokenRequest(BaseModel):
    """
    Schema for refresh token request.
    """
    refresh_token: str = Field(..., description="JWT refresh token")


# ==================== Message Schemas ====================

class Message(BaseModel):
    """
    Generic message response schema.
    """
    message: str = Field(..., description="Response message")
