# backend/app/api/v1/analytics.py
"""
Analytics API endpoints for tender insights and trends.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict

from app.database import get_db
from app.services.analytics.aggregator import analytics_aggregator

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary", response_model=Dict)
def get_summary_statistics(
    db: Session = Depends(get_db)
):
    """
    Get summary statistics for all tenders.

    Returns:
        - total_tenders: Total number of tenders
        - upcoming_tenders: Tenders with deadlines in next 30 days
        - recent_tenders: Tenders created in last 7 days
        - average_budget: Average tender budget
    """
    try:
        stats = analytics_aggregator.get_summary_stats(db)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/volume-trends", response_model=Dict)
def get_volume_trends(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """
    Get tender volume trends over time.

    Args:
        days: Number of days to analyze (default: 30)

    Returns:
        Daily tender counts
    """
    try:
        trends = analytics_aggregator.get_volume_trends(db, days)
        return trends
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/category-distribution", response_model=Dict)
def get_category_distribution(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """
    Get tender distribution by category.

    Args:
        days: Number of days to analyze (default: 30)

    Returns:
        Tender counts by category
    """
    try:
        distribution = analytics_aggregator.get_category_distribution(db, days)
        return distribution
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/regional-distribution", response_model=Dict)
def get_regional_distribution(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """
    Get tender distribution by region.

    Args:
        days: Number of days to analyze (default: 30)

    Returns:
        Tender counts by region
    """
    try:
        distribution = analytics_aggregator.get_regional_distribution(db, days)
        return distribution
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
