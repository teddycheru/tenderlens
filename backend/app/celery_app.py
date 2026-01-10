# backend/app/celery_app.py
"""
Celery application configuration for async tasks and scheduling.
"""

from celery import Celery
from celery.schedules import crontab
from app.config import settings

# Create Celery app
celery_app = Celery(
    "tenderlens",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Celery Beat schedule (periodic tasks)
celery_app.conf.beat_schedule = {
    # Run scrapers every 6 hours
    "scrape-tenders-every-6-hours": {
        "task": "app.workers.scraper_tasks.run_all_scrapers",
        "schedule": crontab(minute=0, hour="*/6"),  # Every 6 hours
    },
    # Clean up old staging records daily
    "cleanup-staging-daily": {
        "task": "app.workers.pipeline_tasks.cleanup_old_staging",
        "schedule": crontab(hour=2, minute=0),  # 2 AM daily
    },
}

# Auto-discover tasks
celery_app.autodiscover_tasks(["app.workers"])
