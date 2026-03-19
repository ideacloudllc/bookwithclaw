"""FastAPI application for BookWithClaw Exchange."""

import logging
from contextlib import asynccontextmanager

import redis.asyncio as redis
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.api.agents import router as agents_router
from app.api.health import router as health_router
from app.api.sessions import router as sessions_router
from app.config import settings

logger = logging.getLogger(__name__)

# Global database and redis connections
engine = None
SessionLocal = None
redis_client = None


async def get_db() -> AsyncSession:
    """Get database session."""
    async with SessionLocal() as session:
        yield session


async def get_redis():
    """Get Redis client."""
    return redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan: startup and shutdown."""
    global engine, SessionLocal, redis_client

    # Startup
    logger.info("Starting BookWithClaw Exchange...")

    # Initialize database
    engine = create_async_engine(
        settings.database_url,
        echo=settings.environment == "development",
        future=True,
    )
    SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Initialize Redis
    redis_client = await redis.from_url(settings.redis_url, decode_responses=True)

    # Test connections
    try:
        async with SessionLocal() as session:
            await session.execute("SELECT 1")
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
    if engine:
        await engine.dispose()
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
app.include_router(health_router)
app.include_router(agents_router)
app.include_router(sessions_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.exchange_host,
        port=settings.exchange_port,
        reload=settings.environment == "development",
    )
