"""
Tender API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional
from datetime import date

from app.core.dependencies import get_db, get_current_active_user
from app.schemas.tender import (
    TenderCreate,
    TenderUpdate,
    TenderResponse,
    TenderFilter,
    TenderListResponse,
    TenderStatus,
    TenderWithScore,
    TenderWithScoreListResponse
)
from app.services.tender_service import TenderService
# TODO: Re-enable when recommendation system is implemented
# from app.services.recommendation.scorer import RecommendationScorer
from app.models.user import User
# from app.models.company_profile import CompanyTenderProfile
from app.workers.embedding_tasks import generate_tender_embedding_task

router = APIRouter()


@router.get("", response_model=TenderListResponse)
async def list_tenders(
    category: Optional[str] = Query(None, description="Filter by category"),
    region: Optional[str] = Query(None, description="Filter by region"),
    status_filter: Optional[TenderStatus] = Query(None, alias="status", description="Filter by status"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    published_from: Optional[date] = Query(None, description="Filter tenders published from this date"),
    published_to: Optional[date] = Query(None, description="Filter tenders published until this date"),
    deadline_from: Optional[date] = Query(None, description="Filter tenders with deadline from this date"),
    deadline_to: Optional[date] = Query(None, description="Filter tenders with deadline until this date"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
    db: Session = Depends(get_db)
):
    """
    List all tenders with optional filtering and pagination.

    Public endpoint - no authentication required.

    Args:
        category: Filter by category
        region: Filter by region
        status_filter: Filter by status
        search: Search term for title and description
        published_from: Filter tenders published from this date
        published_to: Filter tenders published until this date
        deadline_from: Filter tenders with deadline from this date
        deadline_to: Filter tenders with deadline until this date
        skip: Number of records to skip (pagination)
        limit: Number of records to return (pagination)
        db: Database session

    Returns:
        Paginated list of tenders with total count
    """
    filters = TenderFilter(
        category=category,
        region=region,
        status=status_filter,
        search=search,
        published_from=published_from,
        published_to=published_to,
        deadline_from=deadline_from,
        deadline_to=deadline_to,
        skip=skip,
        limit=limit
    )

    tenders, total = TenderService.list_tenders(db, filters)

    return TenderListResponse(
        total=total,
        items=tenders,
        skip=skip,
        limit=limit
    )


@router.get("/recommended", response_model=TenderWithScoreListResponse)
async def get_recommended_tenders(
    min_score: float = Query(0, ge=0, le=100, description="Minimum relevance score"),
    limit: int = Query(50, ge=1, le=100, description="Number of recommendations to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get personalized tender recommendations for the current user.

    TODO: Recommendation system not yet implemented.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Recommendation system is not yet implemented. Please check back later."
    )


@router.get("/{tender_id}", response_model=TenderResponse)
async def get_tender(
    tender_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get tender by ID.

    Public endpoint - no authentication required.

    Args:
        tender_id: Tender UUID
        db: Database session

    Returns:
        Tender data

    Raises:
        HTTPException 404: If tender not found
    """
    tender = TenderService.get_tender(db, tender_id)
    return tender


@router.post("", response_model=TenderResponse, status_code=status.HTTP_201_CREATED)
async def create_tender(
    tender_data: TenderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new tender.

    Requires authentication.

    Args:
        tender_data: Tender creation data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Created tender data
    """
    tender = TenderService.create_tender(db, tender_data)

    # Trigger async embedding generation for recommendations
    try:
        generate_tender_embedding_task.delay(str(tender.id))
    except Exception as e:
        print(f"⚠️  Celery task failed (embedding will not be generated): {e}")

    return tender


@router.put("/{tender_id}", response_model=TenderResponse)
async def update_tender(
    tender_id: UUID,
    tender_data: TenderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update tender.

    Requires authentication.

    Args:
        tender_id: Tender UUID
        tender_data: Tender update data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Updated tender data

    Raises:
        HTTPException 404: If tender not found
    """
    tender = TenderService.update_tender(db, tender_id, tender_data)

    # Regenerate embedding if content changed
    try:
        generate_tender_embedding_task.delay(str(tender.id))
    except Exception as e:
        print(f"⚠️  Celery task failed (embedding will not be regenerated): {e}")

    return tender


@router.delete("/{tender_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tender(
    tender_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete tender (superuser only).

    Args:
        tender_id: Tender UUID
        db: Database session
        current_user: Current authenticated user

    Raises:
        HTTPException 403: If user is not superuser
        HTTPException 404: If tender not found
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can delete tenders"
        )

    TenderService.delete_tender(db, tender_id)


@router.get("/{tender_id}/score")
async def get_tender_score(
    tender_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get relevance score for a specific tender.

    TODO: Recommendation system not yet implemented.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Tender scoring system is not yet implemented. Please check back later."
    )
