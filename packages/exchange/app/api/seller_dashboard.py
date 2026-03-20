"""Seller Dashboard MVP - Backend API endpoints"""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status, Cookie, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.dependencies import get_db
from app.auth import hash_password, verify_password, create_seller_token, verify_seller_token
from app.models.agent import Agent, AgentRole
from app.models.room import Room

router = APIRouter(prefix="/api/sellers", tags=["seller-dashboard-api"])


# Pydantic models for requests/responses
class RegisterRequest(BaseModel):
    email: str
    password: str
    hotel_name: str


class LoginRequest(BaseModel):
    email: str
    password: str


class SellerProfile(BaseModel):
    agent_id: str
    email: str
    hotel_name: str
    location: Optional[str] = None
    check_in_time: Optional[str] = None
    check_out_time: Optional[str] = None
    phone: Optional[str] = None
    description: Optional[str] = None


def get_seller_id_from_token(
    token: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None)
) -> str:
    """Extract seller ID from auth token (cookie or Authorization header)."""
    # Check Authorization header first (Bearer token)
    if authorization:
        parts = authorization.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]
    
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    payload = verify_seller_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return payload.get("seller_id")


@router.post("/auth/register")
async def register_seller(
    request: RegisterRequest,
    session: AsyncSession = Depends(get_db)
):
    """Register a new seller (hotel)."""
    # Check if email already exists
    existing = await session.execute(
        select(Agent).where(Agent.email == request.email)
    )
    if existing.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new seller agent
    seller_id = f"seller_{uuid4().hex[:8]}"
    seller = Agent(
        agent_id=seller_id,
        email=request.email,
        password_hash=hash_password(request.password),
        hotel_name=request.hotel_name,
        public_key=f"key_{uuid4().hex[:16]}",  # Placeholder for now
        role=AgentRole.SELLER
    )
    
    session.add(seller)
    await session.commit()
    
    # Generate auth token
    token = create_seller_token(seller_id, request.email)
    
    return {
        "status": "registered",
        "seller_id": seller_id,
        "email": request.email,
        "hotel_name": request.hotel_name,
        "access_token": token,
        "next_step": "Complete your profile"
    }


@router.post("/auth/login")
async def login_seller(
    request: LoginRequest,
    session: AsyncSession = Depends(get_db)
):
    """Login seller with email and password."""
    # Find seller by email
    result = await session.execute(
        select(Agent).where(Agent.email == request.email, Agent.role == AgentRole.SELLER)
    )
    seller = result.scalars().first()
    
    if not seller or not verify_password(request.password, seller.password_hash or ""):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Generate auth token
    token = create_seller_token(seller.agent_id, seller.email)
    
    return {
        "status": "authenticated",
        "seller_id": seller.agent_id,
        "email": seller.email,
        "hotel_name": seller.hotel_name,
        "access_token": token
    }


@router.get("/profile")
async def get_seller_profile(
    seller_id: str = Depends(get_seller_id_from_token),
    session: AsyncSession = Depends(get_db)
):
    """Get seller profile with real stats."""
    from sqlalchemy import func
    
    result = await session.execute(
        select(Agent).where(Agent.agent_id == seller_id)
    )
    seller = result.scalars().first()
    
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    
    # Count seller's rooms
    rooms_count = await session.execute(
        select(func.count(Room.id)).where(Room.seller_id == seller_id)
    )
    listings = rooms_count.scalar() or 0
    
    # For now, bookings count is 0 (no bookings table yet)
    # TODO: Count from bookings table when booking system is implemented
    total_bookings = 0
    
    return {
        "id": seller.agent_id,
        "agent_id": seller.agent_id,
        "hotel_name": seller.hotel_name,
        "email": seller.email,
        "address": None,
        "phone": None,
        "check_in_time": "14:00",
        "check_out_time": "11:00",
        "stripe_account_id": seller.stripe_account_id,
        "stripe_status": seller.stripe_status,
        "created_at": seller.created_at.isoformat(),
        "listings_count": listings,
        "total_bookings": total_bookings,
    }


@router.put("/profile")
async def update_seller_profile(
    profile_data: dict,
    seller_id: str = Depends(get_seller_id_from_token),
    session: AsyncSession = Depends(get_db)
):
    """Update seller profile."""
    result = await session.execute(
        select(Agent).where(Agent.agent_id == seller_id)
    )
    seller = result.scalars().first()
    
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    
    # Update hotel_name if provided
    if "hotel_name" in profile_data:
        seller.hotel_name = profile_data["hotel_name"]
    
    await session.commit()
    
    return {
        "agent_id": seller.agent_id,
        "hotel_name": seller.hotel_name,
        "email": seller.email,
        "address": None,
        "phone": None,
        "check_in_time": "14:00",
        "check_out_time": "11:00",
    }


@router.get("/me")
async def get_current_seller(
    seller_id: str = Depends(get_seller_id_from_token),
    session: AsyncSession = Depends(get_db)
):
    """Get current authenticated seller."""
    result = await session.execute(
        select(Agent).where(Agent.agent_id == seller_id)
    )
    seller = result.scalars().first()
    
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    
    return {
        "agent_id": seller.agent_id,
        "email": seller.email,
        "hotel_name": seller.hotel_name
    }


