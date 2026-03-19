"""Hotel vertical schema validation."""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, validator


class HotelBuyerIntent(BaseModel):
    """Hotel buyer intent fields."""

    checkin_date: str  # YYYY-MM-DD
    checkout_date: str  # YYYY-MM-DD
    occupants: int
    acceptable_room_types: Optional[list[str]] = None
    preferred_terms: Optional[Dict[str, Any]] = None

    @validator("checkin_date", "checkout_date", pre=True)
    def validate_dates(cls, v):
        """Validate date format."""
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD.")

    @validator("occupants", pre=True)
    def validate_occupants(cls, v):
        """Validate occupants is positive."""
        if v < 1:
            raise ValueError("Occupants must be at least 1.")
        return v


class HotelSellerAsk(BaseModel):
    """Hotel seller ask fields."""

    checkin_date: str  # YYYY-MM-DD
    checkout_date: str  # YYYY-MM-DD
    room_type: str
    max_occupants: int
    terms: Optional[Dict[str, Any]] = None

    @validator("checkin_date", "checkout_date", pre=True)
    def validate_dates(cls, v):
        """Validate date format."""
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD.")

    @validator("max_occupants", pre=True)
    def validate_occupants(cls, v):
        """Validate max_occupants is positive."""
        if v < 1:
            raise ValueError("Max occupants must be at least 1.")
        return v


class HotelVerticalValidator:
    """Validate hotel vertical intents and asks."""

    @staticmethod
    def validate_intent(intent_fields: Dict[str, Any]) -> HotelBuyerIntent:
        """
        Validate hotel buyer intent fields.

        Args:
            intent_fields: Intent vertical_fields dict

        Returns:
            Validated HotelBuyerIntent

        Raises:
            ValidationError if invalid
        """
        return HotelBuyerIntent(**intent_fields)

    @staticmethod
    def validate_ask(ask_fields: Dict[str, Any]) -> HotelSellerAsk:
        """
        Validate hotel seller ask fields.

        Args:
            ask_fields: Ask vertical_fields dict

        Returns:
            Validated HotelSellerAsk

        Raises:
            ValidationError if invalid
        """
        return HotelSellerAsk(**ask_fields)

    @staticmethod
    def check_compatibility(
        intent: Dict[str, Any],
        ask: Dict[str, Any],
    ) -> bool:
        """
        Check if buyer intent and seller ask are compatible.

        Returns True only if:
        - ask.checkin_date <= intent.checkin_date (seller available from)
        - ask.checkout_date >= intent.checkout_date (seller available to)
        - ask.room_type in intent.acceptable_room_types (if specified)
        - ask.max_occupants >= intent.occupants

        Args:
            intent: Intent vertical_fields dict
            ask: Ask vertical_fields dict

        Returns:
            True if compatible, False otherwise
        """
        # Parse dates
        intent_checkin = intent.get("checkin_date")
        intent_checkout = intent.get("checkout_date")
        ask_checkin = ask.get("checkin_date")
        ask_checkout = ask.get("checkout_date")

        # Date compatibility
        if ask_checkin and intent_checkin:
            if ask_checkin > intent_checkin:
                return False  # Seller not available when buyer wants to check in

        if ask_checkout and intent_checkout:
            if ask_checkout < intent_checkout:
                return False  # Seller not available when buyer wants to check out

        # Occupancy compatibility
        intent_occupants = intent.get("occupants", 0)
        ask_max_occupants = ask.get("max_occupants", 0)
        if ask_max_occupants < intent_occupants:
            return False

        # Room type compatibility
        acceptable_types = intent.get("acceptable_room_types", [])
        ask_room_type = ask.get("room_type")
        if acceptable_types and ask_room_type:
            if ask_room_type not in acceptable_types:
                return False

        return True
