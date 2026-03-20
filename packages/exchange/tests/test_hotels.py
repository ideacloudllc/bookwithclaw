"""Tests for hotel vertical schema validator."""

import pytest
from pydantic import ValidationError

from app.verticals.hotels import HotelVerticalValidator, HotelBuyerIntent, HotelSellerAsk


@pytest.mark.asyncio
async def test_validate_intent_valid():
    """Test validating a valid hotel buyer intent."""
    validator = HotelVerticalValidator()

    valid_intent = {
        "checkin_date": "2026-04-01",
        "checkout_date": "2026-04-05",
        "occupants": 2,
        "acceptable_room_types": ["double", "suite"],
    }

    result = validator.validate_intent(valid_intent)
    assert isinstance(result, HotelBuyerIntent)
    assert result.occupants == 2
    assert result.checkin_date == "2026-04-01"


@pytest.mark.asyncio
async def test_validate_ask_valid():
    """Test validating a valid hotel seller ask."""
    validator = HotelVerticalValidator()

    valid_ask = {
        "checkin_date": "2026-04-01",
        "checkout_date": "2026-04-05",
        "room_type": "double",
        "max_occupants": 2,
    }

    result = validator.validate_ask(valid_ask)
    assert isinstance(result, HotelSellerAsk)
    assert result.room_type == "double"
    assert result.max_occupants == 2


@pytest.mark.asyncio
async def test_validate_intent_invalid_date_format():
    """Test rejecting intent with invalid date format."""
    validator = HotelVerticalValidator()

    invalid_intent = {
        "checkin_date": "04-01-2026",  # Wrong format
        "checkout_date": "2026-04-05",
        "occupants": 2,
    }

    with pytest.raises(ValidationError):
        validator.validate_intent(invalid_intent)


@pytest.mark.asyncio
async def test_validate_ask_invalid_occupants():
    """Test rejecting ask with invalid occupants."""
    validator = HotelVerticalValidator()

    invalid_ask = {
        "checkin_date": "2026-04-01",
        "checkout_date": "2026-04-05",
        "room_type": "double",
        "max_occupants": 0,  # Must be at least 1
    }

    with pytest.raises(ValidationError):
        validator.validate_ask(invalid_ask)


@pytest.mark.asyncio
async def test_check_compatibility_compatible():
    """Test compatibility check for compatible intent and ask."""
    validator = HotelVerticalValidator()

    intent = {
        "checkin_date": "2026-04-01",
        "checkout_date": "2026-04-05",
        "occupants": 2,
        "acceptable_room_types": ["double", "suite"],
    }

    ask = {
        "checkin_date": "2026-04-01",
        "checkout_date": "2026-04-05",
        "room_type": "double",
        "max_occupants": 2,
    }

    assert validator.check_compatibility(intent, ask)


@pytest.mark.asyncio
async def test_check_compatibility_incompatible_dates():
    """Test incompatibility detection for conflicting dates."""
    validator = HotelVerticalValidator()

    intent = {
        "checkin_date": "2026-04-01",
        "checkout_date": "2026-04-05",
        "occupants": 2,
    }

    # Seller not available when buyer wants to check in
    ask = {
        "checkin_date": "2026-04-02",
        "checkout_date": "2026-04-05",
        "room_type": "double",
        "max_occupants": 2,
    }

    assert not validator.check_compatibility(intent, ask)


@pytest.mark.asyncio
async def test_check_compatibility_incompatible_occupancy():
    """Test incompatibility detection for insufficient capacity."""
    validator = HotelVerticalValidator()

    intent = {
        "checkin_date": "2026-04-01",
        "checkout_date": "2026-04-05",
        "occupants": 4,  # 4 people needed
    }

    ask = {
        "checkin_date": "2026-04-01",
        "checkout_date": "2026-04-05",
        "room_type": "double",
        "max_occupants": 2,  # Only fits 2
    }

    assert not validator.check_compatibility(intent, ask)


@pytest.mark.asyncio
async def test_check_compatibility_incompatible_room_type():
    """Test incompatibility detection for room type mismatch."""
    validator = HotelVerticalValidator()

    intent = {
        "checkin_date": "2026-04-01",
        "checkout_date": "2026-04-05",
        "occupants": 2,
        "acceptable_room_types": ["suite"],  # Only suite
    }

    ask = {
        "checkin_date": "2026-04-01",
        "checkout_date": "2026-04-05",
        "room_type": "double",  # Offering double
        "max_occupants": 2,
    }

    assert not validator.check_compatibility(intent, ask)
