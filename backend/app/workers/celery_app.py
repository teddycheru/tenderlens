"""
Celery application configuration for async task processing with Upstash Redis.
"""

from celery import Celery
import ssl
import os
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Get Redis URL - prefer CELERY_BROKER_URL if set, fallback to REDIS_URL
redis_url = (
    settings.CELERY_BROKER_URL
    or settings.REDIS_URL
    or os.getenv("REDIS_URL")
)

if not redis_url:
    logger.warning("No REDIS_URL found in environment or settings! Celery may fail to connect.")
elif not redis_url.startswith('rediss://'):
    logger.warning(
        f"REDIS_URL '{redis_url}' does not start with 'rediss://'. "
        "Upstash requires TLS - this may cause connection failures."
    )
else:
    logger.info(f"Using Redis URL for Celery: {redis_url}")

# Create Celery app
celery_app = Celery(
    "tenderlens_worker",
    broker=redis_url,
    backend=redis_url,
    include=[
        "app.workers.ai_tasks",
        "app.workers.embedding_tasks",
        "app.workers.cleanup_tasks"
    ]
)

# Critical: Explicit SSL for Upstash (fixes "Connection closed by server" in Kombu)
celery_app.conf.update(
    # Broker SSL (task queue)
    broker_use_ssl={
        'ssl_cert_reqs': ssl.CERT_REQUIRED,
        'ssl_ca_certs': None,
        'ssl_certfile': None,
        'ssl_keyfile': None,
    },

    # Result backend SSL
    redis_backend_use_ssl={
        'ssl_cert_reqs': ssl.CERT_REQUIRED,
        'ssl_ca_certs': None,
        'ssl_certfile': None,
        'ssl_keyfile': None,
    },

    # Serverless Redis resilience
    broker_connection_retry_on_startup=True,
    broker_connection_max_retries=None,           # infinite retries
    broker_pool_limit=None,                       # disable pooling
    broker_transport_options={
        'visibility_timeout': 3600,               # 1 hour
    },

    # Your original config
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,
    task_soft_time_limit=540,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    result_expires=3600,
)

# Task routes (unchanged)
celery_app.conf.task_routes = {
    "app.workers.ai_tasks.process_tender_ai_task": {"queue": "ai_processing"},
    "app.workers.ai_tasks.batch_process_tenders_task": {"queue": "batch_processing"},
    "generate_tender_embedding": {"queue": "embeddings"},
    "generate_profile_embedding": {"queue": "embeddings"},
    "batch_generate_embeddings": {"queue": "batch_embeddings"},
    "expire_old_tenders": {"queue": "maintenance"},
}

# Beat schedule (unchanged)
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    'expire-old-tenders-daily': {
        'task': 'expire_old_tenders',
        'schedule': crontab(hour=2, minute=0),
    },
}