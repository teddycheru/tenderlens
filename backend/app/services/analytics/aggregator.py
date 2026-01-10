# backend/app/services/analytics/aggregator.py
"""
Analytics aggregator for tender insights and trends.
"""

from typing import Dict, List
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime, timedelta

from app.models.tender import Tender


class AnalyticsAggregator:
    """Aggregate and analyze tender data for insights."""

    def get_volume_trends(self, db: Session, days: int = 30) -> Dict:
        """
        Get tender volume trends over time.

        Args:
            db: Database session
            days: Number of days to analyze

        Returns:
            Tender volume trends by day
        """
        since_date = datetime.utcnow() - timedelta(days=days)

        # Group tenders by creation date
        results = db.query(
            func.date(Tender.created_at).label('date'),
            func.count(Tender.id).label('count')
        ).filter(
            Tender.created_at >= since_date
        ).group_by(
            func.date(Tender.created_at)
        ).order_by(
            func.date(Tender.created_at)
        ).all()

        return {
            "period_days": days,
            "data": [
                {"date": str(row.date), "count": row.count}
                for row in results
            ]
        }

    def get_category_distribution(self, db: Session, days: int = 30) -> Dict:
        """
        Get tender distribution by category.

        Args:
            db: Database session
            days: Number of days to analyze

        Returns:
            Tender counts by category
        """
        since_date = datetime.utcnow() - timedelta(days=days)

        results = db.query(
            Tender.category,
            func.count(Tender.id).label('count')
        ).filter(
            Tender.created_at >= since_date,
            Tender.category.isnot(None)
        ).group_by(
            Tender.category
        ).order_by(
            func.count(Tender.id).desc()
        ).all()

        return {
            "period_days": days,
            "data": [
                {"category": row.category, "count": row.count}
                for row in results
            ]
        }

    def get_regional_distribution(self, db: Session, days: int = 30) -> Dict:
        """
        Get tender distribution by region.

        Args:
            db: Database session
            days: Number of days to analyze

        Returns:
            Tender counts by region
        """
        since_date = datetime.utcnow() - timedelta(days=days)

        results = db.query(
            Tender.region,
            func.count(Tender.id).label('count')
        ).filter(
            Tender.created_at >= since_date,
            Tender.region.isnot(None)
        ).group_by(
            Tender.region
        ).order_by(
            func.count(Tender.id).desc()
        ).all()

        return {
            "period_days": days,
            "data": [
                {"region": row.region, "count": row.count}
                for row in results
            ]
        }

    def get_summary_stats(self, db: Session) -> Dict:
        """
        Get summary statistics for tenders.

        Returns:
            Summary statistics
        """
        total_tenders = db.query(func.count(Tender.id)).scalar()

        # Tenders with upcoming deadlines (next 30 days)
        upcoming_deadline = datetime.utcnow().date() + timedelta(days=30)
        upcoming_tenders = db.query(func.count(Tender.id)).filter(
            Tender.deadline.isnot(None),
            Tender.deadline <= upcoming_deadline,
            Tender.deadline >= datetime.utcnow().date()
        ).scalar()

        # Recent tenders (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_tenders = db.query(func.count(Tender.id)).filter(
            Tender.created_at >= week_ago
        ).scalar()

        # Average budget (where available)
        avg_budget = db.query(func.avg(Tender.budget)).filter(
            Tender.budget.isnot(None)
        ).scalar()

        return {
            "total_tenders": total_tenders or 0,
            "upcoming_tenders": upcoming_tenders or 0,
            "recent_tenders": recent_tenders or 0,
            "average_budget": float(avg_budget) if avg_budget else None
        }


analytics_aggregator = AnalyticsAggregator()
