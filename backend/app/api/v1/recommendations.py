"""
Recommendation API endpoints.

Endpoints:
- GET /recommendations - Get personalized recommendations
- GET /tenders/{tender_id}/similar - Get similar tenders
- POST /refresh-profile-embedding - Refresh profile embedding
- POST /recommendations/{tender_id}/feedback - Submit feedback
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone

from app.core.dependencies import get_current_user, get_db
from app.services.recommendation_service import recommendation_service
from app.services.company_profile_service import CompanyProfileService
from app.models.user import User
from app.models.tender import Tender
from app.models.user_interaction import UserInteraction
from app.models.company_profile import CompanyTenderProfile
from datetime import timedelta
from app.schemas.recommendation import (
    RecommendationResponse,
    TenderRecommendation,
    MatchReason,
    RecommendationFeedback,
    SimilarTenderResponse
)
from app.workers.embedding_tasks import generate_profile_embedding_task

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("", response_model=RecommendationResponse)
async def get_recommendations(
    limit: int = Query(20, ge=1, le=100),
    min_score: Optional[float] = Query(None, ge=0, le=100),
    days_ahead: int = Query(7, ge=1, le=90),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get personalized tender recommendations for the current user.

    Parameters:
    - limit: Number of recommendations (1-100, default: 20)
    - min_score: Minimum match score (0-100, default: profile threshold)
    - days_ahead: Only show tenders with at least this many days until deadline (default: 7)
    """

    # Get user's company profile
    profile = CompanyProfileService.get_profile_by_company(
        db, current_user.company_id
    )

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Company profile not found. Please complete onboarding."
        )

    if profile.profile_embedding is None:
        raise HTTPException(
            status_code=400,
            detail="Profile embedding not ready. Please wait a moment or refresh your profile."
        )

    # Get recommendations
    recommendations = recommendation_service.get_recommendations(
        db=db,
        profile=profile,
        limit=limit,
        min_score=min_score,
        days_ahead=days_ahead
    )

    # Format response
    tender_recommendations = []
    for tender, score, reasons in recommendations:
        days_until = (tender.deadline - datetime.now(timezone.utc).date()).days
        tender_recommendations.append(
            TenderRecommendation(
                tender=tender,
                match_score=score,
                match_reasons=[MatchReason(**r) for r in reasons['reasons']],
                semantic_similarity=reasons['similarity'],
                days_until_deadline=days_until
            )
        )

    return RecommendationResponse(
        recommendations=tender_recommendations,
        total_count=len(tender_recommendations),
        profile_id=str(profile.id),
        profile_completion=float(profile.completion_percentage),
        generated_at=datetime.now(timezone.utc)
    )


