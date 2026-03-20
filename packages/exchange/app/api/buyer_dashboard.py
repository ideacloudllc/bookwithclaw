"""Buyer Dashboard API endpoints"""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.dependencies import get_db
from app.auth import hash_password, verify_password, create_seller_token, verify_seller_token
from app.models.agent import Agent, AgentRole

router = APIRouter(prefix="/api/buyers", tags=["buyer-dashboard-api"])


# Pydantic models
class BuyerRegisterRequest(BaseModel):
    email: str
    password: str
    name: str


class BuyerLoginRequest(BaseModel):
    email: str
    password: str


def get_buyer_id_from_token(token: Optional[str] = None) -> str:
    """Extract buyer ID from auth token (from cookie or header)."""
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    payload = verify_seller_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return payload.get("seller_id")


@router.post("/auth/register")
async def register_buyer(
    request: BuyerRegisterRequest,
    session: AsyncSession = Depends(get_db)
):
    """Register a new buyer."""
    try:
        # Check if email already exists
        existing = await session.execute(
            select(Agent).where(Agent.email == request.email)
        )
        if existing.scalars().first():
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Validate input
        if not request.email or not request.password or not request.name:
            raise HTTPException(status_code=400, detail="Email, password, and name are required")
        
        if len(request.password) < 6:
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
        
        # Create new buyer agent
        buyer_id = f"buyer_{uuid4().hex[:8]}"
        buyer = Agent(
            agent_id=buyer_id,
            email=request.email,
            password_hash=hash_password(request.password),
            hotel_name=request.name,  # Reuse field for buyer name
            public_key=f"key_{uuid4().hex[:16]}",
            role=AgentRole.BUYER
        )
        
        session.add(buyer)
        await session.commit()
        
        token = create_seller_token(buyer_id, request.email)
        
        return {
            "status": "registered",
            "buyer_id": buyer_id,
            "email": request.email,
            "access_token": token,
            "token": token
        }
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        # Return a user-friendly error message
        error_msg = str(e)
        if "duplicate" in error_msg.lower() or "unique" in error_msg.lower():
            raise HTTPException(status_code=400, detail="Email is already in use")
        elif "constraint" in error_msg.lower():
            raise HTTPException(status_code=400, detail="Invalid input - please check your data")
        else:
            raise HTTPException(status_code=500, detail="Registration failed. Please try again.")


@router.post("/auth/login")
async def login_buyer(
    request: BuyerLoginRequest,
    session: AsyncSession = Depends(get_db)
):
    """Login buyer."""
    result = await session.execute(
        select(Agent).where(Agent.email == request.email, Agent.role == AgentRole.BUYER)
    )
    buyer = result.scalars().first()
    
    if not buyer or not verify_password(request.password, buyer.password_hash or ""):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token = create_seller_token(buyer.agent_id, buyer.email)
    
    return {
        "status": "authenticated",
        "buyer_id": buyer.agent_id,
        "email": buyer.email,
        "token": token
    }


@router.get("/search")
async def search_rooms(
    checkin: str = "2026-03-25",
    checkout: str = "2026-03-27",
    location: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    session: AsyncSession = Depends(get_db)
):
    """Search available rooms by date and filters."""
    # Mock room search results
    return {
        "results": [
            {
                "room_id": "rm_1",
                "hotel_name": "The Harriot",
                "location": "San Francisco, CA",
                "room_type": "Deluxe King",
                "capacity": 2,
                "base_price": 350,
                "floor_price": 280,
                "amenities": ["WiFi", "A/C", "Mini Bar"],
                "rating": 4.8,
                "reviews": 127,
                "photos": ["url1", "url2", "url3"],
                "availability": "available"
            },
            {
                "room_id": "rm_2",
                "hotel_name": "Phoenix Hotel",
                "location": "San Francisco, CA",
                "room_type": "Standard Queen",
                "capacity": 2,
                "base_price": 280,
                "floor_price": 220,
                "amenities": ["WiFi", "A/C", "TV"],
                "rating": 4.5,
                "reviews": 89,
                "photos": ["url1", "url2"],
                "availability": "available"
            },
            {
                "room_id": "rm_3",
                "hotel_name": "Auberge Hotel",
                "location": "San Francisco, CA",
                "room_type": "Luxury Suite",
                "capacity": 4,
                "base_price": 550,
                "floor_price": 450,
                "amenities": ["WiFi", "A/C", "Mini Bar", "Lounge", "Kitchen"],
                "rating": 4.9,
                "reviews": 256,
                "photos": ["url1", "url2", "url3", "url4", "url5"],
                "availability": "available"
            }
        ],
        "total": 3,
        "checkin": checkin,
        "checkout": checkout
    }


