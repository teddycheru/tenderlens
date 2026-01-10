"""
Company API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.dependencies import get_db, get_current_active_user
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyResponse
from app.schemas.user import Message
from app.services.company_service import CompanyService
from app.models.user import User

router = APIRouter()


@router.post("", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(
    company_data: CompanyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new company.

    Args:
        company_data: Company creation data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Created company data

    Raises:
        HTTPException 400: If company with same name already exists
    """
    company = CompanyService.create_company(db, company_data)
    return company


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get company by ID.

    Args:
        company_id: Company UUID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Company data

    Raises:
        HTTPException 404: If company not found
    """
    company = CompanyService.get_company(db, company_id)
    return company


@router.get("/me/company", response_model=CompanyResponse)
async def get_my_company(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user's company.

    Args:
        db: Database session
        current_user: Current authenticated user

    Returns:
        Company data

    Raises:
        HTTPException 404: If user has no company or company not found
    """
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not associated with any company"
        )

    company = CompanyService.get_company(db, current_user.company_id)
    return company


@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: UUID,
    company_data: CompanyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update company.

    Only users belonging to the company or superusers can update it.

    Args:
        company_id: Company UUID
        company_data: Company update data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Updated company data

    Raises:
        HTTPException 403: If user doesn't have permission
        HTTPException 404: If company not found
    """
    # Check permissions
    if current_user.company_id != company_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this company"
        )

    company = CompanyService.update_company(db, company_id, company_data)
    return company


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(
    company_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete company (admin only).

    Args:
        company_id: Company UUID
        db: Database session
        current_user: Current authenticated user

    Raises:
        HTTPException 403: If user is not superuser
        HTTPException 404: If company not found
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can delete companies"
        )

    CompanyService.delete_company(db, company_id)
