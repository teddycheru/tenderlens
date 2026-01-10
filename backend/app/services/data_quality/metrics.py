# backend/app/services/data_quality/metrics.py
"""
Calculate and track data quality metrics for monitoring.
"""

from typing import Dict
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.tender_staging import TenderStaging
from app.models.validation_error import ValidationError
from datetime import datetime, timedelta


class DataQualityMetrics:
    """Calculate data quality metrics for pipeline monitoring."""

    @staticmethod
    def calculate_scrape_quality(db: Session, scrape_run_id: int) -> Dict:
        """
        Calculate quality metrics for a specific scrape run.

        Returns:
            {
                "completeness": 0.95,
                "validity": 0.88,
                "uniqueness": 0.92,
                "timeliness": 0.90,
                "overall_score": 91.25
            }
        """

        # Get all staging records for this scrape run
        total_records = db.query(TenderStaging).filter(
            TenderStaging.scrape_run_id == scrape_run_id
        ).count()

        if total_records == 0:
            return {
                "completeness": 0,
                "validity": 0,
                "uniqueness": 0,
                "timeliness": 0,
                "overall_score": 0,
                "total_records": 0
            }

        # Completeness: % with non-null required fields
        complete_records = db.query(TenderStaging).filter(
            TenderStaging.scrape_run_id == scrape_run_id,
            TenderStaging.status.in_(["validated", "loaded"])
        ).count()
        completeness = (complete_records / total_records) * 100

        # Validity: % passing validation
        valid_records = db.query(TenderStaging).filter(
            TenderStaging.scrape_run_id == scrape_run_id,
            TenderStaging.status.in_(["validated", "transformed", "loaded"])
        ).count()
        validity = (valid_records / total_records) * 100

        # Uniqueness: % not duplicates
        unique_records = db.query(TenderStaging).filter(
            TenderStaging.scrape_run_id == scrape_run_id,
            TenderStaging.is_duplicate == False
        ).count()
        uniqueness = (unique_records / total_records) * 100

        # Timeliness: % processed within 1 hour
        sla_threshold = datetime.utcnow() - timedelta(hours=1)
        timely_records = db.query(TenderStaging).filter(
            TenderStaging.scrape_run_id == scrape_run_id,
            TenderStaging.processed_at.isnot(None)
        ).count()
        timeliness = (timely_records / total_records) * 100 if total_records > 0 else 0

        # Overall score (weighted average)
        overall_score = (
            completeness * 0.3 +
            validity * 0.4 +
            uniqueness * 0.2 +
            timeliness * 0.1
        )

        return {
            "completeness": round(completeness, 2),
            "validity": round(validity, 2),
            "uniqueness": round(uniqueness, 2),
            "timeliness": round(timeliness, 2),
            "overall_score": round(overall_score, 2),
            "total_records": total_records
        }

    @staticmethod
    def get_validation_error_summary(db: Session, days: int = 7) -> Dict:
        """
        Get summary of validation errors over last N days.
        """
        since_date = datetime.utcnow() - timedelta(days=days)

        # Group errors by type
        error_counts = db.query(
            ValidationError.error_type,
            func.count(ValidationError.id).label('count')
        ).filter(
            ValidationError.created_at >= since_date
        ).group_by(ValidationError.error_type).all()

        # Group errors by field
        field_errors = db.query(
            ValidationError.field_name,
            func.count(ValidationError.id).label('count')
        ).filter(
            ValidationError.created_at >= since_date,
            ValidationError.field_name.isnot(None)
        ).group_by(ValidationError.field_name).all()

        return {
            "period_days": days,
            "by_type": [
                {"error_type": row.error_type, "count": row.count}
                for row in error_counts
            ],
            "by_field": [
                {"field_name": row.field_name, "count": row.count}
                for row in field_errors
            ]
        }


data_quality_metrics = DataQualityMetrics()
