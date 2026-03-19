"""WebSocket session endpoints for negotiation."""

import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Set

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.order_book import OrderBook
from app.core.signing import verify_signature, canonical_json
from app.core.state_machine import (
    InvalidStateTransitionError,
    NegotiationStateMachine,
)
from app.dependencies import get_current_agent
from app.database import SessionLocal
from app.models.session import SessionState
from app.schemas.messages import (
    DealAcceptedMessage,
    BuyerIntentMessage,
    SellerAskMessage,
)

router = APIRouter(prefix="/sessions", tags=["sessions"])
logger = logging.getLogger(__name__)

# Active WebSocket connections per session
active_connections: Dict[str, Set[WebSocket]] = {}


class ConnectionManager:
    """Manage WebSocket connections for a session."""

    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        """Register a connection."""
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = set()
        self.active_connections[session_id].add(websocket)

    async def disconnect(self, session_id: str, websocket: WebSocket):
        """Unregister a connection."""
        if session_id in self.active_connections:
            self.active_connections[session_id].discard(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]

    async def broadcast(self, session_id: str, message: dict):
        """Send message to all connected clients in session."""
        if session_id not in self.active_connections:
            return

        for connection in self.active_connections[session_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {e}")


manager = ConnectionManager()


@router.post("/")
async def create_session(
    current_agent: dict = Depends(get_current_agent),
) -> dict:
    """
    Create a new negotiation session.

    Returns:
        Session ID and WebSocket URL
    """
    session_id = str(uuid.uuid4())
    return {
        "session_id": session_id,
        "websocket_url": f"ws://localhost:8000/ws/session/{session_id}",
    }


@router.websocket("/ws/session/{session_id}")
async def websocket_endpoint(session_id: str, websocket: WebSocket):
    """
    Main negotiation WebSocket channel.

    Protocol:
    1. Client connects with JWT token in query param
    2. Receives confirmation
    3. Send/receive JSON messages
    4. All messages must be signed with Ed25519
    """
    # Verify auth token
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    from app.core.signing import verify_jwt_token
    payload = verify_jwt_token(token)
    if not payload:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    agent_id = payload.get("agent_id")
    public_key = payload.get("public_key")

    # Connect
    await manager.connect(session_id, websocket)
    logger.info(f"Agent {agent_id} connected to session {session_id}")

    # Get database session and services
    from app.main import redis_client
    async with SessionLocal() as db:
        order_book = OrderBook(redis_client)
        state_machine = NegotiationStateMachine(db)

        try:
            # Listen for messages
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)

                # Verify signature
                msg_copy = message.copy()
                sig = msg_copy.pop("signature")
                msg_bytes = canonical_json(msg_copy).encode()

                if not verify_signature(msg_bytes, sig, public_key):
                    await websocket.send_json(
                        {
                            "error": "INVALID_SIGNATURE",
                            "message": "Message signature verification failed",
                        }
                    )
                    continue

                # Route message by type
                msg_type = message.get("type")

                if msg_type == "BuyerIntent":
                    await handle_buyer_intent(
                        message,
                        agent_id,
                        session_id,
                        order_book,
                        state_machine,
                        manager,
                        db,
                    )

                elif msg_type == "SellerAsk":
                    await handle_seller_ask(
                        message,
                        agent_id,
                        session_id,
                        state_machine,
                        manager,
                        db,
                    )

                elif msg_type == "DealAccepted":
                    await handle_deal_accepted(
                        message,
                        agent_id,
                        session_id,
                        state_machine,
                        manager,
                        db,
                    )

                else:
                    await websocket.send_json(
                        {
                            "error": "UNKNOWN_MESSAGE_TYPE",
                            "message": f"Unknown message type: {msg_type}",
                        }
                    )

        except WebSocketDisconnect:
            await manager.disconnect(session_id, websocket)
            logger.info(f"Agent {agent_id} disconnected from session {session_id}")

        except Exception as e:
            logger.error(f"Error in websocket handler: {e}")
            await websocket.send_json({"error": "INTERNAL_ERROR", "message": str(e)})
            await manager.disconnect(session_id, websocket)


