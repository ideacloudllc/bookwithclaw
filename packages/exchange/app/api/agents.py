"""Agent registration and Ed25519 key management.

According to BUILDSPEC Step 2:
- POST /agents/register accepts { public_key, role, email }
- Returns JWT token with { agent_id, role, public_key, iat, exp: 24h }
- get_current_agent dependency extracts & validates JWT from Authorization header
"""

from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.jwt import create_agent_token, verify_agent_token
from app.core.signing import verify_signature
from app.dependencies import get_db
from app.models.agent import Agent, AgentRole

router = APIRouter(prefix="/agents", tags=["agents"])
security = HTTPBearer()


class AgentRegisterRequest(BaseModel):
    """Register a new agent with Ed25519 public key."""
    public_key: str = Field(..., description="Hex-encoded Ed25519 public key")
    role: str = Field(..., description="'buyer' or 'seller'")
    email: EmailStr = Field(..., description="Agent's email address")


class AgentRegisterResponse(BaseModel):
    """JWT auth token for agent."""
    agent_id: str
    auth_token: str
    expires_in: int = Field(default=86400, description="Seconds until token expires")


async def get_current_agent(
    credentials: HTTPAuthorizationCredentials,
    db: AsyncSession = Depends(get_db)
) -> Agent:
    """
    FastAPI dependency: extract & validate current agent from JWT token.
    
    Usage:
        @router.get("/protected")
        async def protected(agent: Agent = Depends(get_current_agent)):
            return {"agent_id": agent.agent_id}
    
    Raises:
        HTTPException 401 if token is missing, invalid, or expired
        HTTPException 404 if agent not found in database
    """
    try:
        token = credentials.credentials
        payload = verify_agent_token(token)
        agent_id = payload.get("agent_id")
        if not agent_id:
            raise ValueError("Missing agent_id in token")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication: {e}"
        )
    
    # Verify agent exists in database
    result = await db.execute(select(Agent).where(Agent.agent_id == agent_id))
    agent = result.scalars().first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )
    
    return agent


@router.post("/register", response_model=AgentRegisterResponse, status_code=201)
async def register_agent(
    request: AgentRegisterRequest,
    db: AsyncSession = Depends(get_db)
) -> AgentRegisterResponse:
    """
    Register a new agent.
    
    Args:
        public_key: Hex-encoded Ed25519 public key
        role: 'buyer' or 'seller'
        email: Agent's email address
        
    Returns:
        agent_id and JWT auth_token (expires in 24 hours)
        
    Raises:
        HTTPException 400 if public_key already exists
        HTTPException 400 if email already exists
        HTTPException 400 if role is invalid
    """
    # Validate role
    try:
        role_enum = AgentRole[request.role.upper()]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="role must be 'buyer' or 'seller'"
        )
    
    # Check if public key already registered
    existing = await db.execute(
        select(Agent).where(Agent.public_key == request.public_key)
    )
    if existing.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="public_key already registered"
        )
    
    # Check if email already registered
    existing = await db.execute(
        select(Agent).where(Agent.email == request.email)
    )
    if existing.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="email already registered"
        )
    
    # Create new agent
    agent_id = f"agent_{uuid4().hex[:16]}"
    agent = Agent(
        agent_id=agent_id,
        public_key=request.public_key,
        role=role_enum,
        email=request.email,
    )
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    
    # Create JWT token
    token = create_agent_token(agent_id, request.role.lower(), request.public_key)
    
    return AgentRegisterResponse(
        agent_id=agent_id,
        auth_token=token,
        expires_in=86400
    )


@router.get("/me")
async def get_current_agent_info(
    agent: Agent = Depends(get_current_agent)
) -> dict:
    """Get current agent's info."""
    return {
        "agent_id": agent.agent_id,
        "email": agent.email,
        "role": agent.role.value,
        "public_key": agent.public_key,
        "created_at": agent.created_at.isoformat() if agent.created_at else None,
    }
