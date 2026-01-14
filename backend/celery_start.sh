#!/bin/bash
set -e  # Exit on any error

echo "Starting TenderLens Celery Worker..."

# Optional: Simple DB wait (if your tasks need Postgres)
echo "Waiting for database (optional)..."
python -c "
import time
import sys
from sqlalchemy import create_engine
from app.config import settings

max_retries = 30
retry_interval = 2

for i in range(max_retries):
    try:
        engine = create_engine(settings.DATABASE_URL)
        engine.connect()
        print('Database is ready!')
        sys.exit(0)
    except Exception as e:
        if i < max_retries - 1:
            print(f'DB not ready yet, retrying in {retry_interval}s... ({i+1}/{max_retries})')
            time.sleep(retry_interval)
        else:
            print('DB connection failed after retries - continuing anyway for worker')
            sys.exit(0)  # Don't fail worker if DB wait fails
"

# Run Celery worker
echo "Launching Celery worker..."
exec celery -A app.workers.celery_app worker \
  --loglevel=info \
  --concurrency=2 \
  -Q celery,ai_processing,batch_processing,embeddings,batch_embeddings,maintenance