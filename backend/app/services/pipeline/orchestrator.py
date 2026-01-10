# backend/app/services/pipeline/orchestrator.py
"""
Pipeline Orchestrator - Coordinates all ETL stages.
This is the main entry point for processing scraped data.
"""

from sqlalchemy.orm import Session
from typing import Dict
import time
import logging
from datetime import datetime

from app.models.tender_staging import TenderStaging
from app.models.scrape_log import ScrapeLog
from app.services.data_quality.validators import data_validator
from app.services.data_quality.metrics import data_quality_metrics
from app.services.pipeline.transformer import tender_transformer
from app.services.pipeline.deduplicator import tender_deduplicator
from app.services.pipeline.loader import tender_loader

logger = logging.getLogger(__name__)


class PipelineOrchestrator:
    """
    Orchestrate the complete ETL pipeline:
    1. Extract: Get records from staging
    2. Validate: Check data quality
    3. Transform: Normalize and clean
    4. Deduplicate: Check for duplicates
    5. Load: Insert into production
    6. Post-process: Trigger AI and alerts
    """

    def process_scrape_run(self, db: Session, scrape_run_id: int) -> Dict:
        """
        Process all staging records for a scrape run through the pipeline.

        Args:
            db: Database session
            scrape_run_id: ID of scrape run to process

        Returns:
            Pipeline execution summary
        """

        start_time = time.time()

        # Get scrape log
        scrape_log = db.query(ScrapeLog).filter(
            ScrapeLog.id == scrape_run_id
        ).first()

        if not scrape_log:
            return {"error": "Scrape run not found"}

        # Get all pending staging records
        staging_records = db.query(TenderStaging).filter(
            TenderStaging.scrape_run_id == scrape_run_id,
            TenderStaging.status == "pending"
        ).all()

        if not staging_records:
            return {
                "scrape_run_id": scrape_run_id,
                "message": "No pending records to process",
                "records_processed": 0
            }

        # Process each record through pipeline
        results = {
            "validated": 0,
            "validation_failed": 0,
            "transformed": 0,
            "duplicates": 0,
            "loaded": 0,
            "errors": []
        }

        for record in staging_records:
            try:
                # STAGE 2: Validate
                validation_result = data_validator.validate_tender(record.raw_data)

                if not validation_result["is_valid"]:
                    record.status = "failed"
                    record.validation_errors = validation_result["errors"]
                    results["validation_failed"] += 1
                    continue

                record.status = "validated"
                record.quality_score = validation_result["quality_score"]
                record.validated_at = datetime.utcnow()
                results["validated"] += 1

                # STAGE 3: Transform
                transformed_data = tender_transformer.transform(record.raw_data)

                if not transformed_data:
                    record.status = "failed"
                    results["errors"].append(f"Transformation failed for record {record.id}")
                    continue

                record.status = "transformed"
                record.transformed_at = datetime.utcnow()
                results["transformed"] += 1

                # STAGE 4: Deduplicate
                is_duplicate, duplicate_info = tender_deduplicator.check_duplicate(db, transformed_data)

                if is_duplicate:
                    record.is_duplicate = True
                    record.duplicate_of_tender_id = duplicate_info.get("tender_id")
                    record.duplicate_reason = duplicate_info.get("method")
                    record.duplicate_similarity_score = duplicate_info.get("score")
                    record.status = "duplicate"
                    results["duplicates"] += 1

                    # Log duplicate
                    tender_deduplicator.log_duplicate(db, record.id, duplicate_info)
                    continue

                # STAGE 5: Load
                tender = tender_loader.load(db, transformed_data, record)

                if tender:
                    record.status = "loaded"
                    record.processed_at = datetime.utcnow()
                    results["loaded"] += 1

            except Exception as e:
                record.status = "failed"
                record.transformation_errors = [str(e)]
                results["errors"].append(f"Error processing record {record.id}: {str(e)}")

            finally:
                db.commit()

        # Update scrape log with metrics
        total_time = time.time() - start_time
        quality_metrics = data_quality_metrics.calculate_scrape_quality(db, scrape_run_id)

        scrape_log.tenders_validated = results["validated"]
        scrape_log.tenders_validation_failed = results["validation_failed"]
        scrape_log.tenders_duplicate = results["duplicates"]
        scrape_log.tenders_loaded = results["loaded"]
        scrape_log.total_pipeline_time_seconds = total_time
        scrape_log.data_quality_score = quality_metrics["overall_score"]
        scrape_log.quality_metrics = quality_metrics
        db.commit()

        # ===== STAGE 6: Auto-process newly loaded tenders with AI =====
        # Queue AI processing for all successfully loaded tenders
        if results["loaded"] > 0:
            try:
                from app.workers.ai_tasks import batch_process_tenders_task

                # Get all newly loaded tenders from this scrape run
                loaded_records = db.query(TenderStaging).filter(
                    TenderStaging.scrape_run_id == scrape_run_id,
                    TenderStaging.status == "loaded",
                    TenderStaging.tender_id.isnot(None)
                ).all()

                tender_ids = [str(record.tender_id) for record in loaded_records]

                if tender_ids:
                    logger.info(f"🤖 Queuing AI processing for {len(tender_ids)} newly loaded tenders")
                    # Queue batch processing task
                    batch_process_tenders_task.delay(tender_ids)
                    results["ai_queued"] = len(tender_ids)
                else:
                    results["ai_queued"] = 0
            except Exception as e:
                logger.warning(f"Failed to queue AI processing: {e}")
                results["ai_queued"] = 0

        return {
            "scrape_run_id": scrape_run_id,
            "records_processed": len(staging_records),
            "results": results,
            "quality_metrics": quality_metrics,
            "total_time_seconds": round(total_time, 2)
        }


pipeline_orchestrator = PipelineOrchestrator()
