"""
AI processing API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from app.core.dependencies import get_db, get_current_active_user
from app.schemas.ai import (
    AIProcessRequest,
    AIProcessResponse,
    QuickScanRequest,
    QuickScanResponse,
    AIStatusResponse,
    BatchProcessRequest,
    BatchProcessResponse
)
from app.services.ai.ai_service import ai_service
from app.models.user import User


router = APIRouter()


@router.post("/process", response_model=AIProcessResponse, summary="Process tender with AI")
async def process_tender(
    request: AIProcessRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Process tender with AI (summarization + entity extraction).

    Can run synchronously or asynchronously depending on document size and complexity.
    - For simple tenders (description only): processes immediately
    - For documents with URLs: queues background task

    Returns processing results or task ID for async jobs.
    """
    from app.models.tender import Tender

    # Verify tender exists
    tender = db.query(Tender).filter(Tender.id == request.tender_id).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")

    # Check if already processed (unless force reprocess)
    if tender.ai_processed and not request.force_reprocess:
        return AIProcessResponse(
            tender_id=str(tender.id),
            summary=tender.ai_summary,
            entities=tender.extracted_entities,
            quick_scan=tender.ai_summary[:100] if tender.ai_summary else None,
            cached=True
        )

    # Always use async processing to prevent blocking the API
    # This allows the AI button to return immediately to the user
    from app.workers.ai_tasks import process_tender_ai_task

    doc_url = request.doc_url or (tender.doc_url if hasattr(tender, 'doc_url') else None)

    # Queue AI processing task (works for both document and text-only tenders)
    task = process_tender_ai_task.delay(
        str(tender.id),
        doc_url=doc_url,
        force_reprocess=request.force_reprocess
    )

    return AIProcessResponse(
        tender_id=str(tender.id),
        summary=None,
        entities=None,
        quick_scan="Processing in background...",
        task_id=task.id
    )


@router.get("/status/{tender_id}", response_model=AIStatusResponse, summary="Get AI processing status")
def get_ai_status(
    tender_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get AI processing status for a tender.

    Returns whether the tender has been processed, and what AI data is available.
    """
    try:
        status = ai_service.get_processing_status(db, tender_id)
        return AIStatusResponse(**status)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")


@router.get("/result/{tender_id}", response_model=AIProcessResponse, summary="Get AI processing results")
def get_ai_results(
    tender_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get AI processing results for a tender.

    Returns the full AI processing results including summary and entities.
    """
    from app.models.tender import Tender

    tender = db.query(Tender).filter(Tender.id == tender_id).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")

    return AIProcessResponse(
        tender_id=str(tender.id),
        summary=tender.ai_summary,
        entities=tender.extracted_entities,
        quick_scan=tender.ai_summary[:100] if tender.ai_summary else None,
        cached=True
    )


@router.post("/quick-scan", response_model=QuickScanResponse, summary="Generate quick scan")
def generate_quick_scan(
    request: QuickScanRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate quick scan for tender preview.

    Provides a brief 1-2 sentence insight without full processing.
    Useful for tender cards and list views.
    """
    from app.services.ai.summarizer import summarizer

    if not summarizer.is_available():
        raise HTTPException(
            status_code=503,
            detail="AI service not available. Please configure API keys in .env file."
        )

    try:
        quick_scan = summarizer.quick_scan(request.title, request.description)
        return QuickScanResponse(quick_scan=quick_scan)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quick scan failed: {str(e)}")


@router.post("/batch-process", response_model=BatchProcessResponse, summary="Batch process tenders")
async def batch_process_tenders(
    request: BatchProcessRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Process multiple tenders in batch.

    Queues all tenders for async processing and returns task IDs.
    Use /api/v1/ai/task/{task_id} to check progress.
    """
    from app.workers.ai_tasks import batch_process_tenders_task

    # Verify all tenders exist
    from app.models.tender import Tender
    existing_ids = db.query(Tender.id).filter(Tender.id.in_(request.tender_ids)).all()
    existing_ids = [str(id[0]) for id in existing_ids]

    if len(existing_ids) != len(request.tender_ids):
        raise HTTPException(
            status_code=404,
            detail=f"Some tenders not found. Found {len(existing_ids)} of {len(request.tender_ids)}"
        )

    # Queue batch processing
    result = batch_process_tenders_task(existing_ids)
    return BatchProcessResponse(**result)


@router.delete("/cache/{tender_id}", summary="Invalidate AI cache")
def invalidate_cache(
    tender_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Invalidate cached AI results for a tender.

    Forces reprocessing on next AI request.
    """
    success = ai_service.invalidate_cache(tender_id)
    if success:
        return {"message": f"Cache invalidated for tender {tender_id}"}
    else:
        raise HTTPException(status_code=500, detail="Failed to invalidate cache")


@router.get("/health", summary="Check AI service health")
def check_ai_health():
    """
    Check if AI services are available and properly configured.

    Returns status of summarizer and entity extractor.
    """
    from app.services.ai.summarizer import summarizer
    from app.services.ai.entity_extractor import entity_extractor
    from app.core.ai_config import ai_settings

    return {
        "ai_enabled": ai_settings.AI_ENABLED,
        "summarizer_available": summarizer.is_available(),
        "summarizer_provider": summarizer.provider if summarizer.is_available() else None,
        "entity_extractor_available": entity_extractor.is_available(),
        "cache_available": True,  # Redis cache is always available (graceful degradation)
    }
