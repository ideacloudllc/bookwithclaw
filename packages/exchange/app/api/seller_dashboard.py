"""
Seller Dashboard API endpoints.
Provides seller-specific views for rooms, offers, and transactions.
"""

from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_agent, get_db

router = APIRouter(prefix="/sellers", tags=["seller-dashboard"])


@router.get("/profile", response_class=dict)
async def get_seller_profile(agent_id: str = Depends(get_current_agent), session: AsyncSession = Depends(get_db)):
    """
    Get seller profile (hotel info)
    """
    return {
        "agent_id": agent_id,
        "name": "Hotel Name",  # Would query database in production
        "email": "hotel@example.com",
        "location": "San Francisco, CA",
        "check_in_time": "3:00 PM",
        "check_out_time": "11:00 AM",
        "rooms_count": 0,
        "active_listings": 0,
        "pending_offers": 0,
        "completed_bookings": 0,
    }


@router.get("/dashboard", response_class=dict)
async def get_dashboard(agent_id: str = Depends(get_current_agent), session: AsyncSession = Depends(get_db)):
    """
    Get full dashboard overview for seller
    """
    return {
        "profile": {
            "agent_id": agent_id,
            "name": "My Hotel",
            "location": "San Francisco, CA",
            "rooms": 3,
        },
        "stats": {
            "active_listings": 2,
            "pending_offers": 1,
            "completed_bookings": 0,
            "total_revenue": 0,
            "avg_rate": 350.00,
        },
        "recent_offers": [],
        "recent_bookings": [],
    }


@router.get("/rooms", response_class=list)
async def list_rooms(agent_id: str = Depends(get_current_agent), session: AsyncSession = Depends(get_db)):
    """
    List seller's rooms
    """
    return [
        {
            "room_id": "rm_1",
            "name": "Deluxe King",
            "capacity": 2,
            "base_rate": 350,
            "floor_price": 250,
            "availability": "open",
            "photos_count": 3,
            "status": "active",
            "views": 15,
            "inquiries": 2,
        },
    ]


@router.post("/rooms", response_class=dict)
async def create_room(
    room_data: dict,
    agent_id: str = Depends(get_current_agent),
    session: AsyncSession = Depends(get_db),
):
    """
    Create new room listing
    """
    return {
        "room_id": f"rm_{uuid4().hex[:8]}",
        "name": room_data.get("name"),
        "capacity": room_data.get("capacity"),
        "base_rate": room_data.get("base_rate"),
        "floor_price": room_data.get("floor_price"),
        "status": "active",
        "created_at": datetime.utcnow().isoformat(),
    }


@router.put("/rooms/{room_id}", response_class=dict)
async def update_room(
    room_id: str,
    room_data: dict,
    agent_id: str = Depends(get_current_agent),
    session: AsyncSession = Depends(get_db),
):
    """
    Update room rates/details
    """
    return {
        "room_id": room_id,
        "base_rate": room_data.get("base_rate"),
        "floor_price": room_data.get("floor_price"),
        "updated_at": datetime.utcnow().isoformat(),
    }


@router.get("/offers", response_class=list)
async def list_offers(agent_id: str = Depends(get_current_agent), session: AsyncSession = Depends(get_db)):
    """
    List active and pending offers for seller's rooms
    """
    return [
        {
            "offer_id": "of_1",
            "room_id": "rm_1",
            "room_name": "Deluxe King",
            "buyer_id": "by_1",
            "dates": {
                "checkin": "2026-03-25",
                "checkout": "2026-03-27",
            },
            "proposed_price": 320,
            "your_floor": 250,
            "your_base": 350,
            "status": "negotiating",
            "round": 1,
            "created_at": "2026-03-19T10:00:00Z",
            "expires_at": "2026-03-19T10:30:00Z",
        },
    ]


@router.post("/offers/{offer_id}/accept", response_class=dict)
async def accept_offer(
    offer_id: str,
    agent_id: str = Depends(get_current_agent),
    session: AsyncSession = Depends(get_db),
):
    """
    Accept an offer
    """
    return {
        "offer_id": offer_id,
        "status": "accepted",
        "settlement_initiated": True,
        "estimated_payout": 312.40,
        "payout_date": "2026-03-21",
    }


@router.post("/offers/{offer_id}/reject", response_class=dict)
async def reject_offer(
    offer_id: str,
    agent_id: str = Depends(get_current_agent),
    session: AsyncSession = Depends(get_db),
):
    """
    Reject an offer
    """
    return {
        "offer_id": offer_id,
        "status": "rejected",
        "message": "Offer rejected",
    }


@router.get("/bookings", response_class=list)
async def list_bookings(agent_id: str = Depends(get_current_agent), session: AsyncSession = Depends(get_db)):
    """
    List completed bookings for seller
    """
    return []


@router.get("/payouts", response_class=list)
async def list_payouts(agent_id: str = Depends(get_current_agent), session: AsyncSession = Depends(get_db)):
    """
    List payout history
    """
    return []
