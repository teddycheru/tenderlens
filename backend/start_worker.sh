#!/bin/bash
# Celery Worker Startup Script for TenderLens

echo "Starting TenderLens Celery Worker..."

# Wait for Redis to be ready
echo "Waiting for Redis..."
python3 << END
import time
import sys
from app.config import settings
from redis import Redis

max_retries = 30
for i in range(max_retries):
    try:
        redis_url = settings.CELERY_BROKER_URL or settings.REDIS_URL
        if redis_url:
            # Extract host and port from URL
            from urllib.parse import urlparse
            parsed = urlparse(redis_url)
            client = Redis(host=parsed.hostname, port=parsed.port or 6379, socket_connect_timeout=5)
            client.ping()
            print("✅ Redis is ready!")
            sys.exit(0)
    except Exception as e:
        print(f"Waiting for Redis... ({i+1}/{max_retries})")
        time.sleep(2)

print("❌ Redis is not available")
sys.exit(1)
END

# Start Celery worker
echo "Starting Celery worker..."
celery -A app.workers.celery_app.celery_app worker \
    --loglevel=info \
    --concurrency=2 \
    --max-tasks-per-child=50 \
    --task-events \
    --without-gossip \
    --without-mingle \
    --without-heartbeat
