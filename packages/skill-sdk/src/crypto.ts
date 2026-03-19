/**
 * Ed25519 cryptographic utilities for BookWithClaw skills.
 */

import * as ed25519 from "@noble/ed25519";
import { randomBytes } from "crypto";

/**
 * Generate an Ed25519 keypair.
 *
 * @returns {Object} Object with publicKey and privateKey (hex-encoded)
 */
export function generateKeypair(): {
  publicKey: string;
  privateKey: string;
} {
  // Generate 32-byte random private key
  const privateKeyBytes = randomBytes(32);
  const privateKey = privateKeyBytes.toString("hex");

  // Derive public key
  const publicKeyBytes = ed25519.getPublicKey(privateKeyBytes);
  const publicKey = Buffer.from(publicKeyBytes).toString("hex");

  return { publicKey, privateKey };
}

/**
 * Sign a message with an Ed25519 private key.
 *
 * @param message - Message bytes to sign
 * @param privateKey - Hex-encoded private key
 * @returns Hex-encoded signature
 */
export async function signMessage(
  message: Buffer | Uint8Array,
  privateKey: string
): Promise<string> {
  const privKeyBytes = Buffer.from(privateKey, "hex");
  const msgBytes = Buffer.isBuffer(message) ? message : Buffer.from(message);

  const sig = await ed25519.sign(msgBytes, privKeyBytes);
  return Buffer.from(sig).toString("hex");
}

/**
 * Verify an Ed25519 signature.
 *
 * @param message - Original message bytes
 * @param signature - Hex-encoded signature
 * @param publicKey - Hex-encoded public key
 * @returns True if signature is valid, false otherwise
 */
export async function verifySignature(
  message: Buffer | Uint8Array,
  signature: string,
  publicKey: string
): Promise<boolean> {
  try {
    const msgBytes = Buffer.isBuffer(message) ? message : Buffer.from(message);
    const sigBytes = Buffer.from(signature, "hex");
    const pubKeyBytes = Buffer.from(publicKey, "hex");

    return await ed25519.verify(sigBytes, msgBytes, pubKeyBytes);
  } catch {
    return false;
  }
}

/**
 * Serialize an object to canonical JSON (no spaces, sorted keys).
 *
 * @param obj - Object to serialize
 * @returns JSON string
 */
export function canonicalJSON(obj: Record<string, any>): string {
  return JSON.stringify(obj, Object.keys(obj).sort());
}
