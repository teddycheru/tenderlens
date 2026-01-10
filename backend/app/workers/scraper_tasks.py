# backend/app/workers/scraper_tasks.py
"""
Celery tasks for web scraping tenders.
"""

from celery import Task
from app.celery_app import celery_app
from app.database import SessionLocal
from app.models.scrape_log import ScrapeLog
from app.models.tender_staging import TenderStaging
from app.services.scrapers.base_scraper import SampleScraper
from app.services.pipeline.orchestrator import pipeline_orchestrator
from datetime import datetime


@celery_app.task(bind=True, name="app.workers.scraper_tasks.scrape_portal")
def scrape_portal(self: Task, source_id: str) -> dict:
    """
    Scrape a specific tender portal.

    Args:
        source_id: Identifier for the portal to scrape

    Returns:
        Scraping results summary
    """
    db = SessionLocal()

    try:
        # Create scrape log
        scrape_log = ScrapeLog(
            source=source_id,
            status="running",
            started_at=datetime.utcnow()
        )
        db.add(scrape_log)
        db.commit()
        db.refresh(scrape_log)

        # Initialize scraper (you can expand this with a scraper registry)
        scraper = SampleScraper()

        # Run scraper
        tender_data_list = scraper.scrape()

        # Save to staging
        tenders_saved = 0
        for tender_data in tender_data_list:
            staging_record = TenderStaging(
                source_id=source_id,
                source_name=scraper.source_name,
                source_url=tender_data.get('source_url'),
                scrape_run_id=scrape_log.id,
                raw_data=tender_data,
                status="pending"
            )
            db.add(staging_record)
            tenders_saved += 1

        db.commit()

        # Update scrape log
        scrape_log.status = "success"
        scrape_log.tenders_found = tenders_saved
        scrape_log.completed_at = datetime.utcnow()
        db.commit()

        # Process through pipeline
        pipeline_result = pipeline_orchestrator.process_scrape_run(db, scrape_log.id)

        return {
            "scrape_run_id": scrape_log.id,
            "status": "success",
            "tenders_scraped": tenders_saved,
            "pipeline_results": pipeline_result
        }

    except Exception as e:
        if 'scrape_log' in locals():
            scrape_log.status = "failed"
            scrape_log.errors = [str(e)]
            scrape_log.completed_at = datetime.utcnow()
            db.commit()

        return {
            "status": "failed",
            "error": str(e)
        }
    finally:
        db.close()


@celery_app.task(name="app.workers.scraper_tasks.run_all_scrapers")
def run_all_scrapers() -> dict:
    """
    Run all configured scrapers.
    This task is scheduled to run periodically.
    """
    # List of scraper source IDs to run
    scraper_ids = ["sample_portal"]  # Add more scrapers here

    results = {}
    for source_id in scraper_ids:
        result = scrape_portal.delay(source_id)
        results[source_id] = result.id

    return {
        "status": "scheduled",
        "scrapers": scraper_ids,
        "task_ids": results
    }
