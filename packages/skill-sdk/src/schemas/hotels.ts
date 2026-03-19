/**
 * Hotel vertical schema for BookWithClaw.
 */

import { z } from "zod";

/**
 * Hotel buyer intent fields
 */
export const HotelBuyerIntentSchema = z.object({
  checkin_date: z.string().date(),
  checkout_date: z.string().date(),
  occupants: z.number().int().positive(),
  acceptable_room_types: z.array(z.string()).optional(),
  preferred_terms: z
    .object({
      free_wifi: z.boolean().optional(),
      free_parking: z.boolean().optional(),
      breakfast_included: z.boolean().optional(),
      cancellation_policy: z.enum(["strict", "moderate", "flexible"]).optional(),
    })
    .optional(),
});

export type HotelBuyerIntent = z.infer<typeof HotelBuyerIntentSchema>;

/**
 * Hotel seller ask fields
 */
export const HotelSellerAskSchema = z.object({
  checkin_date: z.string().date(),
  checkout_date: z.string().date(),
  room_type: z.string(),
  max_occupants: z.number().int().positive(),
  terms: z
    .object({
      free_wifi: z.boolean().optional(),
      free_parking: z.boolean().optional(),
      breakfast_included: z.boolean().optional(),
      cancellation_policy: z.enum(["strict", "moderate", "flexible"]).optional(),
    })
    .optional(),
});

export type HotelSellerAsk = z.infer<typeof HotelSellerAskSchema>;

/**
 * Validate hotel buyer intent compatibility with ask
 */
export function validateHotelCompatibility(
  intent: HotelBuyerIntent,
  ask: HotelSellerAsk
): boolean {
  // Check dates
  if (ask.checkin_date > intent.checkin_date) return false;
  if (ask.checkout_date < intent.checkout_date) return false;

  // Check occupancy
  if (ask.max_occupants < intent.occupants) return false;

  // Check room type (if buyer specified acceptable types)
  if (intent.acceptable_room_types && intent.acceptable_room_types.length > 0) {
    if (!intent.acceptable_room_types.includes(ask.room_type)) return false;
  }

  return true;
}
