"""FastAPI dependency injection utilities."""

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app import database
from app.api.agents import verify_agent_token

security = HTTPBearer()


async def get_db() -> AsyncSession:
    """
    Get database session.
    
    Usage:
        @router.get("/endpoint")
        async def endpoint(db: AsyncSession = Depends(get_db)):
            ...
    """
    if not database.SessionLocal:
        raise RuntimeError("Database not initialized")
    
    async with database.SessionLocal() as session:
        yield session


async def get_current_agent_payload(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> dict:
    """
    Extract and verify JWT token from Authorization header.
    
    Returns:
        Decoded JWT payload: {agent_id, role, public_key, iat, exp}
        
    Raises:
        HTTPException 401 if token is missing or invalid
        
    Usage:
        @router.get("/protected")
        async def protected(payload = Depends(get_current_agent_payload)):
            return {"agent_id": payload["agent_id"]}
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization credentials",
        )
    
    try:
        token = credentials.credentials
        payload = verify_agent_token(token)
        return payload
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {e}",
        )
