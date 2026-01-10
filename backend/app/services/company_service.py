"""
Company service - Business logic for company management.
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional
from uuid import UUID

from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyUpdate


class CompanyService:
    """
    Service class for company-related operations.
    """

    @staticmethod
    def create_company(db: Session, company_data: CompanyCreate) -> Company:
        """
        Create a new company.

        Args:
            db: Database session
            company_data: Company creation data

        Returns:
            Created company

        Raises:
            HTTPException 400: If company with same name already exists
        """
        # Check if company with same name exists
        existing_company = db.query(Company).filter(
            Company.name == company_data.name
        ).first()

        if existing_company:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Company with this name already exists"
            )

        # Create new company
        company = Company(**company_data.model_dump())
        db.add(company)
        db.commit()
        db.refresh(company)

        return company

    @staticmethod
    def get_company(db: Session, company_id: UUID) -> Company:
        """
        Get company by ID.

        Args:
            db: Database session
            company_id: Company UUID

        Returns:
            Company

        Raises:
            HTTPException 404: If company not found
        """
        company = db.query(Company).filter(Company.id == company_id).first()

        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )

        return company

    @staticmethod
    def update_company(
        db: Session,
        company_id: UUID,
        company_data: CompanyUpdate
    ) -> Company:
        """
        Update company.

        Args:
            db: Database session
            company_id: Company UUID
            company_data: Company update data

        Returns:
            Updated company

        Raises:
            HTTPException 404: If company not found
        """
        company = CompanyService.get_company(db, company_id)

        # Update fields
        update_data = company_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(company, field, value)

        db.commit()
        db.refresh(company)

        return company

    @staticmethod
    def delete_company(db: Session, company_id: UUID) -> None:
        """
        Delete company.

        Args:
            db: Database session
            company_id: Company UUID

        Raises:
            HTTPException 404: If company not found
        """
        company = CompanyService.get_company(db, company_id)
        db.delete(company)
        db.commit()
