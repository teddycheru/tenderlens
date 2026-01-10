"""
Tender service - Business logic for tender management.
"""

from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from fastapi import HTTPException, status
from typing import List, Tuple
from uuid import UUID

from app.models.tender import Tender
from app.schemas.tender import TenderCreate, TenderUpdate, TenderFilter


class TenderService:
    """
    Service class for tender-related operations.
    """

    @staticmethod
    def create_tender(db: Session, tender_data: TenderCreate) -> Tender:
        """
        Create a new tender.

        Args:
            db: Database session
            tender_data: Tender creation data

        Returns:
            Created tender
        """
        tender = Tender(**tender_data.model_dump())
        db.add(tender)
        db.commit()
        db.refresh(tender)

        return tender

    @staticmethod
    def get_tender(db: Session, tender_id: UUID) -> Tender:
        """
        Get tender by ID.

        Args:
            db: Database session
            tender_id: Tender UUID

        Returns:
            Tender

        Raises:
            HTTPException 404: If tender not found
        """
        tender = db.query(Tender).filter(Tender.id == tender_id).first()

        if not tender:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tender not found"
            )

        return tender

    @staticmethod
    def list_tenders(
        db: Session,
        filters: TenderFilter
    ) -> Tuple[List[Tender], int]:
        """
        List tenders with filtering, searching, and pagination.

        Args:
            db: Database session
            filters: Filter criteria

        Returns:
            Tuple of (list of tenders, total count)
        """
        query = db.query(Tender)

        # Apply category filter
        if filters.category:
            query = query.filter(Tender.category == filters.category)

        # Apply region filter
        if filters.region:
            query = query.filter(Tender.region == filters.region)

        # Apply status filter
        if filters.status:
            query = query.filter(Tender.status == filters.status)

        # Apply published date filters
        if filters.published_from:
            query = query.filter(Tender.published_date >= filters.published_from)

        if filters.published_to:
            query = query.filter(Tender.published_date <= filters.published_to)

        # Apply deadline date filters
        if filters.deadline_from:
            query = query.filter(Tender.deadline >= filters.deadline_from)

        if filters.deadline_to:
            query = query.filter(Tender.deadline <= filters.deadline_to)

        # Apply search filter (searches in title and description)
        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.filter(
                or_(
                    Tender.title.ilike(search_term),
                    Tender.description.ilike(search_term)
                )
            )

        # Get total count before pagination
        total = query.count()

        # Apply pagination and ordering
        tenders = query.order_by(Tender.created_at.desc()).offset(filters.skip).limit(filters.limit).all()

        return tenders, total

    @staticmethod
    def update_tender(
        db: Session,
        tender_id: UUID,
        tender_data: TenderUpdate
    ) -> Tender:
        """
        Update tender.

        Args:
            db: Database session
            tender_id: Tender UUID
            tender_data: Tender update data

        Returns:
            Updated tender

        Raises:
            HTTPException 404: If tender not found
        """
        tender = TenderService.get_tender(db, tender_id)

        # Update fields
        update_data = tender_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(tender, field, value)

        db.commit()
        db.refresh(tender)

        return tender

    @staticmethod
    def delete_tender(db: Session, tender_id: UUID) -> None:
        """
        Delete tender.

        Args:
            db: Database session
            tender_id: Tender UUID

        Raises:
            HTTPException 404: If tender not found
        """
        tender = TenderService.get_tender(db, tender_id)
        db.delete(tender)
        db.commit()
