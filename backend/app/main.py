"""
FastAPI application entry point for TenderLens Backend.
"""

import os
import redis
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import create_tables
from app.api.v1 import api_router

# Create main FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*\.vercel\.app",  # Allow all Vercel domains
    allow_origins=settings.BACKEND_CORS_ORIGINS,     # Additional origins from settings
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Helper function to test Redis connection
def test_redis_connection():
    """
    Test connection to Redis (Upstash) using the REDIS_URL environment variable.
    Prints detailed info to logs for debugging.
    """
    redis_url = os.getenv("REDIS_URL")
    
    if not redis_url:
        print("⚠️  REDIS_URL environment variable is NOT set!")
        return False

    print(f"🔍 Testing Redis connection...")
    print(f"   URL: {redis_url.replace(os.getenv('REDIS_PASSWORD', ''), '***') if 'REDIS_PASSWORD' in os.environ else redis_url}")

    try:
        # Create Redis client with sensible timeouts for serverless (Upstash)
        client = redis.from_url(
            redis_url,
            decode_responses=True,
            socket_timeout=5,
            socket_connect_timeout=5,
            socket_keepalive=True,
            retry_on_timeout=True,
            health_check_interval=30,
        )

        # Basic ping test
        pong = client.ping()
        print("✅ Redis PING successful!")

        # Optional: Test write/read cycle
        client.setex("render_test_key", 60, "connection_works")
        value = client.get("render_test_key")
        print(f"   Read/write test: {value}")

        # Optional: Get server info (helpful for debugging)
        server_info = client.info("server")
        print(f"   Redis mode: {server_info.get('redis_mode', 'unknown')}")
        print(f"   Redis version: {server_info.get('redis_version', 'unknown')}")

        return True

    except redis.exceptions.ConnectionError as e:
        print(f"❌ Redis connection FAILED (ConnectionError): {str(e)}")
        return False
    except redis.exceptions.AuthenticationError as e:
        print(f"❌ Redis authentication FAILED: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during Redis test: {str(e)}")
        return False


@app.on_event("startup")
async def startup_event():
    """
    Actions to perform when the FastAPI application starts.
    """
    # Create database tables (safe - won't error if already exist)
    create_tables()

    # Test Redis connection
    redis_ok = test_redis_connection()
    
    if redis_ok:
        print(f"✅ {settings.PROJECT_NAME} Redis connection verified")
    else:
        print(f"⚠️  {settings.PROJECT_NAME} Redis connection test failed - check logs!")

    print(f"✅ {settings.PROJECT_NAME} started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Actions to perform when the FastAPI application shuts down.
    """
    print(f"👋 {settings.PROJECT_NAME} shutting down")


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to TenderLens API",
        "version": settings.VERSION,
        "docs": f"{settings.API_V1_STR}/docs"
    }


# Health check (used by Render)
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }


# API v1 root info
@app.get(f"{settings.API_V1_STR}/")
async def api_root():
    return {
        "message": "TenderLens API v1",
        "endpoints": {
            "docs": f"{settings.API_V1_STR}/docs",
            "health": "/health",
            "auth": f"{settings.API_V1_STR}/auth"
        }
    }


# ────────────────────────────────────────────────
# Optional: Add this endpoint for manual Redis testing
# ────────────────────────────────────────────────
test_router = APIRouter(prefix=settings.API_V1_STR, tags=["debug"])

@test_router.get("/test-redis")
async def api_test_redis():
    """
    Manual endpoint to test Redis connection from the running instance.
    Useful for debugging on Render.
    """
    redis_url = os.getenv("REDIS_URL")
    
    if not redis_url:
        return {"status": "error", "message": "REDIS_URL not set"}

    try:
        client = redis.from_url(redis_url, decode_responses=True)
        pong = client.ping()
        
        client.setex("api_test_key", 60, "works")
        value = client.get("api_test_key")

        return {
            "status": "success",
            "ping": pong,
            "write_read_test": value,
            "redis_url": redis_url.replace(os.getenv('REDIS_PASSWORD', ''), '***') if 'REDIS_PASSWORD' in os.environ else redis_url
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "redis_url": redis_url.replace(os.getenv('REDIS_PASSWORD', ''), '***') if 'REDIS_PASSWORD' in os.environ else redis_url
        }

# Include the test router
app.include_router(test_router)