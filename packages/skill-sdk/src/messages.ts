/**
 * Message type definitions for BookWithClaw Exchange.
 * All message schemas use Zod for runtime validation.
 */

import { z } from "zod";

/**
 * Base message schema (shared by all message types)
 */
const BaseMessage = z.object({
  type: z.string(),
  round_num: z.number().int().positive(),
  timestamp: z.string().datetime(),
  signature: z.string().length(128), // 64-byte sig in hex
  payload: z.record(z.any()),
});

export type BaseMessage = z.infer<typeof BaseMessage>;

/**
 * BUYER INTENT — Buyer announces availability and preferences
 */
export const BuyerIntentSchema = BaseMessage.extend({
  type: z.literal("BuyerIntent"),
  payload: z.object({
    intent_id: z.string().uuid(),
    vertical: z.string(),
    buyer_agent_id: z.string().uuid(),
    budget_ceiling: z.number().int().positive(), // in cents
    max_negotiation_rounds: z.number().int().positive(),
    preferred_terms: z.record(z.any()).optional(),
    vertical_fields: z.record(z.any()), // e.g., hotels: checkin, checkout, room_type
  }),
});

export type BuyerIntent = z.infer<typeof BuyerIntentSchema>;

/**
 * SELLER ASK — Seller offers availability and pricing
 */
export const SellerAskSchema = BaseMessage.extend({
  type: z.literal("SellerAsk"),
  payload: z.object({
    ask_id: z.string().uuid(),
    vertical: z.string(),
    seller_agent_id: z.string().uuid(),
    session_id: z.string().uuid(),
    price: z.number().int().nonnegative(), // in cents
    floor_price: z.number().int().nonnegative(),
    terms: z.record(z.any()).optional(),
    seller_reputation_score: z.number().int().min(0).max(100),
    stake_amount: z.number().int().nonnegative(),
    vertical_fields: z.record(z.any()),
  }),
});

export type SellerAsk = z.infer<typeof SellerAskSchema>;

/**
 * BUYER COUNTER-OFFER — Buyer adjusts price/terms
 */
export const BuyerCounterOfferSchema = BaseMessage.extend({
  type: z.literal("BuyerCounterOffer"),
  payload: z.object({
    session_id: z.string().uuid(),
    buyer_agent_id: z.string().uuid(),
    round_num: z.number().int().positive(),
    counter_price: z.number().int().positive(),
    preferred_terms: z.record(z.any()).optional(),
  }),
});

export type BuyerCounterOffer = z.infer<typeof BuyerCounterOfferSchema>;

/**
 * SELLER COUNTER-OFFER — Seller adjusts price/terms
 */
export const SellerCounterOfferSchema = BaseMessage.extend({
  type: z.literal("SellerCounterOffer"),
  payload: z.object({
    session_id: z.string().uuid(),
    seller_agent_id: z.string().uuid(),
    round_num: z.number().int().positive(),
    counter_price: z.number().int().positive(),
    terms: z.record(z.any()).optional(),
  }),
});

export type SellerCounterOffer = z.infer<typeof SellerCounterOfferSchema>;

/**
 * DEAL ACCEPTED — Either party accepts the current offer
 */
export const DealAcceptedSchema = BaseMessage.extend({
  type: z.literal("DealAccepted"),
  payload: z.object({
    session_id: z.string().uuid(),
    agent_id: z.string().uuid(),
    agreed_price: z.number().int().positive(),
  }),
});

export type DealAccepted = z.infer<typeof DealAcceptedSchema>;

/**
 * SESSION WALKAWAY — Agent abandons negotiation
 */
export const SessionWalkawaySchema = BaseMessage.extend({
  type: z.literal("SessionWalkaway"),
  payload: z.object({
    session_id: z.string().uuid(),
    agent_id: z.string().uuid(),
    reason: z.string(),
  }),
});

export type SessionWalkaway = z.infer<typeof SessionWalkawaySchema>;

/**
 * SETTLEMENT COMPLETE — Both parties notified of settlement
 */
export const SettlementCompleteSchema = BaseMessage.extend({
  type: z.literal("SettlementComplete"),
  payload: z.object({
    session_id: z.string().uuid(),
    transaction_id: z.string().uuid(),
    booking_ref: z.string(),
    agreed_price: z.number().int().positive(),
    platform_fee: z.number().int().nonnegative(),
    payout: z.number().int().nonnegative(), // seller payout in cents
  }),
});

export type SettlementComplete = z.infer<typeof SettlementCompleteSchema>;

/**
 * SETTLEMENT FAILED — Settlement could not be completed
 */
export const SettlementFailedSchema = BaseMessage.extend({
  type: z.literal("SettlementFailed"),
  payload: z.object({
    session_id: z.string().uuid(),
    reason: z.string(),
  }),
});

export type SettlementFailed = z.infer<typeof SettlementFailedSchema>;

/**
 * Union of all message types
 */
export const MessageSchema = z.union([
  BuyerIntentSchema,
  SellerAskSchema,
  BuyerCounterOfferSchema,
  SellerCounterOfferSchema,
  DealAcceptedSchema,
  SessionWalkawaySchema,
  SettlementCompleteSchema,
  SettlementFailedSchema,
]);

export type Message = z.infer<typeof MessageSchema>;

/**
 * Parse and validate a message
 */
export function parseMessage(data: unknown): Message {
  return MessageSchema.parse(data);
}