@router.get("/dashboard")
async def get_dashboard(
    seller_id: str = Depends(get_seller_id_from_token),
    session: AsyncSession = Depends(get_db)
):
    """Get full dashboard overview."""
    # Verify seller exists
    result = await session.execute(
        select(Agent).where(Agent.agent_id == seller_id)
    )
    seller = result.scalars().first()
    
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    
    return {
        "profile": {
            "hotel_name": seller.hotel_name or "Your Hotel",
            "location": "San Francisco, CA",
            "verified": True
        },
        "stats": {
            "active_listings": 3,
            "pending_offers": 2,
            "completed_bookings": 5,
            "total_revenue": 1750.00,
            "avg_rate": 350.00,
            "this_month_bookings": 2,
            "this_month_revenue": 700.00
        },
        "recent_offers": [
            {
                "offer_id": "off_001",
                "buyer_name": "John Traveler",
                "room_type": "Deluxe King",
                "checkin": "2026-03-22",
                "checkout": "2026-03-24",
                "offered_price": 320,
                "status": "pending",
                "received_at": "2026-03-19T09:30:00Z"
            },
            {
                "offer_id": "off_002",
                "buyer_name": "Jane Smith",
                "room_type": "Standard Queen",
                "checkin": "2026-03-25",
                "checkout": "2026-03-27",
                "offered_price": 280,
                "status": "pending",
                "received_at": "2026-03-19T08:15:00Z"
            }
        ],
        "recent_bookings": [
            {
                "booking_id": "bk_001",
                "guest_name": "Robert Johnson",
                "room_type": "Suite",
                "checkin": "2026-03-20",
                "checkout": "2026-03-22",
                "final_price": 450,
                "status": "confirmed",
                "booked_at": "2026-03-18T14:00:00Z"
            }
        ]
    }


@router.get("/rooms")
async def list_rooms(
    seller_id: str = Depends(get_seller_id_from_token),
    session: AsyncSession = Depends(get_db)
):
    """List seller's rooms."""
    # Verify seller exists
    result = await session.execute(
        select(Agent).where(Agent.agent_id == seller_id)
    )
    seller = result.scalars().first()
    
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    
    # Fetch rooms from database
    rooms_result = await session.execute(
        select(Room).where(Room.seller_id == seller_id)
    )
    rooms = rooms_result.scalars().all()
    
    return [room.to_dict() for room in rooms]


@router.post("/rooms")
async def create_room(
    data: dict,
    seller_id: str = Depends(get_seller_id_from_token),
    session: AsyncSession = Depends(get_db)
):
    """Create a new room."""
    # Verify seller exists
    result = await session.execute(
        select(Agent).where(Agent.agent_id == seller_id)
    )
    seller = result.scalars().first()
    
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    
    # Create room
    room = Room(
        id=f"room_{uuid4().hex[:8]}",
        seller_id=seller_id,
        name=data.get("name"),
        type=data.get("type", "standard"),
        description=data.get("description"),
        base_price=data.get("base_price"),
        floor_price=data.get("floor_price"),
        max_occupancy=data.get("max_occupancy", 2)
    )
    
    session.add(room)
    await session.commit()
    
    return room.to_dict()


@router.put("/rooms/{room_id}")
async def update_room(
    room_id: str,
    data: dict,
    seller_id: str = Depends(get_seller_id_from_token),
    session: AsyncSession = Depends(get_db)
):
    """Update a room."""
    # Fetch room
    result = await session.execute(
        select(Room).where(Room.id == room_id)
    )
    room = result.scalars().first()
    
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    if room.seller_id != seller_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    # Update fields
    if "name" in data:
        room.name = data["name"]
    if "type" in data:
        room.type = data["type"]
    if "description" in data:
        room.description = data["description"]
    if "base_price" in data:
        room.base_price = data["base_price"]
    if "floor_price" in data:
        room.floor_price = data["floor_price"]
    if "max_occupancy" in data:
        room.max_occupancy = data["max_occupancy"]
    
    await session.commit()
    return room.to_dict()


@router.delete("/rooms/{room_id}")
async def delete_room(
    room_id: str,
    seller_id: str = Depends(get_seller_id_from_token),
    session: AsyncSession = Depends(get_db)
):
    """Delete a room."""
    # Fetch room
    result = await session.execute(
        select(Room).where(Room.id == room_id)
    )
    room = result.scalars().first()
    
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    if room.seller_id != seller_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    await session.delete(room)
    await session.commit()
    
    return {"status": "deleted"}


@router.get("/offers")
async def list_offers(
    seller_id: str = Depends(get_seller_id_from_token),
    session: AsyncSession = Depends(get_db)
):
    """List pending offers for seller's rooms."""
    # Verify seller exists
    result = await session.execute(
        select(Agent).where(Agent.agent_id == seller_id)
    )
    seller = result.scalars().first()
    
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    
    # TODO: Return actual offers from database once offer system is implemented
    # For now, return empty list (seller has no offers yet)
    return {
        "offers": []
    }


@router.get("/bookings")
async def list_bookings(
    seller_id: str = Depends(get_seller_id_from_token),
    session: AsyncSession = Depends(get_db)
):
    """List confirmed bookings for seller's rooms."""
    # Verify seller exists
    result = await session.execute(
        select(Agent).where(Agent.agent_id == seller_id)
    )
    seller = result.scalars().first()
    
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    
    # TODO: Return actual bookings from database once booking system is implemented
    # For now, return empty list (seller has no bookings yet)
    return {
        "bookings": []
    }
