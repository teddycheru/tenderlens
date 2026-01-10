"""
FastAPI application entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import create_tables
from app.api.v1 import api_router

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)

# Configure CORS - allow all Vercel preview URLs using regex
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*\.vercel\.app",  # Allow all Vercel preview and production URLs
    allow_origins=settings.BACKEND_CORS_ORIGINS,  # Also allow specific origins (localhost, etc.)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.on_event("startup")
async def startup_event():
    """
    Execute on application startup.
    """
    # Create database tables if they don't exist
    # (safe to call - won't error if tables already exist)
    create_tables()
    print(f"✅ {settings.PROJECT_NAME} started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Execute on application shutdown.
    """
    print(f"👋 {settings.PROJECT_NAME} shutting down")


@app.get("/")
async def root():
    """
    Root endpoint - API health check.
    """
    return {
        "message": "Welcome to TenderLens API",
        "version": settings.VERSION,
        "docs": f"{settings.API_V1_STR}/docs"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    """
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }


@app.get(f"{settings.API_V1_STR}/")
async def api_root():
    """
    API v1 root endpoint.
    """
    return {
        "message": "TenderLens API v1",
        "endpoints": {
            "docs": f"{settings.API_V1_STR}/docs",
            "health": "/health",
            "auth": f"{settings.API_V1_STR}/auth"
        }
    }
