"""Agent registration and management endpoints."""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.signing import create_jwt_token
from app.main import SessionLocal
from app.models.agent import Agent, AgentRole

router = APIRouter(prefix="/agents", tags=["agents"])


class AgentRegisterRequest(BaseModel):
    """Request to register a new agent."""

    public_key: str = Field(..., description="Hex-encoded Ed25519 public key")
    role: str = Field(..., description="'buyer' or 'seller'")
    email: EmailStr = Field(..., description="Agent's email address")


class AgentRegisterResponse(BaseModel):
    """Response after agent registration."""

    agent_id: str
    auth_token: str
    expires_in: int = 86400  # 24 hours


@router.post("/register", response_model=AgentRegisterResponse)
async def register_agent(
    request: AgentRegisterRequest,
    db: AsyncSession = Depends(lambda: SessionLocal()),
) -> AgentRegisterResponse:
    """
    Register a new agent and receive JWT auth token.
    
    Args:
        request: AgentRegisterRequest with public_key, role, email
        db: Database session
        
    Returns:
        Agent ID and JWT token
        
    Raises:
        HTTPException 400 if public key or email already registered
        HTTPException 400 if role is invalid
    """
    # Validate role
    try:
        role = AgentRole(request.role)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role. Must be 'buyer' or 'seller'.",
        )
    
    # Validate public key format (should be 64-char hex string = 32 bytes)
    if len(request.public_key) != 64 or not all(c in "0123456789abcdefABCDEF" for c in request.public_key):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid public_key. Must be 64-character hex string (Ed25519).",
        )
    
    # Check if public key already registered
    existing = await db.execute(
        select(Agent).where(Agent.public_key == request.public_key)
    )
    if existing.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Public key already registered.",
        )
    
    # Check if email already registered
    existing = await db.execute(
        select(Agent).where(Agent.email == request.email)
    )
    if existing.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered.",
        )
    
    # Create new agent
    agent_id = str(uuid.uuid4())
    agent = Agent(
        agent_id=agent_id,
        public_key=request.public_key,
        role=role,
        email=request.email,
    )
    
    db.add(agent)
    await db.commit()
    
    # Generate JWT token
    token = create_jwt_token(agent_id, request.public_key, request.role)
    
    return AgentRegisterResponse(
        agent_id=agent_id,
        auth_token=token,
        expires_in=86400,
    )