@router.get("/{session_id}")
async def get_session_status(
    session_id: str,
    current_agent: dict = Depends(get_current_agent),
) -> dict:
    """Get session status and history."""
    async with SessionLocal() as db:
        state_machine = NegotiationStateMachine(db)
        session = await state_machine.get_session(session_id)

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found",
            )

        return {
            "session_id": session.session_id,
            "state": session.state.value,
            "buyer_agent_id": session.buyer_agent_id,
            "seller_agent_id": session.seller_agent_id,
            "round_number": session.round_number,
            "agreed_price": session.agreed_price,
            "created_at": session.created_at.isoformat(),
        }


# Private message handlers


async def handle_buyer_intent(
    message: dict,
    agent_id: str,
    session_id: str,
    order_book: OrderBook,
    state_machine: NegotiationStateMachine,
    manager: ConnectionManager,
    db: AsyncSession,
):
    """Handle buyer intent message."""
    payload = message.get("payload", {})
    intent_id = payload.get("intent_id")
    vertical = payload.get("vertical", "hotels")

    # Create session if not exists
    session = await state_machine.get_session(session_id)
    if not session:
        session = await state_machine.open_session(
            session_id,
            agent_id,
            vertical,
            max_rounds=payload.get("max_negotiation_rounds", 10),
        )

    # Transition OPEN -> MATCHING
    try:
        session = await state_machine.transition(session_id, SessionState.MATCHING)
    except InvalidStateTransitionError:
        pass  # Already in MATCHING or later

    # Store intent
    await state_machine.store_intent(session_id, payload)

    # Publish to order book
    await order_book.publish_intent(intent_id, payload)

    # Find matching asks
    matches = await order_book.get_matching_asks(payload, limit=5)

    # Send response to buyer
    await manager.broadcast(
        session_id,
        {
            "type": "IntentAcknowledged",
            "session_id": session_id,
            "matches": len(matches),
        },
    )

    logger.info(f"Buyer intent {intent_id} published with {len(matches)} matches")


async def handle_seller_ask(
    message: dict,
    agent_id: str,
    session_id: str,
    state_machine: NegotiationStateMachine,
    manager: ConnectionManager,
    db: AsyncSession,
):
    """Handle seller ask message."""
    payload = message.get("payload", {})

    session = await state_machine.get_session(session_id)
    if not session:
        await manager.broadcast(
            session_id,
            {
                "error": "SESSION_NOT_FOUND",
                "message": f"Session {session_id} not found",
            },
        )
        return

    # Set seller if not set
    if not session.seller_agent_id:
        await state_machine.set_seller(session_id, agent_id)

    # Transition MATCHING -> NEGOTIATING
    try:
        session = await state_machine.transition(session_id, SessionState.NEGOTIATING)
    except InvalidStateTransitionError:
        pass  # Already negotiating

    # Store ask
    await state_machine.store_ask(session_id, payload)

    # Broadcast ask to buyer
    await manager.broadcast(
        session_id,
        {
            "type": "SellerAsk",
            "payload": payload,
        },
    )

    logger.info(f"Seller ask for session {session_id} at price {payload.get('price')}")


async def handle_deal_accepted(
    message: dict,
    agent_id: str,
    session_id: str,
    state_machine: NegotiationStateMachine,
    manager: ConnectionManager,
    db: AsyncSession,
):
    """Handle deal accepted message."""
    payload = message.get("payload", {})
    agreed_price = payload.get("agreed_price")

    # Record agreed price
    session = await state_machine.agree_price(session_id, agreed_price)

    # Broadcast confirmation to both parties
    await manager.broadcast(
        session_id,
        {
            "type": "DealAccepted",
            "session_id": session_id,
            "agreed_price": agreed_price,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )

    logger.info(f"Deal accepted for session {session_id} at price {agreed_price}")
