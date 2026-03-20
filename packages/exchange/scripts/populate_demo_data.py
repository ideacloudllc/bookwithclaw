#!/usr/bin/env python3
"""Populate comprehensive demo data for testing both buyer and seller accounts."""

import asyncio
from datetime import datetime, timedelta
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models.agent import Agent, AgentRole
from app.models.room import Room


async def populate_demo_data():
    """Add comprehensive demo data to existing accounts."""
    engine = create_async_engine(settings.database_url, echo=False)
    
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Get demo buyer
        buyer_result = await session.execute(
            select(Agent).where(Agent.email == "demo-buyer@example.com")
        )
        demo_buyer = buyer_result.scalars().first()
        
        # Get demo seller
        seller_result = await session.execute(
            select(Agent).where(Agent.email == "demo-hotel@example.com")
        )
        demo_seller = seller_result.scalars().first()
        
        if not demo_buyer or not demo_seller:
            print("✗ Demo accounts not found. Run seed_demo_data.py first.")
            await engine.dispose()
            return
        
        print(f"✓ Found demo buyer: {demo_buyer.agent_id}")
        print(f"✓ Found demo seller: {demo_seller.agent_id}\n")
        
        # === ADD MORE ROOMS FOR SELLER ===
        print("Adding demo rooms...")
        
        additional_rooms = [
            {
                "seller_id": demo_seller.agent_id,
                "name": "Standard Double Room",
                "type": "standard",
                "base_price": 25000,  # $250
                "floor_price": 20000,  # $200
                "max_occupancy": 2,
                "description": "Comfortable double room with city views"
            },
            {
                "seller_id": demo_seller.agent_id,
                "name": "Family Suite with Kitchen",
                "type": "suite",
                "base_price": 60000,  # $600
                "floor_price": 48000,  # $480
                "max_occupancy": 4,
                "description": "Spacious family suite with kitchenette"
            },
            {
                "seller_id": demo_seller.agent_id,
                "name": "Premium Room with Balcony",
                "type": "deluxe",
                "base_price": 45000,  # $450
                "floor_price": 36000,  # $360
                "max_occupancy": 2,
                "description": "Premium room with private balcony and mini bar"
            },
        ]
        
        # Check if rooms already exist
        existing_rooms = await session.execute(
            select(Room).where(Room.seller_id == demo_seller.agent_id)
        )
        existing_count = len(existing_rooms.scalars().all())
        
        if existing_count < 6:
            for room_data in additional_rooms:
                room = Room(
                    id=f"room_{uuid4().hex[:8]}",
                    seller_id=room_data["seller_id"],
                    name=room_data["name"],
                    type=room_data["type"],
                    base_price=room_data["base_price"],
                    floor_price=room_data["floor_price"],
                    max_occupancy=room_data["max_occupancy"],
                    description=room_data["description"],
                )
                session.add(room)
                print(f"  ✓ {room_data['name']} (${room_data['base_price']/100:.0f} base)")
            
            await session.commit()
            print(f"✓ Added {len(additional_rooms)} more rooms\n")
        else:
            print(f"✓ Seller already has {existing_count} rooms, skipping\n")
        
        print("✅ Demo data fully populated!\n")
        print("📋 Demo Account Credentials:\n")
        print("BUYER:")
        print("  Email: demo-buyer@example.com")
        print("  Password: demo1234")
        print("  Name: Demo Buyer\n")
        print("SELLER (Hotel):")
        print("  Email: demo-hotel@example.com")
        print("  Password: demo1234")
        print("  Name: Demo Hotel")
        print("  Rooms: Multiple listings ready for negotiation\n")
        print("📍 Test URL: http://159.65.36.5:8890/buyers/\n")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(populate_demo_data())