@router.get("/tenders/{tender_id}/similar", response_model=List[SimilarTenderResponse])
async def get_similar_tenders(
    tender_id: str,
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """
    Get tenders similar to a specific tender.
    Useful for "You might also like" features.
    """

    similar = recommendation_service.get_similar_tenders(
        db=db,
        tender_id=tender_id,
        limit=limit
    )

    if not similar:
        raise HTTPException(
            status_code=404,
            detail="Tender not found or has no embedding"
        )

    return [
        SimilarTenderResponse(
            tender=tender,
            similarity_score=similarity,
            days_until_deadline=(tender.deadline - datetime.now(timezone.utc).date()).days
        )
        for tender, similarity in similar
    ]


@router.post("/refresh-profile-embedding")
async def refresh_profile_embedding(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Manually trigger profile embedding regeneration.
    Useful after user updates their profile.
    """
    profile = CompanyProfileService.get_profile_by_company(
        db, current_user.company_id
    )

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Trigger async embedding generation
    task = generate_profile_embedding_task.delay(str(profile.id))

    return {
        "message": "Profile embedding regeneration started",
        "task_id": task.id,
        "profile_id": str(profile.id)
    }


@router.post("/feedback/{tender_id}")
async def submit_recommendation_feedback(
    tender_id: str,
    feedback: RecommendationFeedback,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Collect user feedback on recommendation quality.

    This helps improve recommendations over time by:
    1. Adjusting profile scoring weights based on what users actually like
    2. Identifying patterns in relevant vs irrelevant recommendations
    3. Building data for future collaborative filtering

    Feedback types:
    - relevant: User found this recommendation helpful
    - not_relevant: Recommendation was not useful
    - applied: User applied to this tender (strongest positive signal)
    - saved: User saved for later (positive signal)
    - dismissed: Not interested (negative signal)
    """

    # Verify tender exists
    tender = db.query(Tender).filter(Tender.id == tender_id).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")

    # Check if interaction already exists
    existing_interaction = db.query(UserInteraction).filter(
        UserInteraction.user_id == current_user.id,
        UserInteraction.tender_id == tender_id,
        UserInteraction.interaction_type == feedback.interaction_type
    ).first()

    if existing_interaction:
        # Update existing interaction
        existing_interaction.feedback_reason = feedback.reason
        existing_interaction.created_at = datetime.now(timezone.utc)
    else:
        # Create new interaction
        interaction = UserInteraction(
            user_id=current_user.id,
            company_id=current_user.company_id,
            tender_id=tender_id,
            interaction_type=feedback.interaction_type,
            feedback_reason=feedback.reason,
            match_score_at_time=feedback.match_score,
            tender_category=tender.category,
            tender_region=tender.region,
            tender_budget=tender.budget,
            created_at=datetime.now(timezone.utc)
        )
        db.add(interaction)

    # Update profile interaction count
    profile = CompanyProfileService.get_profile_by_company(
        db, current_user.company_id
    )
    if profile:
        profile.interaction_count += 1
        profile.last_interaction_at = datetime.now(timezone.utc)

    db.commit()

    return {
        "message": "Feedback recorded successfully",
        "tender_id": tender_id,
        "interaction_type": feedback.interaction_type
    }


@router.get("/debug")
async def debug_recommendations(
    days_ahead: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Debug endpoint to understand why recommendations might be empty.
    Shows profile settings and tender counts for each filter stage.
    """
    today = datetime.now(timezone.utc).date()
    max_deadline = today + timedelta(days=days_ahead)

    # Get profile
    profile = CompanyProfileService.get_profile_by_company(db, current_user.company_id)

    if not profile:
        return {"error": "No profile found"}

    # Count tenders at each filter stage
    total_tenders = db.query(Tender).count()

    with_embedding = db.query(Tender).filter(
        Tender.content_embedding.isnot(None)
    ).count()

    active_status = db.query(Tender).filter(
        Tender.recommendation_status == 'active'
    ).count()

    future_deadline = db.query(Tender).filter(
        Tender.deadline >= today
    ).count()

    deadline_in_range = db.query(Tender).filter(
        Tender.deadline >= today,
        Tender.deadline <= max_deadline
    ).count()

    # Check sector matching
    matching_sectors = 0
    if profile.active_sectors:
        matching_sectors = db.query(Tender).filter(
            Tender.category.in_(profile.active_sectors)
        ).count()

    # Check region matching
    matching_regions = 0
    if profile.preferred_regions:
        matching_regions = db.query(Tender).filter(
            Tender.region.in_(profile.preferred_regions)
        ).count()

    # Sample tender deadlines
    sample_tenders = db.query(Tender).limit(5).all()
    tender_samples = [
        {
            "title": t.title[:50],
            "category": t.category,
            "region": t.region,
            "deadline": str(t.deadline) if t.deadline else None,
            "recommendation_status": t.recommendation_status,
            "has_embedding": t.content_embedding is not None
        }
        for t in sample_tenders
    ]

    return {
        "profile": {
            "id": str(profile.id),
            "has_embedding": profile.profile_embedding is not None,
            "active_sectors": profile.active_sectors,
            "preferred_regions": profile.preferred_regions,
            "min_match_threshold": profile.min_match_threshold
        },
        "filter_analysis": {
            "total_tenders": total_tenders,
            "with_embedding": with_embedding,
            "active_status": active_status,
            "future_deadline": future_deadline,
            "deadline_in_range": deadline_in_range,
            "matching_sectors": matching_sectors,
            "matching_regions": matching_regions,
            "days_ahead": days_ahead,
            "date_range": f"{today} to {max_deadline}"
        },
        "sample_tenders": tender_samples,
        "diagnosis": _diagnose_empty_recommendations(
            total_tenders, with_embedding, active_status,
            future_deadline, deadline_in_range, matching_sectors,
            matching_regions, profile
        )
    }


def _diagnose_empty_recommendations(
    total, with_embedding, active, future, in_range,
    sectors, regions, profile
):
    """Generate diagnosis messages based on filter counts."""
    issues = []

    if total == 0:
        issues.append("No tenders in database")
    if with_embedding == 0:
        issues.append("No tenders have embeddings - run embedding generation")
    if active == 0:
        issues.append("No tenders have recommendation_status='active'")
    if future == 0:
        issues.append("All tender deadlines are in the past")
    if in_range == 0:
        issues.append(f"No tenders with deadlines in the next {profile.min_match_threshold} days")
    if profile.active_sectors and sectors == 0:
        issues.append(f"No tenders match profile sectors: {profile.active_sectors}")
    if profile.preferred_regions and regions == 0:
        issues.append(f"No tenders match profile regions: {profile.preferred_regions}")
    if not profile.profile_embedding:
        issues.append("Profile has no embedding")

    if not issues:
        return ["All filters pass - issue might be min_score threshold or vector similarity"]

    return issues
