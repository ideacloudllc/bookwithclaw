/**
 * Tests for cryptographic utilities.
 */

import { describe, it, expect } from "vitest";

import {
  canonicalJSON,
  generateKeypair,
  signMessage,
  verifySignature,
} from "../src/crypto";

describe("Crypto Utilities", () => {
  it("generates a valid Ed25519 keypair", () => {
    const { publicKey, privateKey } = generateKeypair();

    // Check format: 64-char hex strings (32-byte keys)
    expect(publicKey).toMatch(/^[0-9a-f]{64}$/);
    expect(privateKey).toMatch(/^[0-9a-f]{64}$/);

    // Keys should be different
    expect(publicKey).not.toBe(privateKey);
  });

  it("signs and verifies a message", async () => {
    const { publicKey, privateKey } = generateKeypair();
    const message = Buffer.from("test message");

    // Sign
    const signature = await signMessage(message, privateKey);
    expect(signature).toMatch(/^[0-9a-f]{128}$/); // 64-byte signature in hex

    // Verify correct signature
    const isValid = await verifySignature(message, signature, publicKey);
    expect(isValid).toBe(true);
  });

  it("rejects tampered messages", async () => {
    const { publicKey, privateKey } = generateKeypair();
    const message = Buffer.from("test message");

    // Sign
    const signature = await signMessage(message, privateKey);

    // Try to verify with different message
    const isValid = await verifySignature(
      Buffer.from("different message"),
      signature,
      publicKey
    );
    expect(isValid).toBe(false);
  });

  it("rejects tampered signatures", async () => {
    const { publicKey, privateKey } = generateKeypair();
    const message = Buffer.from("test message");

    // Sign
    let signature = await signMessage(message, privateKey);

    // Tamper with signature
    signature = signature.substring(0, 126) + "00";

    // Try to verify tampered signature
    const isValid = await verifySignature(message, signature, publicKey);
    expect(isValid).toBe(false);
  });

  it("produces canonical JSON with sorted keys", () => {
    const obj1 = { b: 2, a: 1, c: { z: 3, y: 2 } };
    const obj2 = { a: 1, c: { y: 2, z: 3 }, b: 2 };

    const json1 = canonicalJSON(obj1);
    const json2 = canonicalJSON(obj2);

    // Should produce identical JSON regardless of input key order
    expect(json1).toBe(json2);
    expect(json1).toContain('"a":1');
    expect(json1).toContain('"b":2');
  });
});
