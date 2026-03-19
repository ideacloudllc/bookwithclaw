/**
 * BookWithClaw Skill SDK - Public API
 * 
 * Reference implementations for Hotel Room Buyer and Seller skills.
 */

// Crypto utilities
export { generateKeypair, signMessage, verifySignature, getPublicKeyFromPrivate, canonicalJSON } from './crypto';

// Message types and schemas
export {
  Message,
  BuyerIntentMessage,
  SellerAskMessage,
  BuyerCounterOfferMessage,
  SellerCounterOfferMessage,
  DealAcceptedMessage,
  SessionWalkawayMessage,
  SettlementCompleteMessage,
  parseMessage,
  BuyerIntentMessageSchema,
  SellerAskMessageSchema,
  BuyerCounterOfferMessageSchema,
  SellerCounterOfferMessageSchema,
  DealAcceptedMessageSchema,
  SessionWalkawayMessageSchema,
  SettlementCompleteMessageSchema,
} from './messages';

// WebSocket connection manager
export {
  ExchangeConnection,
  type ExchangeConnectionOptions,
} from './websocket';

// Buyer skill
export {
  BuyerSkill,
  type HotelBuyerConfig,
  type BuyerSkillOptions,
  type SessionResult,
} from './buyer-skill';

// Seller skill
export {
  SellerSkill,
  type HotelSellerConfig,
  type SellerSkillOptions,
} from './seller-skill';
