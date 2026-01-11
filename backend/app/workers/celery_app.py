"""
Celery application configuration for async task processing.
"""

from celery import Celery
from app.config import settings
import ssl


def get_redis_url_with_ssl_params(url: str) -> str:
    """Add SSL certificate parameters to rediss:// URLs."""
    if url and url.startswith('rediss://'):
        # Add SSL certificate requirement parameter if using SSL
        if 'ssl_cert_reqs' not in url:
            separator = '&' if '?' in url else '?'
            # Use string "none", not ssl.CERT_NONE (which is integer 0)
            url = f"{url}{separator}ssl_cert_reqs=none"
    return url


# Get Redis URLs with SSL parameters if needed
broker_url = get_redis_url_with_ssl_params(settings.CELERY_BROKER_URL or settings.REDIS_URL)
backend_url = get_redis_url_with_ssl_params(settings.CELERY_RESULT_BACKEND or settings.REDIS_URL)

# Create Celery app
celery_app = Celery(
    "tenderlens_worker",
    broker=broker_url,
    backend=backend_url,
    include=[
        "app.workers.ai_tasks",
        "app.workers.embedding_tasks",
        "app.workers.cleanup_tasks"
    ]
)

# Configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,  # 10 minutes max per task
    task_soft_time_limit=540,  # Soft limit at 9 minutes
    worker_prefetch_multiplier=1,  # Disable prefetching for long-running tasks
    worker_max_tasks_per_child=50,  # Restart worker after 50 tasks (prevent memory leaks)
    task_acks_late=True,  # Acknowledge tasks after completion
    task_reject_on_worker_lost=True,  # Requeue tasks if worker dies
    result_expires=3600,  # Task results expire after 1 hour
)

# Configure task routes
celery_app.conf.task_routes = {
    "app.workers.ai_tasks.process_tender_ai_task": {"queue": "ai_processing"},
    "app.workers.ai_tasks.batch_process_tenders_task": {"queue": "batch_processing"},
    "generate_tender_embedding": {"queue": "embeddings"},
    "generate_profile_embedding": {"queue": "embeddings"},
    "batch_generate_embeddings": {"queue": "batch_embeddings"},
    "expire_old_tenders": {"queue": "maintenance"},
}

# Configure beat schedule for periodic tasks
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    # Daily cleanup: expire old tenders at 2 AM
    'expire-old-tenders-daily': {
        'task': 'expire_old_tenders',
        'schedule': crontab(hour=2, minute=0),  # 2:00 AM daily
    },
}
