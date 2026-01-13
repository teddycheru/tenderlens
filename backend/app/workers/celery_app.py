"""
Celery application configuration for async task processing with Upstash Redis.
"""

from celery import Celery
import ssl
from app.config import settings


# Use the raw REDIS_URL from settings (should already contain ?ssl_cert_reqs=required)
redis_url = settings.REDIS_URL or settings.CELERY_BROKER_URL

# Safety check - make sure we're using TLS
if not redis_url or not redis_url.startswith('rediss://'):
    raise ValueError(
        "REDIS_URL must start with 'rediss://' for Upstash. "
        "Example: rediss://default:password@host:6379?ssl_cert_reqs=required"
    )

print(f"Using Redis URL for Celery: {redis_url}")

# Create Celery app
celery_app = Celery(
    "tenderlens_worker",
    broker=redis_url,
    backend=redis_url,  # same Redis instance for results (common & efficient)
    include=[
        "app.workers.ai_tasks",
        "app.workers.embedding_tasks",
        "app.workers.cleanup_tasks"
    ]
)

# Critical: Explicit SSL configuration required for Upstash + Celery/Kombu
celery_app.conf.update(
    # === SSL for broker (task queue) ===
    broker_use_ssl={
        'ssl_cert_reqs': ssl.CERT_REQUIRED,     # strict verification (recommended)
        'ssl_ca_certs': None,                   # Upstash uses public CA
        'ssl_certfile': None,
        'ssl_keyfile': None,
    },

    # === SSL for result backend ===
    redis_backend_use_ssl={
        'ssl_cert_reqs': ssl.CERT_REQUIRED,
        'ssl_ca_certs': None,
        'ssl_certfile': None,
        'ssl_keyfile': None,
    },

    # === Connection resilience (very important for serverless Redis like Upstash) ===
    broker_connection_retry_on_startup=True,
    broker_connection_max_retries=None,           # retry forever during startup
    broker_pool_limit=None,                       # disable connection pooling
    broker_transport_options={
        'visibility_timeout': 3600,               # 1 hour - prevents task loss on long tasks
    },

    # === Your existing good settings ===
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,          # 10 minutes max per task
    task_soft_time_limit=540,     # Soft limit at 9 minutes
    worker_prefetch_multiplier=1, # No prefetching for long-running tasks
    worker_max_tasks_per_child=50,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    result_expires=3600,          # Results expire after 1 hour
)

# Task routes
celery_app.conf.task_routes = {
    "app.workers.ai_tasks.process_tender_ai_task": {"queue": "ai_processing"},
    "app.workers.ai_tasks.batch_process_tenders_task": {"queue": "batch_processing"},
    "generate_tender_embedding": {"queue": "embeddings"},
    "generate_profile_embedding": {"queue": "embeddings"},
    "batch_generate_embeddings": {"queue": "batch_embeddings"},
    "expire_old_tenders": {"queue": "maintenance"},
}

# Periodic tasks (beat schedule)
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    'expire-old-tenders-daily': {
        'task': 'expire_old_tenders',
        'schedule': crontab(hour=2, minute=0),  # 2:00 AM daily
    },
}