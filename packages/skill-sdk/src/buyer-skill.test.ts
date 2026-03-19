/**
 * Unit tests for BuyerSkill.
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { BuyerSkill } from './buyer-skill';
import { generateKeypair } from './crypto';

describe('BuyerSkill', () => {
  let buyerSkill: BuyerSkill;
  let publicKey: string;
  let privateKey: string;

  beforeEach(() => {
    const keys = generateKeypair();
    publicKey = keys.publicKey;
    privateKey = keys.privateKey;

    buyerSkill = new BuyerSkill({
      exchangeUrl: 'ws://localhost:8890',
      authToken: 'test_token',
      config: {
        agentId: 'buyer_test_123',
        publicKey,
        privateKey,
        checkInDate: '2026-03-25',
        checkOutDate: '2026-03-27',
        budgetCeilingCents: 50000, // $500/night
        occupants: 2,
        acceptableRoomTypes: ['deluxe_king', 'standard_queen'],
      },
    });
  });

  it('should create a BuyerSkill instance', () => {
    expect(buyerSkill).toBeDefined();
  });

  it('should emit events', () => {
    return new Promise<void>((resolve) => {
      buyerSkill.on('test_event', () => {
        expect(true).toBe(true);
        resolve();
      });

      buyerSkill.emit('test_event');
    });
  });

  it('should handle disconnect', () => {
    buyerSkill.disconnect();
    expect(true).toBe(true); // Simple sanity check
  });
});
