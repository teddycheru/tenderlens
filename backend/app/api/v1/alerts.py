"""
Alert API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional

from app.core.dependencies import get_db, get_current_active_user
from app.schemas.alert import (
    AlertCreate,
    AlertUpdate,
    AlertResponse,
    AlertListResponse
)
from app.services.alert_service import AlertService
from app.models.user import User

router = APIRouter()


@router.get("", response_model=AlertListResponse)
async def list_alerts(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
    active_only: bool = Query(False, description="Return only active alerts"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List all alerts for the current user's company.

    Requires authentication.

    Args:
        skip: Number of records to skip (pagination)
        limit: Number of records to return (pagination)
        active_only: If True, return only active alerts
        db: Database session
        current_user: Current authenticated user

    Returns:
        Paginated list of alerts with total count

    Raises:
        HTTPException 400: If user is not associated with a company
    """
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with a company to manage alerts"
        )

    alerts, total = AlertService.list_alerts_by_company(
        db,
        company_id=current_user.company_id,
        skip=skip,
        limit=limit,
        active_only=active_only
    )

    return AlertListResponse(
        total=total,
        items=alerts,
        skip=skip,
        limit=limit
    )


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get alert by ID.

    Requires authentication.

    Args:
        alert_id: Alert UUID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Alert data

    Raises:
        HTTPException 404: If alert not found
        HTTPException 403: If alert doesn't belong to user's company
    """
    alert = AlertService.get_alert(db, alert_id)

    # Verify alert belongs to user's company
    if current_user.company_id != alert.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this alert"
        )

    return alert


@router.post("", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def create_alert(
    alert_data: AlertCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new alert for the user's company.

    Requires authentication.

    Args:
        alert_data: Alert creation data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Created alert data

    Raises:
        HTTPException 400: If user is not associated with a company
    """
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with a company to create alerts"
        )

    alert = AlertService.create_alert(db, alert_data, current_user.company_id)
    return alert


@router.put("/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: UUID,
    alert_data: AlertUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update alert.

    Requires authentication.

    Args:
        alert_id: Alert UUID
        alert_data: Alert update data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Updated alert data

    Raises:
        HTTPException 404: If alert not found
        HTTPException 403: If alert doesn't belong to user's company
        HTTPException 400: If user is not associated with a company
    """
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with a company to update alerts"
        )

    alert = AlertService.update_alert(db, alert_id, alert_data, current_user.company_id)
    return alert


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert(
    alert_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete alert.

    Requires authentication.

    Args:
        alert_id: Alert UUID
        db: Database session
        current_user: Current authenticated user

    Raises:
        HTTPException 404: If alert not found
        HTTPException 403: If alert doesn't belong to user's company
        HTTPException 400: If user is not associated with a company
    """
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with a company to delete alerts"
        )

    AlertService.delete_alert(db, alert_id, current_user.company_id)


@router.patch("/{alert_id}/toggle", response_model=AlertResponse)
async def toggle_alert_status(
    alert_id: UUID,
    is_active: bool = Query(..., description="New active status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Toggle alert active status (enable/disable).

    Requires authentication.

    Args:
        alert_id: Alert UUID
        is_active: New active status
        db: Database session
        current_user: Current authenticated user

    Returns:
        Updated alert data

    Raises:
        HTTPException 404: If alert not found
        HTTPException 403: If alert doesn't belong to user's company
        HTTPException 400: If user is not associated with a company
    """
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with a company to manage alerts"
        )

    alert = AlertService.toggle_alert_status(db, alert_id, current_user.company_id, is_active)
    return alert
