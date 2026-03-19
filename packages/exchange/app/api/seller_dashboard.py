"""
Seller Dashboard MVP - Backend API endpoints
"""

from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_agent, get_db

router = APIRouter(prefix="/sellers", tags=["seller-dashboard"])


@router.post("/auth/register")
async def register_seller(
    email: str, 
    hotel_name: str,
    session: AsyncSession = Depends(get_db)
):
    """Register a new seller (hotel) - simplified for MVP"""
    # In real app: send email verification, etc.
    # For MVP: just create agent record
    agent_id = f"seller_{uuid4().hex[:8]}"
    
    return {
        "agent_id": agent_id,
        "email": email,
        "hotel_name": hotel_name,
        "status": "registered",
        "next_step": "Set up your profile in the dashboard"
    }


@router.get("/profile")
async def get_seller_profile(
    agent_id: str = Depends(get_current_agent),
    session: AsyncSession = Depends(get_db)
):
    """Get seller profile"""
    # In MVP: return mock data
    # In production: query actual agent record
    return {
        "agent_id": agent_id,
        "hotel_name": "Your Hotel Name",
        "email": "hotel@example.com",
        "location": "San Francisco, CA",
        "check_in_time": "3:00 PM",
        "check_out_time": "11:00 AM",
        "phone": "+1-555-0000",
        "description": "Beautiful 3-star hotel in downtown"
    }


@router.put("/profile")
async def update_seller_profile(
    profile_data: dict,
    agent_id: str = Depends(get_current_agent),
    session: AsyncSession = Depends(get_db)
):
    """Update seller profile"""
    return {
        "status": "updated",
        "profile": profile_data
    }


@router.get("/dashboard")
async def get_dashboard(
    agent_id: str = Depends(get_current_agent),
    session: AsyncSession = Depends(get_db)
):
    """Get full dashboard overview"""
    return {
        "profile": {
            "hotel_name": "My Hotel",
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
    agent_id: str = Depends(get_current_agent),
    session: AsyncSession = Depends(get_db)
):
    """List seller's rooms"""
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
                "description": "Cozy room, perfect for couples",
                "capacity": 2,
                "amenities": ["WiFi", "A/C", "Desk"],
                "base_rate": 250,
                "floor_price": 200,
                "availability": "open",
                "photos": 2,
                "status": "active",
                "views": 12,
                "inquiries": 1,
                "bookings": 1
            },
            {
                "room_id": "rm_3",
                "name": "Suite",
                "description": "Luxury suite with living area",
                "capacity": 4,
                "amenities": ["WiFi", "A/C", "Jacuzzi", "Living Room"],
                "base_rate": 500,
                "floor_price": 400,
                "availability": "booked",
                "photos": 5,
                "status": "active",
                "views": 45,
                "inquiries": 5,
                "bookings": 3
            }
        ]
    }


@router.post("/rooms")
async def create_room(
    room_data: dict,
    agent_id: str = Depends(get_current_agent),
    session: AsyncSession = Depends(get_db)
):
    """Create new room listing"""
    room_id = f"rm_{uuid4().hex[:6]}"
    return {
        "room_id": room_id,
        "name": room_data.get("name"),
        "capacity": room_data.get("capacity"),
        "base_rate": room_data.get("base_rate"),
        "floor_price": room_data.get("floor_price"),
        "status": "active",
        "created_at": datetime.utcnow().isoformat(),
        "message": "Room created! Add photos to improve booking chances."
    }


@router.put("/rooms/{room_id}")
async def update_room(
    room_id: str,
    room_data: dict,
    agent_id: str = Depends(get_current_agent),
    session: AsyncSession = Depends(get_db)
):
    """Update room listing"""
    return {
        "room_id": room_id,
        "status": "updated",
        "updated_at": datetime.utcnow().isoformat(),
        "data": room_data
    }


