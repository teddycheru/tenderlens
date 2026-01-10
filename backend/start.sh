#!/bin/bash
set -e

echo "Starting TenderLens Backend..."

# Wait for database to be ready
echo "Waiting for database..."
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
            print(f'Database not ready yet, retrying in {retry_interval}s... ({i+1}/{max_retries})')
            time.sleep(retry_interval)
        else:
            print(f'Failed to connect to database after {max_retries} attempts')
            sys.exit(1)
"

# Handle database migrations
echo "Setting up database schema..."

# Check if alembic_version table exists
DB_HAS_ALEMBIC=$(python -c "
from sqlalchemy import create_engine, inspect
from app.config import settings
try:
    engine = create_engine(settings.DATABASE_URL)
    inspector = inspect(engine)
    print('yes' if 'alembic_version' in inspector.get_table_names() else 'no')
except Exception:
    print('no')
" 2>/dev/null)

if [ "$DB_HAS_ALEMBIC" = "no" ]; then
    # First deployment - mark all migrations as applied
    echo "First deployment - marking all migrations as applied..."
    alembic stamp head
else
    # Run any new migrations
    echo "Running database migrations..."
    alembic upgrade head
fi

# Start the application
echo "Starting FastAPI application..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
