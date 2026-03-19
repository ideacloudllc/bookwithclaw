# BookWithClaw Seller API Integration Guide
## For Hotels With Custom Booking Systems

---

## Overview

This guide is for **hotel developers** who want to:
- Programmatically manage rooms, rates, and availability
- Receive booking notifications via webhook
- Integrate BookWithClaw offers into existing PMS (Property Management System)
- Build custom UIs on top of the BookWithClaw Exchange

**For non-technical hotels:** Use the web dashboard instead. This is optional.

---

## Authentication

### Get Your API Key

1. Log in to your seller dashboard
2. Go to **Settings → API Keys**
3. Click **Generate New Key**
4. Copy the key (you'll use it in all requests)

### Make Authenticated Requests

All requests must include your API key in the header:

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://api.bookwithclaw.ai/v1/...
```

---

## Base URL

```
Production: https://api.bookwithclaw.ai/v1
Sandbox:    https://sandbox.bookwithclaw.ai/v1
```

**Use sandbox for testing. No real money changes hands.**

---

## Core Endpoints

### 1. List Your Rooms

```http
GET /rooms
```

**Response:**
```json
{
  "rooms": [
    {
      "room_id": "rm_abc123",
      "hotel_id": "ht_xyz789",
      "name": "Deluxe King",
      "capacity": 2,
      "base_rate": 350,
      "floor_price": 200,
      "availability": "open",
      "photos": [
        {
          "url": "https://...",
          "order": 1
        }
      ],
      "created_at": "2026-03-19T12:00:00Z"
    }
  ]
}
```

---

### 2. Update Room Pricing

```http
PATCH /rooms/{room_id}
Content-Type: application/json

{
  "base_rate": 375,
  "floor_price": 225
}
```

**Why update rate?** Seasonal pricing, occupancy adjustments, competitor matching.

**Response:** Updated room object (same as above)

---

### 3. Update Room Availability

```http
PATCH /rooms/{room_id}/availability
Content-Type: application/json

{
  "status": "open",  # or "blocked"
  "dates": {
    "start": "2026-04-01",
    "end": "2026-04-30"
  }
}
```

**Use case:** Block dates for maintenance, staff events, private bookings.

---

### 4. Get Active Offers

```http
GET /offers?status=pending
```

**Response:**
```json
{
  "offers": [
    {
      "offer_id": "of_abc123",
      "room_id": "rm_abc123",
      "buyer_id": "by_xyz789",
      "dates": {
        "checkin": "2026-03-25",
        "checkout": "2026-03-27"
      },
      "guests": 2,
      "proposed_price": 320,
      "your_floor": 200,
      "your_base": 350,
      "status": "negotiating",
      "rounds": 2,
      "created_at": "2026-03-19T14:22:00Z",
      "expires_at": "2026-03-19T14:52:00Z"
    }
  ]
}
```

---

### 5. Accept an Offer

```http
POST /offers/{offer_id}/accept
Content-Type: application/json

{
  "agreed_price": 320,
  "confirmed": true
}
```

**Response:**
```json
{
  "offer_id": "of_abc123",
  "status": "accepted",
  "settlement_initiated": true,
  "estimated_payout": 314.40,
  "payout_date": "2026-03-21"
}
```

**How we calculate payout:**
```
Agreed price:              $320.00
Platform fee (1.8%):        -$5.76
Stripe fee (2.9% + $0.30): -$9.58
Your payout:              $304.66
```

---

### 6. Reject an Offer

```http
POST /offers/{offer_id}/reject
Content-Type: application/json

{
  "reason": "Too low, below floor price"
}
```

**Status changes to:** `rejected` (AI agent notifies buyer)

---

### 7. Counter-Offer

```http
POST /offers/{offer_id}/counter
Content-Type: application/json

{
  "suggested_price": 340,
  "negotiation_message": "Can we do $340 for the cleaner checkout?"
}
```

**Response:** Offer moves to `counter_offered`, buyer gets notification

---

### 8. Get Booking Details

```http
GET /bookings/{booking_id}
```

**Response:**
```json
{
  "booking_id": "bk_abc123",
  "offer_id": "of_abc123",
  "room_id": "rm_abc123",
  "buyer_name": "Jane Doe",
  "buyer_email": "jane@example.com",
  "checkin": "2026-03-25",
  "checkout": "2026-03-27",
  "guests": 2,
  "agreed_price": 320,
  "platform_fee": 5.76,
  "stripe_fee": 9.58,
  "your_payout": 304.66,
  "payment_status": "settled",
  "settlement_date": "2026-03-21T08:30:00Z",
  "special_requests": "Early check-in if possible"
}
```

---

## Webhooks

### Register a Webhook Endpoint

```http
POST /webhooks
Content-Type: application/json

{
  "url": "https://your-hotel.com/bookwithclaw-webhooks",
  "events": ["offer.created", "offer.accepted", "booking.settled"]
}
```

### Listen for Events

Your endpoint should accept POST requests:

```
POST https://your-hotel.com/bookwithclaw-webhooks
```

**Event: `offer.created`**
```json
{
  "event": "offer.created",
  "timestamp": "2026-03-19T14:22:00Z",
  "data": {
    "offer_id": "of_abc123",
    "room_id": "rm_abc123",
    "proposed_price": 320,
    "checkin": "2026-03-25",
    "checkout": "2026-03-27"
  }
}
```

**Event: `offer.accepted`**
```json
{
  "event": "offer.accepted",
  "timestamp": "2026-03-19T14:45:00Z",
  "data": {
    "offer_id": "of_abc123",
    "booking_id": "bk_abc123",
    "agreed_price": 320,
    "buyer_name": "Jane Doe"
  }
}
```

**Event: `booking.settled`**
```json
{
  "event": "booking.settled",
  "timestamp": "2026-03-21T08:30:00Z",
  "data": {
    "booking_id": "bk_abc123",
    "your_payout": 304.66,
    "payment_status": "completed",
    "settlement_date": "2026-03-21"
  }
}
```

### Verify Webhook Signatures

All webhooks include a signature header:

```http
X-BookWithClaw-Signature: sha256=abc123def456...
```

Verify it:

```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)

