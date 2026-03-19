"""Test configuration and fixtures."""

import asyncio
import os
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Set test environment BEFORE importing app
os.environ.setdefault("ENVIRONMENT", "testing")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("EXCHANGE_SECRET_KEY", "test_secret_key_32_bytes_12345")
os.environ.setdefault("STRIPE_SECRET_KEY", "sk_test_fake")
os.environ.setdefault("STRIPE_WEBHOOK_SECRET", "whsec_test_fake")
os.environ.setdefault("STRIPE_PLATFORM_ACCOUNT", "acct_test_fake")
os.environ.setdefault("SENDGRID_API_KEY", "SG.test_fake")

from app.main import app
from app.models import Base
from app import database


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    """Initialize test database once per session."""
    await database.init_db()
    yield
    await database.close_db()


@pytest.fixture
async def db_session() -> AsyncSession:
    """Create an in-memory database session for testing."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with SessionLocal() as session:
        yield session
    
    await engine.dispose()


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)
