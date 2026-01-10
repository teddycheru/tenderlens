"""
Alert service - Business logic for alert management.
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Tuple
from uuid import UUID

from app.models.alert import Alert
from app.models.company import Company
from app.models.user import User
from app.schemas.alert import AlertCreate, AlertUpdate


class AlertService:
    """
    Service class for alert-related operations.
    """

    @staticmethod
    def create_alert(
        db: Session,
        alert_data: AlertCreate,
        company_id: UUID
    ) -> Alert:
        """
        Create a new alert for a company.

        Args:
            db: Database session
            alert_data: Alert creation data
            company_id: Company UUID

        Returns:
            Created alert

        Raises:
            HTTPException 404: If company not found
        """
        # Verify company exists
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )

        # Create alert
        alert_dict = alert_data.model_dump()
        alert_dict['company_id'] = company_id
        alert = Alert(**alert_dict)

        db.add(alert)
        db.commit()
        db.refresh(alert)

        return alert

    @staticmethod
    def get_alert(db: Session, alert_id: UUID) -> Alert:
        """
        Get alert by ID.

        Args:
            db: Database session
            alert_id: Alert UUID

        Returns:
            Alert

        Raises:
            HTTPException 404: If alert not found
        """
        alert = db.query(Alert).filter(Alert.id == alert_id).first()

        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found"
            )

        return alert

    @staticmethod
    def list_alerts_by_company(
        db: Session,
        company_id: UUID,
        skip: int = 0,
        limit: int = 20,
        active_only: bool = False
    ) -> Tuple[List[Alert], int]:
        """
        List alerts for a specific company.

        Args:
            db: Database session
            company_id: Company UUID
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return
            active_only: If True, return only active alerts

        Returns:
            Tuple of (list of alerts, total count)
        """
        query = db.query(Alert).filter(Alert.company_id == company_id)

        # Filter by active status if requested
        if active_only:
            query = query.filter(Alert.is_active == True)

        # Get total count before pagination
        total = query.count()

        # Apply pagination and ordering
        alerts = query.order_by(Alert.created_at.desc()).offset(skip).limit(limit).all()

        return alerts, total

    @staticmethod
    def update_alert(
        db: Session,
        alert_id: UUID,
        alert_data: AlertUpdate,
        company_id: UUID
    ) -> Alert:
        """
        Update alert.

        Args:
            db: Database session
            alert_id: Alert UUID
            alert_data: Alert update data
            company_id: Company UUID (for authorization)

        Returns:
            Updated alert

        Raises:
            HTTPException 404: If alert not found
            HTTPException 403: If alert doesn't belong to company
        """
        alert = AlertService.get_alert(db, alert_id)

        # Verify alert belongs to company
        if alert.company_id != company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this alert"
            )

        # Update fields
        update_data = alert_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(alert, field, value)

        db.commit()
        db.refresh(alert)

        return alert

    @staticmethod
    def delete_alert(db: Session, alert_id: UUID, company_id: UUID) -> None:
        """
        Delete alert.

        Args:
            db: Database session
            alert_id: Alert UUID
            company_id: Company UUID (for authorization)

        Raises:
            HTTPException 404: If alert not found
            HTTPException 403: If alert doesn't belong to company
        """
        alert = AlertService.get_alert(db, alert_id)

        # Verify alert belongs to company
        if alert.company_id != company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this alert"
            )

        db.delete(alert)
        db.commit()

    @staticmethod
    def toggle_alert_status(
        db: Session,
        alert_id: UUID,
        company_id: UUID,
        is_active: bool
    ) -> Alert:
        """
        Toggle alert active status.

        Args:
            db: Database session
            alert_id: Alert UUID
            company_id: Company UUID (for authorization)
            is_active: New active status

        Returns:
            Updated alert

        Raises:
            HTTPException 404: If alert not found
            HTTPException 403: If alert doesn't belong to company
        """
        alert = AlertService.get_alert(db, alert_id)

        # Verify alert belongs to company
        if alert.company_id != company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this alert"
            )

        alert.is_active = is_active
        db.commit()
        db.refresh(alert)

        return alert
