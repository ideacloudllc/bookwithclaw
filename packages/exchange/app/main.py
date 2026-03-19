"""FastAPI application for BookWithClaw Exchange."""

import logging
from contextlib import asynccontextmanager

import redis.asyncio as redis
from fastapi import FastAPI
from sqlalchemy import text

from app.config import settings
from app import database  # Initialize database module first

# Now safe to import routers that depend on database
from app.api.agents import router as agents_router
from app.api.health import router as health_router
from app.api.sessions import router as sessions_router
from app.api.landing import router as landing_router
from app.api.seller_dashboard import router as seller_dashboard_router
from app.api.dashboard_ui import router as dashboard_ui_router

logger = logging.getLogger(__name__)

# Global redis client (database handled by database module)
redis_client = None


async def get_db():
    """Get database session from database module."""
    async with database.SessionLocal() as session:
        yield session


async def get_redis():
    """Get Redis client."""
    return redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan: startup and shutdown."""
    global redis_client

    # Startup
    logger.info("Starting BookWithClaw Exchange...")

    # Initialize database via database module
    await database.init_db()

    # Initialize Redis
    redis_client = await redis.from_url(settings.redis_url, decode_responses=True)

    # Test connections
    try:
        async with database.SessionLocal() as session:
            await session.execute(text("SELECT 1"))
        logger.info("✓ PostgreSQL connected")
    except Exception as e:
        logger.error(f"✗ PostgreSQL connection failed: {e}")
        raise

    try:
        await redis_client.ping()
        logger.info("✓ Redis connected")
    except Exception as e:
        logger.error(f"✗ Redis connection failed: {e}")
        raise

    logger.info("✓ Exchange ready")
    yield

    # Shutdown
    logger.info("Shutting down BookWithClaw Exchange...")
    await database.close_db()
    if redis_client:
        await redis_client.close()
    logger.info("✓ Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="BookWithClaw Exchange",
    description="Agent-to-agent negotiation exchange with atomic settlement",
    version="0.1.0",
    lifespan=lifespan,
)

# Include routers
app.include_router(landing_router)           # Landing pages (sellers signup, home)
app.include_router(health_router)            # Health check
app.include_router(agents_router)            # Agent registration
app.include_router(seller_dashboard_router)  # Seller dashboard API
app.include_router(dashboard_ui_router)      # Seller dashboard UI
app.include_router(sessions_router)          # Negotiation sessions


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.exchange_host,
        port=settings.exchange_port,
        reload=settings.environment == "development",
    )
