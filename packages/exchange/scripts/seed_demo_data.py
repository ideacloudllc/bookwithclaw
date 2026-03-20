#!/usr/bin/env python3
"""Seed demo data for BookWithClaw testing."""

import asyncio
from datetime import datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models.agent import Agent, AgentRole
from app.models.room import Room
from app.auth import hash_password


async def seed_demo_data():
    """Create demo buyers and sellers with sample rooms."""
    engine = create_async_engine(settings.database_url, echo=False)
    
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Check if demo data already exists
        existing = await session.execute(
            select(Agent).where(Agent.email == "demo-buyer@example.com")
        )
        
        if existing.scalars().first():
            print("✓ Demo data already exists, skipping...")
            await engine.dispose()
            return
        
        # === CREATE DEMO BUYERS ===
        demo_buyers = [
            {
                "agent_id": f"buyer_demo_001",
                "email": "demo-buyer@example.com",
                "password": "demo1234",
                "name": "Demo Buyer",
                "phone": "+1-415-555-0001",
            },
            {
                "agent_id": f"buyer_demo_002",
                "email": "jane@example.com",
                "password": "demo1234",
                "name": "Jane Traveler",
                "phone": "+1-415-555-0002",
            },
        ]
        
        print("Creating demo buyers...")
        for buyer_data in demo_buyers:
            buyer = Agent(
                agent_id=buyer_data["agent_id"],
                email=buyer_data["email"],
                password_hash=hash_password(buyer_data["password"]),
                hotel_name=buyer_data["name"],
                public_key=f"key_{uuid4().hex[:16]}",
                role=AgentRole.BUYER,
            )
            session.add(buyer)
            print(f"  ✓ {buyer_data['name']} ({buyer_data['email']})")
        
        # === CREATE DEMO SELLERS ===
        demo_sellers = [
            {
                "agent_id": f"seller_demo_001",
                "email": "demo-hotel@example.com",
                "password": "demo1234",
                "name": "Demo Hotel",
                "phone": "+1-415-555-1001",
                "stripe_account_id": "acct_demo_001",
            },
            {
                "agent_id": f"seller_demo_002",
                "email": "luxury-hotel@example.com",
                "password": "demo1234",
                "name": "Luxury Hotel Group",
                "phone": "+1-415-555-1002",
                "stripe_account_id": "acct_demo_002",
            },
        ]
        
        print("\nCreating demo sellers...")
        for seller_data in demo_sellers:
            seller = Agent(
                agent_id=seller_data["agent_id"],
                email=seller_data["email"],
                password_hash=hash_password(seller_data["password"]),
                hotel_name=seller_data["name"],
                public_key=f"key_{uuid4().hex[:16]}",
                role=AgentRole.SELLER,
                stripe_account_id=seller_data["stripe_account_id"],
                stripe_status="connected",
            )
            session.add(seller)
            print(f"  ✓ {seller_data['name']} ({seller_data['email']})")
        
        await session.commit()
        
        # === CREATE DEMO ROOMS ===
        print("\nCreating demo rooms...")
        
        rooms = [
            {
                "seller_id": "seller_demo_001",
                "name": "Deluxe King Room",
                "type": "deluxe",
                "base_price": 35000,  # $350
                "floor_price": 28000,  # $280
                "max_occupancy": 2,
            },
            {
                "seller_id": "seller_demo_001",
                "name": "Suite with View",
                "type": "suite",
                "base_price": 50000,  # $500
                "floor_price": 40000,  # $400
                "max_occupancy": 4,
            },
            {
                "seller_id": "seller_demo_002",
                "name": "Luxury Ocean View",
                "type": "luxury",
                "base_price": 75000,  # $750
                "floor_price": 60000,  # $600
                "max_occupancy": 2,
            },
        ]
        
        for room_data in rooms:
            room = Room(
                id=f"room_{uuid4().hex[:8]}",
                seller_id=room_data["seller_id"],
                name=room_data["name"],
                type=room_data["type"],
                base_price=room_data["base_price"],
                floor_price=room_data["floor_price"],
                max_occupancy=room_data["max_occupancy"],
            )
            session.add(room)
            print(f"  ✓ {room_data['name']} (${room_data['base_price']/100:.2f} base)")
        
        await session.commit()
        
        print("\n✅ Demo data created successfully!")
        print("\n📋 Demo Credentials:")
        print("  Buyer:")
        print("    Email: demo-buyer@example.com")
        print("    Password: demo1234")
        print("  Seller:")
        print("    Email: demo-hotel@example.com")
        print("    Password: demo1234")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_demo_data())
