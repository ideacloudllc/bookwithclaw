"""Seller Dashboard MVP - Backend API endpoints"""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status, Cookie
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.dependencies import get_db
from app.auth import hash_password, verify_password, create_seller_token, verify_seller_token
from app.models.agent import Agent, AgentRole

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


def get_seller_id_from_token(token: Optional[str] = Cookie(None)) -> str:
    """Extract seller ID from auth token cookie."""
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
        "token": token,
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
        "token": token
    }


@router.get("/profile")
async def get_seller_profile(
    seller_id: str = Depends(get_seller_id_from_token),
    session: AsyncSession = Depends(get_db)
):
    """Get seller profile."""
    result = await session.execute(
        select(Agent).where(Agent.agent_id == seller_id)
    )
    seller = result.scalars().first()
    
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    
    return {
        "agent_id": seller.agent_id,
        "hotel_name": seller.hotel_name,
        "email": seller.email,
        "location": "San Francisco, CA",
        "check_in_time": "3:00 PM",
        "check_out_time": "11:00 AM",
        "phone": "+1-555-0000",
        "description": "Beautiful hotel in downtown"
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
    
    return {"status": "updated", "seller_id": seller.agent_id}


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
    
    return {
        "rooms": [
            {
                "room_id": "rm_1",
                "name": "Deluxe King",
                "description": "Spacious room with city view",
                "capacity": 2,
                "amenities": ["WiFi", "A/C", "Mini Bar", "TV"],
                "base_rate": 350,
                "floor_price": 280,
                "availability": "open",
                "photos": 3,
                "status": "active",
                "views": 24,
                "inquiries": 3,
                "bookings": 2
            },
            {
                "room_id": "rm_2",
                "name": "Standard Queen",
                "description": "Comfortable room with garden view",
                "capacity": 2,
                "amenities": ["WiFi", "A/C", "TV"],
                "base_rate": 280,
                "floor_price": 220,
                "availability": "open",
                "photos": 2,
                "status": "active",
                "views": 18,
                "inquiries": 5,
                "bookings": 3
            },
            {
                "room_id": "rm_3",
                "name": "Suite",
                "description": "Luxury suite with private lounge",
                "capacity": 4,
                "amenities": ["WiFi", "A/C", "Mini Bar", "TV", "Lounge", "Kitchen"],
                "base_rate": 550,
                "floor_price": 450,
                "availability": "open",
                "photos": 5,
                "status": "active",
                "views": 42,
                "inquiries": 2,
                "bookings": 1
            }
        ]
    }


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
    
    return {
        "offers": [
            {
                "offer_id": "off_001",
                "room_id": "rm_1",
                "buyer_name": "John Traveler",
                "room_type": "Deluxe King",
                "checkin": "2026-03-22",
                "checkout": "2026-03-24",
                "nights": 2,
                "offered_price": 320,
                "total": 640,
                "status": "pending",
                "received_at": "2026-03-19T09:30:00Z"
            },
            {
                "offer_id": "off_002",
                "room_id": "rm_2",
                "buyer_name": "Jane Smith",
                "room_type": "Standard Queen",
                "checkin": "2026-03-25",
                "checkout": "2026-03-27",
                "nights": 2,
                "offered_price": 280,
                "total": 560,
                "status": "pending",
                "received_at": "2026-03-19T08:15:00Z"
            }
        ]
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
    
    return {
        "bookings": [
            {
                "booking_id": "bk_001",
                "room_id": "rm_3",
                "guest_name": "Robert Johnson",
                "room_type": "Suite",
                "checkin": "2026-03-20",
                "checkout": "2026-03-22",
                "nights": 2,
                "final_price": 450,
                "total": 900,
                "status": "confirmed",
                "booked_at": "2026-03-18T14:00:00Z"
            },
            {
                "booking_id": "bk_002",
                "room_id": "rm_1",
                "guest_name": "Emma Wilson",
                "room_type": "Deluxe King",
                "checkin": "2026-03-28",
                "checkout": "2026-03-30",
                "nights": 2,
                "final_price": 340,
                "total": 680,
                "status": "confirmed",
                "booked_at": "2026-03-17T10:30:00Z"
            }
        ]
    }