@router.get("/rooms/{room_id}")
async def get_room_details(
    room_id: str,
    session: AsyncSession = Depends(get_db)
):
    """Get details for a specific room."""
    return {
        "room_id": room_id,
        "hotel_name": "The Harriot",
        "location": "San Francisco, CA",
        "room_type": "Deluxe King",
        "description": "Spacious room with panoramic city views, king bed, luxury amenities",
        "capacity": 2,
        "base_price": 350,
        "floor_price": 280,
        "check_in_time": "3:00 PM",
        "check_out_time": "11:00 AM",
        "amenities": ["WiFi", "A/C", "Mini Bar", "TV", "Desk", "Coffee Maker"],
        "rating": 4.8,
        "reviews": 127,
        "photos": [
            {"url": "photo1.jpg", "caption": "Main room view"},
            {"url": "photo2.jpg", "caption": "Bathroom"},
            {"url": "photo3.jpg", "caption": "City view from balcony"}
        ],
        "hotel_info": {
            "name": "The Harriot",
            "rating": 4.8,
            "reviews": 450,
            "phone": "+1-415-555-0101",
            "website": "theharriot.com",
            "address": "123 Main St, San Francisco, CA 94103"
        }
    }


@router.post("/make-offer")
async def make_offer(
    room_id: str,
    checkin: str,
    checkout: str,
    offered_price: int,
    buyer_id: Optional[str] = None,
    session: AsyncSession = Depends(get_db)
):
    """Create a buyer intent (make an offer on a room)."""
    offer_id = f"offer_{uuid4().hex[:8]}"
    
    return {
        "status": "offer_created",
        "offer_id": offer_id,
        "room_id": room_id,
        "offered_price": offered_price,
        "checkin": checkin,
        "checkout": checkout,
        "created_at": datetime.utcnow().isoformat(),
        "next_step": "Waiting for seller response..."
    }


@router.get("/my-offers")
async def get_buyer_offers(
    token: Optional[str] = None,
    session: AsyncSession = Depends(get_db)
):
    """Get all offers/negotiations for the buyer."""
    buyer_id = get_buyer_id_from_token(token)
    
    return {
        "offers": [
            {
                "offer_id": "offer_1",
                "hotel_name": "The Harriot",
                "room_type": "Deluxe King",
                "checkin": "2026-03-25",
                "checkout": "2026-03-27",
                "nights": 2,
                "offered_price": 300,
                "seller_counter": 320,
                "your_counter": None,
                "status": "awaiting_your_response",
                "messages": [
                    {"from": "seller", "text": "We can do $320/night", "at": "2026-03-19T10:30:00Z"},
                    {"from": "you", "text": "Is $300 possible?", "at": "2026-03-19T10:00:00Z"}
                ]
            },
            {
                "offer_id": "offer_2",
                "hotel_name": "Phoenix Hotel",
                "room_type": "Standard Queen",
                "checkin": "2026-03-28",
                "checkout": "2026-03-30",
                "nights": 2,
                "offered_price": 250,
                "seller_counter": 280,
                "your_counter": 265,
                "status": "awaiting_seller_response",
                "messages": [
                    {"from": "you", "text": "How about $265?", "at": "2026-03-19T09:15:00Z"},
                    {"from": "seller", "text": "Minimum is $280", "at": "2026-03-19T08:45:00Z"}
                ]
            }
        ]
    }


@router.post("/offers/{offer_id}/counter")
async def counter_offer(
    offer_id: str,
    counter_price: int,
    token: Optional[str] = None,
    session: AsyncSession = Depends(get_db)
):
    """Send a counter offer."""
    buyer_id = get_buyer_id_from_token(token)
    
    return {
        "status": "counter_sent",
        "offer_id": offer_id,
        "counter_price": counter_price,
        "status_now": "awaiting_seller_response",
        "message": f"Counter offer of ${counter_price}/night sent to seller"
    }


@router.post("/offers/{offer_id}/accept")
async def accept_offer(
    offer_id: str,
    token: Optional[str] = None,
    session: AsyncSession = Depends(get_db)
):
    """Accept seller's offer - complete negotiation."""
    buyer_id = get_buyer_id_from_token(token)
    
    return {
        "status": "offer_accepted",
        "offer_id": offer_id,
        "message": "Offer accepted! Proceeding to payment...",
        "next_step": "payment"
    }


@router.get("/my-bookings")
async def get_buyer_bookings(
    token: Optional[str] = None,
    session: AsyncSession = Depends(get_db)
):
    """Get buyer's confirmed bookings."""
    buyer_id = get_buyer_id_from_token(token)
    
    return {
        "bookings": [
            {
                "booking_id": "bk_001",
                "hotel_name": "The Harriot",
                "room_type": "Deluxe King",
                "location": "San Francisco, CA",
                "checkin": "2026-04-01",
                "checkout": "2026-04-03",
                "nights": 2,
                "total_price": 700,
                "status": "confirmed",
                "confirmation_email": "Sent to your email",
                "check_in_instructions": "Check in at 3:00 PM at front desk"
            }
        ]
    }
