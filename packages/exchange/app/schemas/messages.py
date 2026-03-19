"""Pydantic message schemas for validation."""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class BaseMessageSchema(BaseModel):
    """Base schema for all messages."""

    type: str
    round_num: int = Field(..., gt=0)
    timestamp: str
    signature: str = Field(..., min_length=128, max_length=128)
    payload: Dict[str, Any]


class BuyerIntentMessage(BaseMessageSchema):
    """Buyer intent message schema."""

    type: str = "BuyerIntent"

    class Config:
        json_schema_extra = {
            "example": {
                "type": "BuyerIntent",
                "round_num": 1,
                "timestamp": "2026-01-01T00:00:00Z",
                "signature": "00" * 64,
                "payload": {
                    "intent_id": "uuid",
                    "vertical": "hotels",
                    "buyer_agent_id": "uuid",
                    "budget_ceiling": 50000,
                    "max_negotiation_rounds": 10,
                    "preferred_terms": {},
                    "vertical_fields": {},
                },
            }
        }


class SellerAskMessage(BaseMessageSchema):
    """Seller ask message schema."""

    type: str = "SellerAsk"

    class Config:
        json_schema_extra = {
            "example": {
                "type": "SellerAsk",
                "round_num": 1,
                "timestamp": "2026-01-01T00:00:00Z",
                "signature": "00" * 64,
                "payload": {
                    "ask_id": "uuid",
                    "vertical": "hotels",
                    "seller_agent_id": "uuid",
                    "session_id": "uuid",
                    "price": 40000,
                    "floor_price": 30000,
                    "terms": {},
                    "seller_reputation_score": 85,
                    "stake_amount": 5000,
                    "vertical_fields": {},
                },
            }
        }


class BuyerCounterOfferMessage(BaseMessageSchema):
    """Buyer counter-offer message schema."""

    type: str = "BuyerCounterOffer"


class SellerCounterOfferMessage(BaseMessageSchema):
    """Seller counter-offer message schema."""

    type: str = "SellerCounterOffer"


class DealAcceptedMessage(BaseMessageSchema):
    """Deal accepted message schema."""

    type: str = "DealAccepted"

    class Config:
        json_schema_extra = {
            "example": {
                "type": "DealAccepted",
                "round_num": 2,
                "timestamp": "2026-01-01T00:01:00Z",
                "signature": "00" * 64,
                "payload": {
                    "session_id": "uuid",
                    "agent_id": "uuid",
                    "agreed_price": 40000,
                },
            }
        }


class SessionWalkawayMessage(BaseMessageSchema):
    """Session walkaway message schema."""

    type: str = "SessionWalkaway"


class SettlementCompleteMessage(BaseMessageSchema):
    """Settlement complete message schema."""

    type: str = "SettlementComplete"


class SettlementFailedMessage(BaseMessageSchema):
    """Settlement failed message schema."""

    type: str = "SettlementFailed"