# Usage
is_valid = verify_webhook(
    payload_body,
    request.headers['X-BookWithClaw-Signature'],
    YOUR_WEBHOOK_SECRET
)
```

---

## Example: Sync PMS with BookWithClaw

### Use Case: Update BookWithClaw rates when your PMS rate changes

```python
import requests

API_KEY = "sk_seller_abc123xyz"
BASE_URL = "https://api.bookwithclaw.ai/v1"

def sync_rates_to_bookwithclaw(room_id, new_rate, floor_price):
    """Update room pricing on BookWithClaw"""
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "base_rate": new_rate,
        "floor_price": floor_price
    }
    
    response = requests.patch(
        f"{BASE_URL}/rooms/{room_id}",
        json=payload,
        headers=headers
    )
    
    if response.status_code == 200:
        print(f"Rate updated: ${new_rate}")
    else:
        print(f"Error: {response.json()}")

# Example: Update Deluxe King to $375 base, $225 floor
sync_rates_to_bookwithclaw("rm_abc123", 375, 225)
```

---

## Example: Auto-Accept Offers Above Price Threshold

```python
import requests

def auto_accept_good_offers(min_price_threshold):
    """Accept any offer above a certain price"""
    
    headers = {"Authorization": f"Bearer {API_KEY}"}
    
    # Get pending offers
    response = requests.get(
        f"{BASE_URL}/offers?status=pending",
        headers=headers
    )
    
    offers = response.json()["offers"]
    
    for offer in offers:
        if offer["proposed_price"] >= min_price_threshold:
            # Auto-accept
            requests.post(
                f"{BASE_URL}/offers/{offer['offer_id']}/accept",
                json={"agreed_price": offer["proposed_price"]},
                headers=headers
            )
            print(f"Auto-accepted offer {offer['offer_id']} at ${offer['proposed_price']}")

# Accept anything $300 or higher
auto_accept_good_offers(300)
```

---

## Example: Block Dates When PMS Shows Maintenance

```python
import requests
from datetime import datetime, timedelta

def block_maintenance_dates(room_id, start_date, end_date):
    """Block room from BookWithClaw during maintenance"""
    
    headers = {"Authorization": f"Bearer {API_KEY}"}
    
    payload = {
        "status": "blocked",
        "dates": {
            "start": start_date,
            "end": end_date
        }
    }
    
    response = requests.patch(
        f"{BASE_URL}/rooms/{room_id}/availability",
        json=payload,
        headers=headers
    )
    
    print(f"Room blocked: {start_date} to {end_date}")

# Block for a week starting next Monday
start = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
end = (datetime.now() + timedelta(days=8)).strftime("%Y-%m-%d")
block_maintenance_dates("rm_abc123", start, end)
```

---

## Error Handling

### Common Error Responses

**401 Unauthorized**
```json
{
  "error": "UNAUTHORIZED",
  "message": "Invalid or expired API key"
}
```

**400 Bad Request**
```json
{
  "error": "INVALID_REQUEST",
  "message": "Missing required field: base_rate"
}
```

**404 Not Found**
```json
{
  "error": "NOT_FOUND",
  "message": "Room rm_abc123 not found"
}
```

**429 Rate Limited**
```json
{
  "error": "RATE_LIMITED",
  "message": "Max 100 requests per minute"
}
```

---

## Rate Limits

- **REST API:** 100 requests/minute
- **Webhooks:** No limit (we retry on failure)
- **Concurrent connections:** 10 per API key

---

## Sandbox Testing

Use `https://sandbox.bookwithclaw.ai/v1` for testing.

**Test cards:**
```
4242 4242 4242 4242  → Successful charge
4000 0000 0000 0002  → Card declined
```

No real money changes hands in sandbox.

---

## Postman Collection

Download our Postman collection for quick API testing:

```
https://bookwithclaw.ai/postman-collection.json
```

Import into Postman, set your API key, and start testing.

---

## Support

- **API Issues:** support@bookwithclaw.ai
- **Status Page:** status.bookwithclaw.ai
- **Docs:** https://docs.bookwithclaw.ai
- **Slack:** Join our developer community (link in dashboard)

---

## Best Practices

1. **Use webhooks instead of polling** — More efficient, real-time updates
2. **Verify webhook signatures** — Ensure requests are from BookWithClaw
3. **Handle retries gracefully** — Webhooks retry for 24 hours
4. **Idempotent operations** — Always include `idempotency-key` on POST requests
5. **Monitor rate limits** — Check headers for `X-RateLimit-Remaining`

---

## Changelog

**v1.0.0** (2026-03-19)
- Initial API release
- Rooms, offers, bookings endpoints
- Webhook support
- Sandbox environment
