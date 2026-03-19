"""Database configuration and session factory."""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings

# Initialize as None - will be set during app startup
engine = None
SessionLocal = None


async def init_db():
    """Initialize database engine and session factory."""
    global engine, SessionLocal
    
    engine = create_async_engine(
        settings.database_url,
        echo=settings.environment == "development",
        pool_pre_ping=True,
        pool_size=20,
        max_overflow=10,
    )
    
    SessionLocal = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    # Create all tables
    from app.models.base import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Close database connection pool."""
    global engine
    if engine:
        await engine.dispose()


async def get_session() -> AsyncSession:
    """Dependency for getting database session."""
    if not SessionLocal:
        raise RuntimeError("Database not initialized")
    
    async with SessionLocal() as session:
        yield session
