/**
 * BookWithClaw Skill SDK
 *
 * Public API for building autonomous agent skills that connect to the BookWithClaw Exchange.
 */

// Crypto utilities
export { generateKeypair, signMessage, verifySignature, canonicalJSON } from "./crypto";

// Message types and schemas
export {
  BaseMessage,
  BuyerIntent,
  BuyerIntentSchema,
  SellerAsk,
  SellerAskSchema,
  BuyerCounterOffer,
  BuyerCounterOfferSchema,
  SellerCounterOffer,
  SellerCounterOfferSchema,
  DealAccepted,
  DealAcceptedSchema,
  SessionWalkaway,
  SessionWalkawaySchema,
  SettlementComplete,
  SettlementCompleteSchema,
  SettlementFailed,
  SettlementFailedSchema,
  Message,
  MessageSchema,
  parseMessage,
} from "./messages";

// Vertical schemas
export {
  HotelBuyerIntent,
  HotelBuyerIntentSchema,
  HotelSellerAsk,
  HotelSellerAskSchema,
  validateHotelCompatibility,
} from "./schemas/hotels";

// WebSocket connection
export { ExchangeConnection, ExchangeConnectionOptions } from "./websocket";

// Reference skill implementations
export {
  BuyerSkill,
  BuyerSkillConfig,
  HotelBuyerConfig,
  SkillResult,
} from "./buyer-skill";

export {
  SellerSkill,
  SellerSkillConfig,
  HotelSellerConfig,
} from "./seller-skill";
