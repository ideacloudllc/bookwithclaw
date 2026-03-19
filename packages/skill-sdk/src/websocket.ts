/**
 * WebSocket connection manager for connecting skills to the exchange.
 * 
 * Handles:
 * - Connection lifecycle
 * - Auto-reconnect with exponential backoff
 * - Message sending/receiving
 * - Event emission
 */

import { EventEmitter } from 'events';
import WebSocket from 'ws';
import { Message, parseMessage } from './messages';

export interface ExchangeConnectionOptions {
  exchangeUrl: string;
  sessionId: string;
  authToken: string;
  maxRetries?: number;
}

/**
 * ExchangeConnection manages WebSocket connection to the exchange.
 * 
 * Events:
 * - 'connected' - Connection established
 * - 'disconnected' - Connection lost
 * - 'message' - Message received
 * - 'error' - Error occurred
 */
export class ExchangeConnection extends EventEmitter {
  private ws: WebSocket | null = null;
  private url: string;
  private authToken: string;
  private isConnecting = false;
  private retryCount = 0;
  private maxRetries: number;
  private lastBackoffMs = 1000;

  constructor(options: ExchangeConnectionOptions) {
    super();
    
    this.url = `${options.exchangeUrl}/ws/session/${options.sessionId}`;
    this.authToken = options.authToken;
    this.maxRetries = options.maxRetries ?? 5;
  }

  /**
   * Connect to the exchange WebSocket.
   * 
   * @returns Promise that resolves when connected
   */
  public async connect(): Promise<void> {
    if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.OPEN)) {
      return;
    }

    this.isConnecting = true;

    try {
      return await new Promise((resolve, reject) => {
        // Use token in URL since browsers don't allow custom headers in WebSocket
        const urlWithAuth = `${this.url}?token=${encodeURIComponent(this.authToken)}`;
        
        this.ws = new WebSocket(urlWithAuth);

        this.ws.addEventListener('open', () => {
          this.isConnecting = false;
          this.retryCount = 0;
          this.lastBackoffMs = 1000;
          this.emit('connected');
          resolve();
        });

        this.ws.addEventListener('message', (event) => {
          const message = parseMessage(event.data);
          if (message) {
            this.emit('message', message);
          }
        });

        this.ws.addEventListener('close', () => {
          this.isConnecting = false;
          this.emit('disconnected');
          this.attemptReconnect();
        });

        this.ws.addEventListener('error', (event) => {
          this.emit('error', new Error(`WebSocket error: ${event}`));
          reject(new Error(`Failed to connect: ${event}`));
        });

        // Timeout after 10 seconds
        setTimeout(() => {
          if (this.isConnecting && this.ws?.readyState !== WebSocket.OPEN) {
            this.ws?.close();
            reject(new Error('Connection timeout'));
          }
        }, 10000);
      });
    } catch (error) {
      this.isConnecting = false;
      throw error;
    }
  }

  /**
   * Disconnect from the exchange.
   */
  public disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.isConnecting = false;
    this.retryCount = 0;
  }

  /**
   * Send a message to the exchange.
   * 
   * @param message - Message to send
   * @returns Promise that resolves when sent
   */
  public async send(message: Message): Promise<void> {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      throw new Error('WebSocket is not connected');
    }

    return new Promise((resolve, reject) => {
      try {
        const json = JSON.stringify(message);
        this.ws!.send(json, (error) => {
          if (error) {
            reject(error);
          } else {
            resolve();
          }
        });
      } catch (error) {
        reject(error);
      }
    });
  }

  /**
   * Check if connected.
   */
  public isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }

  /**
   * Attempt to reconnect with exponential backoff.
   */
  private attemptReconnect(): void {
    if (this.retryCount >= this.maxRetries) {
      this.emit('error', new Error(`Max retries (${this.maxRetries}) exceeded`));
      return;
    }

    this.retryCount++;
    const delayMs = Math.min(this.lastBackoffMs * 2, 30000); // Cap at 30 seconds
    this.lastBackoffMs = delayMs;

    setTimeout(() => {
      this.connect().catch((error) => {
        this.emit('error', error);
      });
    }, delayMs);
  }
}
