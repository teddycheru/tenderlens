"""
Database configuration and session management using SQLAlchemy 2.0.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool
from pgvector.psycopg2 import register_vector

from app.config import settings

# Create database engine with connection pooling
# Increased pool_size and max_overflow to handle concurrent requests better
# pool_size: 20 connections in the pool
# max_overflow: 20 additional connections when needed (up to 40 total)
engine = create_engine(
    settings.get_db_url(),
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before using
    echo=False,  # Set to True for SQL query logging
    pool_recycle=3600,  # Recycle connections after 1 hour to prevent stale connections
)

# Register pgvector type for each new connection
@event.listens_for(engine, "connect")
def register_vector_type(dbapi_conn, connection_record):
    """Register pgvector type for psycopg2 connections."""
    register_vector(dbapi_conn)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for ORM models
Base = declarative_base()


def get_db():
    """
    Dependency function to get database session.
    Yields a database session and ensures it's closed after use.

    Usage in FastAPI endpoints:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    Create all database tables.
    Used for development/testing. In production, use Alembic migrations.
    """
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """
    Drop all database tables.
    Use with caution - for testing purposes only.
    """
    Base.metadata.drop_all(bind=engine)
