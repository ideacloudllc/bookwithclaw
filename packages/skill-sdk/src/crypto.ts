/**
 * Ed25519 cryptographic utilities for agent message signing and verification.
 */

import { getPublicKey, sign, verify, utils, etc } from '@noble/ed25519';
import { createHash } from 'crypto';

// Configure SHA-512 for @noble/ed25519
etc.sha512Sync = (message: Uint8Array) => {
  return new Uint8Array(createHash('sha512').update(message).digest());
};

/**
 * Generate an Ed25519 keypair (synchronous).
 * 
 * @returns Object with { publicKey, privateKey } as hex strings
 */
export function generateKeypair() {
  const privateKey = utils.randomPrivateKey();
  const publicKey = getPublicKey(privateKey);
  
  return {
    publicKey: Buffer.from(publicKey).toString('hex'),
    privateKey: Buffer.from(privateKey).toString('hex'),
  };
}

/**
 * Sign a message using an Ed25519 private key.
 * 
 * @param message - Message bytes to sign
 * @param privateKey - Private key as hex string
 * @returns Signature as hex string
 */
export async function signMessage(message: Buffer, privateKey: string): Promise<string> {
  const privateKeyBytes = Buffer.from(privateKey, 'hex');
  const signature = await sign(message, privateKeyBytes);
  return Buffer.from(signature).toString('hex');
}

/**
 * Verify an Ed25519 signature.
 * 
 * @param message - Message bytes that were signed
 * @param signature - Signature as hex string
 * @param publicKey - Public key as hex string
 * @returns True if signature is valid, false otherwise
 */
export async function verifySignature(
  message: Buffer,
  signature: string,
  publicKey: string
): Promise<boolean> {
  try {
    const signatureBytes = Buffer.from(signature, 'hex');
    const publicKeyBytes = Buffer.from(publicKey, 'hex');
    const isValid = await verify(signatureBytes, message, publicKeyBytes);
    return isValid;
  } catch {
    return false;
  }
}

/**
 * Extract public key from private key.
 * 
 * @param privateKey - Private key as hex string
 * @returns Public key as hex string
 */
export function getPublicKeyFromPrivate(privateKey: string): string {
  const privateKeyBytes = Buffer.from(privateKey, 'hex');
  const publicKey = getPublicKey(privateKeyBytes);
  return Buffer.from(publicKey).toString('hex');
}

/**
 * Produce canonical JSON with sorted keys (RFC 7159 compliant).
 * Used for message signing to ensure consistent serialization.
 * 
 * @param obj - Object to serialize
 * @returns Canonical JSON string with sorted keys
 */
export function canonicalJSON(obj: any): string {
  return JSON.stringify(sortKeys(obj));
}

/**
 * Recursively sort object keys for canonical JSON.
 */
function sortKeys(obj: any): any {
  if (Array.isArray(obj)) {
    return obj.map(sortKeys);
  } else if (obj !== null && typeof obj === 'object') {
    const sorted: any = {};
    const keys = Object.keys(obj).sort();
    for (const key of keys) {
      sorted[key] = sortKeys(obj[key]);
    }
    return sorted;
  } else {
    return obj;
  }
}
