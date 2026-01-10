# backend/app/api/v1/pipeline.py
"""
Pipeline admin API endpoints for monitoring and management.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict
from datetime import datetime, timedelta

from app.database import get_db
from app.models.scrape_log import ScrapeLog
from app.models.tender_staging import TenderStaging
from app.services.data_quality.metrics import data_quality_metrics

router = APIRouter(prefix="/pipeline", tags=["pipeline"])


@router.get("/scrape-logs", response_model=List[Dict])
def get_scrape_logs(
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Get recent scrape logs.

    Args:
        limit: Number of logs to return (default: 20)

    Returns:
        List of scrape logs
    """
    logs = db.query(ScrapeLog).order_by(
        ScrapeLog.started_at.desc()
    ).limit(limit).all()

    return [
        {
            "id": log.id,
            "source": log.source,
            "status": log.status,
            "tenders_found": log.tenders_found,
            "tenders_loaded": log.tenders_loaded,
            "tenders_duplicate": log.tenders_duplicate,
            "data_quality_score": log.data_quality_score,
            "started_at": log.started_at,
            "completed_at": log.completed_at,
            "duration_seconds": log.duration_seconds()
        }
        for log in logs
    ]


@router.get("/scrape-logs/{scrape_run_id}", response_model=Dict)
def get_scrape_log_details(
    scrape_run_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific scrape run.

    Args:
        scrape_run_id: ID of scrape run

    Returns:
        Detailed scrape log information
    """
    log = db.query(ScrapeLog).filter(ScrapeLog.id == scrape_run_id).first()

    if not log:
        raise HTTPException(status_code=404, detail="Scrape log not found")

    # Get quality metrics
    quality_metrics = data_quality_metrics.calculate_scrape_quality(db, scrape_run_id)

    return {
        "id": log.id,
        "source": log.source,
        "status": log.status,
        "tenders_found": log.tenders_found,
        "tenders_validated": log.tenders_validated,
        "tenders_validation_failed": log.tenders_validation_failed,
        "tenders_duplicate": log.tenders_duplicate,
        "tenders_loaded": log.tenders_loaded,
        "data_quality_score": log.data_quality_score,
        "quality_metrics": quality_metrics,
        "errors": log.errors,
        "started_at": log.started_at,
        "completed_at": log.completed_at,
        "duration_seconds": log.duration_seconds()
    }


@router.get("/staging-status", response_model=Dict)
def get_staging_status(
    db: Session = Depends(get_db)
):
    """
    Get current status of staging table.

    Returns:
        Staging record counts by status
    """
    total = db.query(TenderStaging).count()
    pending = db.query(TenderStaging).filter(TenderStaging.status == "pending").count()
    validated = db.query(TenderStaging).filter(TenderStaging.status == "validated").count()
    loaded = db.query(TenderStaging).filter(TenderStaging.status == "loaded").count()
    failed = db.query(TenderStaging).filter(TenderStaging.status == "failed").count()
    duplicate = db.query(TenderStaging).filter(TenderStaging.status == "duplicate").count()

    return {
        "total": total,
        "pending": pending,
        "validated": validated,
        "loaded": loaded,
        "failed": failed,
        "duplicate": duplicate
    }


@router.get("/validation-errors", response_model=Dict)
def get_validation_errors(
    days: int = 7,
    db: Session = Depends(get_db)
):
    """
    Get summary of validation errors.

    Args:
        days: Number of days to analyze (default: 7)

    Returns:
        Validation error summary
    """
    summary = data_quality_metrics.get_validation_error_summary(db, days)
    return summary
