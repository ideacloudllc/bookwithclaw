/**
 * Ed25519 cryptographic utilities for agent message signing and verification.
 */

import { ed25519 } from '@noble/ed25519';

/**
 * Generate an Ed25519 keypair.
 * 
 * @returns Object with { publicKey, privateKey } as hex strings
 */
export async function generateKeypair() {
  const privateKey = ed25519.utils.randomPrivateKey();
  const publicKey = await ed25519.getPublicKeyAsync(privateKey);
  
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
  const signature = await ed25519.signAsync(message, privateKeyBytes);
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
    const isValid = await ed25519.verifyAsync(signatureBytes, message, publicKeyBytes);
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
export async function getPublicKey(privateKey: string): Promise<string> {
  const privateKeyBytes = Buffer.from(privateKey, 'hex');
  const publicKey = await ed25519.getPublicKeyAsync(privateKeyBytes);
  return Buffer.from(publicKey).toString('hex');
}
