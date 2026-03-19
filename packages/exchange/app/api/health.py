"""Health check endpoint."""

from datetime import datetime

from fastapi import APIRouter, Depends

router = APIRouter()


@router.get("/health")
async def health_check() -> dict:
    """Check exchange health: database and Redis connectivity."""
    from app.main import redis_client, SessionLocal

    health = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {"database": False, "redis": False},
    }

    # Check database
    try:
        async with SessionLocal() as session:
            await session.execute("SELECT 1")
        health["services"]["database"] = True
    except Exception as e:
        health["status"] = "degraded"
        health["database_error"] = str(e)

    # Check Redis
    try:
        await redis_client.ping()
        health["services"]["redis"] = True
    except Exception as e:
        health["status"] = "degraded"
        health["redis_error"] = str(e)

    return health
