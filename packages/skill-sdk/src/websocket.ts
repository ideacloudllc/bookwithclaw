/**
 * WebSocket connection manager for BookWithClaw Exchange.
 */

import { EventEmitter } from "events";
import { WebSocket } from "ws";

import { Message, MessageSchema, parseMessage } from "./messages";

export interface ExchangeConnectionOptions {
  exchangeUrl: string;
  sessionId: string;
  authToken: string;
  reconnectMaxRetries?: number;
  reconnectDelay?: number;
}

/**
 * Manages WebSocket connection to BookWithClaw Exchange.
 */
export class ExchangeConnection extends EventEmitter {
  private ws: WebSocket | null = null;
  private options: ExchangeConnectionOptions & {
    reconnectMaxRetries: number;
    reconnectDelay: number;
  };
  private reconnectAttempts = 0;
  private messageQueue: Message[] = [];

  constructor(options: ExchangeConnectionOptions) {
    super();
    this.options = {
      ...options,
      reconnectMaxRetries: options.reconnectMaxRetries || 5,
      reconnectDelay: options.reconnectDelay || 1000,
    };
  }

  /**
   * Connect to the exchange
   */
  async connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      const url = this.buildWebSocketUrl();

      try {
        this.ws = new WebSocket(url);

        this.ws.onopen = () => {
          console.log(`Connected to exchange: ${url}`);
          this.reconnectAttempts = 0;
          this.emit("connected");
          this.flushMessageQueue();
          resolve();
        };

        this.ws.onmessage = (event) => {
          this.handleMessage(event.data);
        };

        this.ws.onerror = (error) => {
          console.error("WebSocket error:", error);
          this.emit("error", error);
          reject(error);
        };

        this.ws.onclose = () => {
          console.log("Disconnected from exchange");
          this.emit("disconnected");
          this.attemptReconnect();
        };
      } catch (error) {
        reject(error);
      }
    });
  }

  /**
   * Send a message to the exchange
   */
  async sendMessage(message: Message): Promise<void> {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      // Queue message if not connected
      this.messageQueue.push(message);
      if (!this.ws) {
        await this.connect();
      }
      return;
    }

    const json = JSON.stringify(message);
    this.ws.send(json);
    this.emit("sent", message);
  }

  /**
   * Close the connection
   */
  close(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  /**
   * Check if connected
   */
  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }

  // Private helpers

  private buildWebSocketUrl(): string {
    const baseUrl = this.options.exchangeUrl.replace(/\/$/, "");
    const sessionId = this.options.sessionId;
    const token = this.options.authToken;

    return `${baseUrl}/ws/session/${sessionId}?token=${encodeURIComponent(token)}`;
  }

  private handleMessage(data: string): void {
    try {
      const parsed = JSON.parse(data);
      const message = parseMessage(parsed);
      this.emit("message", message);
    } catch (error) {
      console.error("Failed to parse message:", error, "data:", data);
      this.emit("error", error);
    }
  }

  private flushMessageQueue(): void {
    while (this.messageQueue.length > 0 && this.isConnected()) {
      const message = this.messageQueue.shift()!;
      const json = JSON.stringify(message);
      if (this.ws) {
        this.ws.send(json);
        this.emit("sent", message);
      }
    }
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts >= this.options.reconnectMaxRetries) {
      console.error("Max reconnect attempts reached");
      this.emit("reconnect_failed");
      return;
    }

    this.reconnectAttempts++;
    const delay =
      this.options.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

    console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.options.reconnectMaxRetries}) in ${delay}ms...`);

    setTimeout(() => {
      this.connect().catch((error) => {
        console.error("Reconnect failed:", error);
      });
    }, delay);
  }
}
