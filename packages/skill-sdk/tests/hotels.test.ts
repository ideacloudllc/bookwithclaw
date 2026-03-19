/**
 * Tests for hotel vertical schema.
 */

import { describe, it, expect } from "vitest";

import {
  HotelBuyerIntentSchema,
  HotelSellerAskSchema,
  validateHotelCompatibility,
} from "../src/schemas/hotels";

describe("Hotel Vertical Schema", () => {
  it("validates hotel buyer intent", () => {
    const intent = {
      checkin_date: "2026-04-01",
      checkout_date: "2026-04-05",
      occupants: 2,
      acceptable_room_types: ["double", "suite"],
      preferred_terms: {
        free_wifi: true,
        breakfast_included: true,
      },
    };

    const result = HotelBuyerIntentSchema.safeParse(intent);
    expect(result.success).toBe(true);
  });

  it("validates hotel seller ask", () => {
    const ask = {
      checkin_date: "2026-04-01",
      checkout_date: "2026-04-05",
      room_type: "double",
      max_occupants: 2,
      terms: {
        free_wifi: true,
        breakfast_included: false,
      },
    };

    const result = HotelSellerAskSchema.safeParse(ask);
    expect(result.success).toBe(true);
  });

  it("rejects buyer intent with invalid dates", () => {
    const intent = {
      checkin_date: "2026-04-05",
      checkout_date: "2026-04-01", // Checkout before checkin
      occupants: 2,
    };

    const result = HotelBuyerIntentSchema.safeParse(intent);
    expect(result.success).toBe(false);
  });

  it("checks compatibility between buyer and seller", () => {
    const buyer = {
      checkin_date: "2026-04-01",
      checkout_date: "2026-04-05",
      occupants: 2,
      acceptable_room_types: ["double"],
    };

    const seller = {
      checkin_date: "2026-04-01",
      checkout_date: "2026-04-05",
      room_type: "double",
      max_occupants: 2,
    };

    const compatible = validateHotelCompatibility(buyer, seller);
    expect(compatible).toBe(true);
  });

  it("detects incompatible dates", () => {
    const buyer = {
      checkin_date: "2026-04-01",
      checkout_date: "2026-04-05",
      occupants: 2,
    };

    const seller = {
      checkin_date: "2026-04-02", // After buyer's checkin
      checkout_date: "2026-04-05",
      room_type: "double",
      max_occupants: 2,
    };

    const compatible = validateHotelCompatibility(buyer, seller);
    expect(compatible).toBe(false);
  });

  it("detects insufficient occupancy", () => {
    const buyer = {
      checkin_date: "2026-04-01",
      checkout_date: "2026-04-05",
      occupants: 4,
    };

    const seller = {
      checkin_date: "2026-04-01",
      checkout_date: "2026-04-05",
      room_type: "double",
      max_occupants: 2,
    };

    const compatible = validateHotelCompatibility(buyer, seller);
    expect(compatible).toBe(false);
  });

  it("detects incompatible room types", () => {
    const buyer = {
      checkin_date: "2026-04-01",
      checkout_date: "2026-04-05",
      occupants: 2,
      acceptable_room_types: ["suite"],
    };

    const seller = {
      checkin_date: "2026-04-01",
      checkout_date: "2026-04-05",
      room_type: "double",
      max_occupants: 2,
    };

    const compatible = validateHotelCompatibility(buyer, seller);
    expect(compatible).toBe(false);
  });
});