@router.get("/offers")
async def list_offers(
    agent_id: str = Depends(get_current_agent),
    session: AsyncSession = Depends(get_db),
    status: Optional[str] = None
):
    """List incoming offers/intents"""
    return {
        "offers": [
            {
                "offer_id": "off_001",
                "room_id": "rm_1",
                "room_type": "Deluxe King",
                "buyer_name": "John Traveler",
                "buyer_rating": 4.8,
                "checkin": "2026-03-22",
                "checkout": "2026-03-24",
                "nights": 2,
                "offered_price": 320,
                "your_rate": 350,
                "discount": "8.6%",
                "status": "pending",
                "received_at": "2026-03-19T09:30:00Z",
                "expires_in_hours": 24
            },
            {
                "offer_id": "off_002",
                "room_id": "rm_2",
                "room_type": "Standard Queen",
                "buyer_name": "Jane Smith",
                "buyer_rating": 5.0,
                "checkin": "2026-03-25",
                "checkout": "2026-03-27",
                "nights": 2,
                "offered_price": 280,
                "your_rate": 250,
                "discount": "premium",
                "status": "pending",
                "received_at": "2026-03-19T08:15:00Z",
                "expires_in_hours": 18
            }
        ]
    }


@router.post("/offers/{offer_id}/accept")
async def accept_offer(
    offer_id: str,
    agent_id: str = Depends(get_current_agent),
    session: AsyncSession = Depends(get_db)
):
    """Accept an offer"""
    return {
        "status": "accepted",
        "offer_id": offer_id,
        "booking_confirmed": True,
        "message": "Offer accepted! Your guest will receive confirmation.",
        "next_steps": [
            "Prepare room for check-in",
            "Send welcome info to guest",
            "Settlement happens automatically"
        ]
    }


@router.post("/offers/{offer_id}/counter")
async def counter_offer(
    offer_id: str,
    counter_data: dict,
    agent_id: str = Depends(get_current_agent),
    session: AsyncSession = Depends(get_db)
):
    """Send counter-offer to buyer"""
    return {
        "status": "countered",
        "offer_id": offer_id,
        "your_counter_price": counter_data.get("price"),
        "message": "Counter-offer sent! Waiting for buyer response.",
        "expires_in": "24 hours"
    }


@router.post("/offers/{offer_id}/decline")
async def decline_offer(
    offer_id: str,
    agent_id: str = Depends(get_current_agent),
    session: AsyncSession = Depends(get_db)
):
    """Decline an offer"""
    return {
        "status": "declined",
        "offer_id": offer_id,
        "message": "Offer declined."
    }


@router.get("/bookings")
async def list_bookings(
    agent_id: str = Depends(get_current_agent),
    session: AsyncSession = Depends(get_db),
    status: Optional[str] = None
):
    """List all bookings"""
    return {
        "bookings": [
            {
                "booking_id": "bk_001",
                "guest_name": "Robert Johnson",
                "room_type": "Suite",
                "checkin": "2026-03-20",
                "checkout": "2026-03-22",
                "nights": 2,
                "final_price": 450,
                "platform_fee": 8.10,
                "your_earnings": 441.90,
                "status": "confirmed",
                "booked_at": "2026-03-18T14:00:00Z",
                "guest_rating": None
            },
            {
                "booking_id": "bk_002",
                "guest_name": "Alice Wonder",
                "room_type": "Deluxe King",
                "checkin": "2026-03-15",
                "checkout": "2026-03-17",
                "nights": 2,
                "final_price": 400,
                "platform_fee": 7.20,
                "your_earnings": 392.80,
                "status": "completed",
                "booked_at": "2026-03-12T10:00:00Z",
                "guest_rating": 5.0
            }
        ]
    }


@router.get("/pricing-rules")
async def get_pricing_rules(
    agent_id: str = Depends(get_current_agent),
    session: AsyncSession = Depends(get_db)
):
    """Get current pricing rules and recommendations"""
    return {
        "rules": [
            {
                "room_id": "rm_1",
                "name": "Deluxe King",
                "base_rate": 350,
                "floor_price": 280,
                "ceiling_price": 500,
                "occupancy": 75,
                "recommendation": "You're priced competitively. Consider: 1) Weekends: +$30, 2) Last-minute: -$20"
            }
        ]
    }


@router.post("/pricing-rules/{room_id}")
async def update_pricing_rules(
    room_id: str,
    rules_data: dict,
    agent_id: str = Depends(get_current_agent),
    session: AsyncSession = Depends(get_db)
):
    """Update pricing for a room"""
    return {
        "room_id": room_id,
        "status": "updated",
        "base_rate": rules_data.get("base_rate"),
        "floor_price": rules_data.get("floor_price"),
        "message": "Pricing updated! New offers will use these rates."
    }
