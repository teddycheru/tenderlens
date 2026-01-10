"""
Company Profile API Endpoints

Endpoints for company tender profile management and onboarding.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.models.user import User
from app.core.dependencies import get_current_user
from app.services.company_profile_service import CompanyProfileService
from app.schemas.company_profile import (
    CompanyProfileCreate,
    CompanyProfileCreateStep1,
    CompanyProfileCreateStep2,
    CompanyProfileUpdate,
    CompanyProfileResponse,
    CompanyProfileSummary,
    ProfileOptions
)
from app.workers.embedding_tasks import generate_profile_embedding_task

router = APIRouter(prefix="/company-profile", tags=["Company Profile"])


@router.post("", response_model=CompanyProfileResponse, status_code=status.HTTP_201_CREATED)
def create_company_profile(
    profile_data: CompanyProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new company tender profile (complete onboarding).

    This endpoint creates a profile with all fields at once.
    For step-by-step onboarding, use the step-specific endpoints.
    """
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with a company"
        )

    profile = CompanyProfileService.create_profile(
        db=db,
        company_id=current_user.company_id,
        profile_data=profile_data
    )

    # Trigger async embedding generation for the new profile (optional if Celery not available)
    try:
        generate_profile_embedding_task.delay(str(profile.id))
    except Exception as e:
        print(f"⚠️  Celery task failed (embeddings will not be generated): {e}")

    return profile


@router.post("/step1", response_model=CompanyProfileResponse, status_code=status.HTTP_201_CREATED)
def create_profile_step1(
    step1_data: CompanyProfileCreateStep1,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Step 1 of onboarding: Create profile with critical fields only.

    Collects: primary_sector, active_sectors, sub_sectors, preferred_regions, keywords
    """
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with a company"
        )

    # Convert Step1 data to full profile data with defaults
    profile_data = CompanyProfileCreate(
        **step1_data.model_dump(),
        budget_currency="ETB"  # Default currency
    )

    profile = CompanyProfileService.create_profile(
        db=db,
        company_id=current_user.company_id,
        profile_data=profile_data
    )

    # Trigger async embedding generation for the new profile (optional if Celery not available)
    try:
        generate_profile_embedding_task.delay(str(profile.id))
    except Exception as e:
        print(f"⚠️  Celery task failed (embeddings will not be generated): {e}")

    return profile


@router.put("/step2", response_model=CompanyProfileResponse)
def complete_profile_step2(
    step2_data: CompanyProfileCreateStep2,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Step 2 of onboarding: Complete profile with optional refinement fields.

    Adds: company_size, years_in_operation, certifications, budget_range
    """
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with a company"
        )

    # Update profile with Step 2 data
    profile_update = CompanyProfileUpdate(**step2_data.model_dump(exclude_unset=True))

    profile = CompanyProfileService.update_profile(
        db=db,
        company_id=current_user.company_id,
        profile_update=profile_update
    )

    # Trigger async embedding generation to update the profile embedding (optional if Celery not available)
    try:
        generate_profile_embedding_task.delay(str(profile.id))
    except Exception as e:
        print(f"⚠️  Celery task failed (embeddings will not be generated): {e}")

    return profile


@router.get("", response_model=CompanyProfileResponse)
def get_my_company_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the current user's company profile.
    """
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with a company"
        )

    profile = CompanyProfileService.get_profile_by_company(
        db=db,
        company_id=current_user.company_id
    )

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company profile not found. Please complete onboarding."
        )

    return profile


@router.get("/company/{company_id}", response_model=CompanyProfileResponse)
def get_company_profile_by_id(
    company_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a company profile by company ID.

    Restricted to:
    - The company owner
    - Superusers
    """
    # Check permissions
    if not current_user.is_superuser and current_user.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this company profile"
        )

    profile = CompanyProfileService.get_profile_by_company(db=db, company_id=company_id)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company profile not found"
        )

    return profile


@router.put("", response_model=CompanyProfileResponse)
def update_my_company_profile(
    profile_update: CompanyProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update the current user's company profile.

    Allows partial updates - only provided fields will be updated.
    """
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with a company"
        )

    profile = CompanyProfileService.update_profile(
        db=db,
        company_id=current_user.company_id,
        profile_update=profile_update
    )

    return profile


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_company_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete the current user's company profile.

    Note: This will remove all profile data and interaction history.
    """
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with a company"
        )

    CompanyProfileService.delete_profile(
        db=db,
        company_id=current_user.company_id
    )

    return None


@router.get("/options", response_model=ProfileOptions)
def get_profile_options():
    """
    Get available options for profile dropdowns.

    Returns lists of:
    - Available business sectors
    - Ethiopian regions
    - Common certifications
    - Company size options
    - Years in operation options
    - Keyword suggestions by sector
    """
    return CompanyProfileService.get_profile_options()


@router.get("/options/keywords/{sector}", response_model=List[str])
def get_keyword_suggestions_for_sector(sector: str):
    """
    Get keyword suggestions for a specific sector.

    Useful for autocomplete/suggestions when user selects a sector.
    """
    suggestions = CompanyProfileService.get_keyword_suggestions(sector)

    if not suggestions:
        # Return empty list if sector not found
        return []

    return suggestions


@router.get("/stats", response_model=dict)
def get_my_profile_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get statistics about the current user's company profile.

    Returns completion percentage, interaction count, and other metrics.
    """
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with a company"
        )

    stats = CompanyProfileService.get_profile_stats(
        db=db,
        company_id=current_user.company_id
    )

    return stats


# Admin endpoints (superuser only)

@router.get("/admin/incomplete", response_model=List[CompanyProfileSummary])
def get_incomplete_profiles(
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Admin: Get list of incomplete company profiles.

    Useful for follow-up campaigns to encourage profile completion.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can access this endpoint"
        )

    profiles = CompanyProfileService.get_incomplete_profiles(db=db, limit=limit)

    return profiles


@router.get("/admin/sector/{sector}", response_model=List[CompanyProfileSummary])
def get_profiles_by_sector(
    sector: str,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Admin: Get all profiles in a specific sector.

    Useful for analytics and targeted campaigns.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can access this endpoint"
        )

    profiles = CompanyProfileService.get_profiles_by_sector(
        db=db,
        sector=sector,
        limit=limit
    )

    return profiles
