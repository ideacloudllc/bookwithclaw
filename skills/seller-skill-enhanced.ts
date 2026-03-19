import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';

interface SellerProperty {
  location: string;           // e.g., "Manhattan", "Downtown San Francisco"
  checkinDate: string;        // YYYY-MM-DD (earliest available)
  checkoutDate: string;       // YYYY-MM-DD (latest available)
  roomType: string;           // e.g., "deluxe", "suite", "standard"
  floorPrice: number;         // Minimum acceptable price in cents
  askPrice: number;           // Initial asking price in cents
  maxOccupants: number;
  hotelStars: number;         // 1-5 star rating
  reputationScore: number;    // 0-100
  stakeAmount: number;        // in cents
  
  // Available amenities
  amenities: {
    wifi?: boolean;
    breakfast?: boolean;
    parking?: boolean;
    gym?: boolean;
    pool?: boolean;
    petFriendly?: boolean;
    lateCheckout?: boolean;    // Can provide late checkout (default: 0-2 hours)
    concierge?: boolean;
    kitchenette?: boolean;
    [key: string]: boolean | undefined;
  };
}

export interface BuyerIntent {
  location: string;
  checkinDate: string;
  checkoutDate: string;
  budgetCeiling: number;
  occupants: number;
  preferredAmenities?: { [key: string]: number | undefined };
  roomTypes?: string[];
}

interface CounterOfferStrategy {
  price: number;
  lateCheckoutHours?: number;  // Offer additional late checkout hours
  breakfastIncluded?: boolean; // Add breakfast to sweeten deal
  reasoning: string;
}

export class EnhancedSellerSkill {
  private property: SellerProperty;
  private activeAsks: Map<string, any> = new Map();
  private activeSessions: Map<string, BuyerIntent> = new Map();
  private counterOfferCount: Map<string, number> = new Map();
  private maxRounds: number = 5;

  constructor(prop: SellerProperty) {
    this.property = prop;
  }

  /**
   * Publish an ask with full property details
   */
  async publishAsk(): Promise<string> {
    console.log(`🏨 [Seller] Publishing hotel offer:`);
    console.log(`   📍 Location: ${this.property.location}`);
    console.log(`   🏨 Room Type: ${this.property.roomType}`);
    console.log(`   ⭐ Rating: ${this.property.hotelStars}/5`);
    console.log(`   💰 Asking Price: $${(this.property.askPrice / 100).toFixed(2)}`);
    console.log(`   💰 Floor Price: $${(this.property.floorPrice / 100).toFixed(2)}`);
    console.log(`   ✨ Amenities: ${this.getAmenityList()}\n`);

    const askId = uuidv4();

    const ask = {
      ask_id: askId,
      location: this.property.location,
      room_type: this.property.roomType,
      checkin_date: this.property.checkinDate,
      checkout_date: this.property.checkoutDate,
      price: this.property.askPrice,
      floor_price: this.property.floorPrice,
      max_occupants: this.property.maxOccupants,
      hotel_stars: this.property.hotelStars,
      amenities: this.property.amenities,
      seller_reputation_score: this.property.reputationScore,
      stake_amount: this.property.stakeAmount,
    };

    this.activeAsks.set(askId, ask);
    console.log(`✅ [Seller] Ask published: ${askId}`);

    return askId;
  }

  /**
   * Get amenity list as string
   */
  private getAmenityList(): string {
    return Object.entries(this.property.amenities)
      .filter(([, available]) => available)
      .map(([name]) => this.formatAmenity(name))
      .join(', ') || 'Basic';
  }

  /**
   * Format amenity name
   */
  private formatAmenity(name: string): string {
    return name
      .replace(/([A-Z])/g, ' $1')
      .replace(/^./, (str) => str.toUpperCase())
      .trim();
  }

  /**
   * Evaluate buyer offer considering multiple factors
   */
  async evaluateOffer(buyerIntent: BuyerIntent, sessionId: string): Promise<{
    action: 'accept' | 'counter' | 'reject';
    price?: number;
    amenityBoost?: string;
    reasoning: string;
  }> {
    console.log(`\n💰 [Seller] Evaluating buyer intent:`);
    console.log(`   📍 Needs: ${buyerIntent.location}`);
    console.log(`   💰 Budget: $${(buyerIntent.budgetCeiling / 100).toFixed(2)}`);
    console.log(`   👥 Occupants: ${buyerIntent.occupants}\n`);

    // Store intent for counter-offer strategy
    this.activeSessions.set(sessionId, buyerIntent);

    // Hard rejection: location mismatch
    if (!this.isLocationMatch(buyerIntent.location)) {
      return {
        action: 'reject',
        reasoning: `❌ Location mismatch: need "${buyerIntent.location}", we're in "${this.property.location}"`,
      };
    }

    // Hard rejection: occupancy
    if (buyerIntent.occupants > this.property.maxOccupants) {
      return {
        action: 'reject',
        reasoning: `❌ Room only fits ${this.property.maxOccupants}, buyer needs ${buyerIntent.occupants}`,
      };
    }

    // Hard rejection: room type
    if (buyerIntent.roomTypes && buyerIntent.roomTypes.length > 0) {
      if (!buyerIntent.roomTypes.includes(this.property.roomType)) {
        return {
          action: 'reject',
          reasoning: `❌ Room type mismatch: we have ${this.property.roomType}, they want ${buyerIntent.roomTypes.join('/')}`,
        };
      }
    }

    const offerPrice = this.getOfferedPrice(buyerIntent);
    const amenityMatch = this.scoreAmenityAlignment(buyerIntent.preferredAmenities);

    console.log(`   Offered Price: $${(offerPrice / 100).toFixed(2)}`);
    console.log(`   Amenity Match: ${(amenityMatch * 100).toFixed(0)}%`);

    // Accept excellent offers (budget-friendly + good match)
    if (offerPrice >= this.property.askPrice * 0.9 && amenityMatch >= 0.8) {
      return {
        action: 'accept',
        reasoning: `✅ Great match! Price $${(offerPrice / 100).toFixed(2)} + strong amenity alignment (${(amenityMatch * 100).toFixed(0)}%)`,
      };
    }

    // Accept fair offers at floor price
    if (offerPrice >= this.property.floorPrice && amenityMatch >= 0.7) {
      return {
        action: 'accept',
        reasoning: `✅ Fair price at $${(offerPrice / 100).toFixed(2)} with good amenity match`,
      };
    }

    // Counter offers below asking but above floor
    const rounds = this.counterOfferCount.get(sessionId) || 0;
    if (offerPrice >= this.property.floorPrice * 0.8 && rounds < this.maxRounds) {
      const strategy = this.generateCounterStrategy(offerPrice, buyerIntent);
      this.counterOfferCount.set(sessionId, rounds + 1);

      return {
        action: 'counter',
        price: strategy.price,
        amenityBoost: strategy.lateCheckoutHours
          ? `+ Late checkout (${strategy.lateCheckoutHours} hours)`
          : strategy.breakfastIncluded
          ? '+ Free breakfast'
          : undefined,
        reasoning: strategy.reasoning,
      };
    }

    // Reject too-low offers
    return {
      action: 'reject',
      reasoning: `❌ Offer $${(offerPrice / 100).toFixed(2)} is too low (floor: $${(this.property.floorPrice / 100).toFixed(2)})`,
    };
  }

  /**
   * Get the offered price from buyer intent (derived)
   */
  private getOfferedPrice(intent: BuyerIntent): number {
    // Approximate: assume buyer offers 90% of their ceiling initially
    return Math.floor(intent.budgetCeiling * 0.85);
  }

  /**
   * Score how well our amenities match buyer's preferences
   */
  private scoreAmenityAlignment(buyerPrefs?: { [key: string]: number | undefined }): number {
    if (!buyerPrefs || Object.keys(buyerPrefs).length === 0) return 0.5;

    let totalScore = 0;
    let totalWeight = 0;

    for (const [amenity, weight] of Object.entries(buyerPrefs)) {
      if (!weight) continue;
      totalWeight += weight;
      if (this.property.amenities[amenity]) {
        totalScore += weight;
      }
    }

    return totalWeight > 0 ? totalScore / totalWeight : 0.5;
  }

  /**
   * Check location compatibility
   */
  private isLocationMatch(buyerLocation: string): boolean {
    const normalize = (s: string) => s.toLowerCase().replace(/\s+/g, '');
    return normalize(this.property.location).includes(normalize(buyerLocation));
  }

  /**
   * Generate intelligent counter-offer with sweeteners
   */
  private generateCounterStrategy(buyerPrice: number, intent: BuyerIntent): CounterOfferStrategy {
    // Calculate split-the-difference as base
    let counterPrice = Math.floor((buyerPrice + this.property.askPrice) / 2);

    // If buyer has high amenity expectations, offer sweeteners instead of price reduction
    const amenityMatch = this.scoreAmenityAlignment(intent.preferredAmenities);

    let reasoning = '';
    let lateCheckoutHours = 0;
    let breakfastIncluded = false;

    if (amenityMatch < 0.5 && this.property.amenities.lateCheckout) {
      // Offer late checkout to compensate for missing amenities
      lateCheckoutHours = 2;
      counterPrice = Math.floor(this.property.askPrice * 0.95); // Slight reduction
      reasoning = `🤝 Countering at $${(counterPrice / 100).toFixed(2)} + 2-hour late checkout`;
    } else if (amenityMatch < 0.6 && this.property.amenities.breakfast) {
      // Offer free breakfast
      breakfastIncluded = true;
      counterPrice = Math.floor(this.property.askPrice * 0.92);
      reasoning = `🤝 Countering at $${(counterPrice / 100).toFixed(2)} + complimentary breakfast`;
    } else {
      // Standard price negotiation
      reasoning = `🤝 Countering at $${(counterPrice / 100).toFixed(2)}`;
    }

    // Never go below floor price
    counterPrice = Math.max(counterPrice, this.property.floorPrice);

    return {
      price: counterPrice,
      lateCheckoutHours,
      breakfastIncluded,
      reasoning,
    };
  }

  /**
   * Accept a deal
   */
  async acceptDeal(sessionId: string, finalPrice: number): Promise<void> {
    const intent = this.activeSessions.get(sessionId);
    console.log(`\n✅ [Seller] DEAL ACCEPTED at $${(finalPrice / 100).toFixed(2)}`);
    if (intent) {
      console.log(`   👤 Buyer: ${intent.location}, ${intent.occupants} occupant(s)`);
    }
    console.log(`   🎉 Booking complete!`);
  }

  /**
   * Get summary of what we're offering
   */
  getSummary(): string {
    return `${this.property.roomType} in ${this.property.location} - $${(this.property.askPrice / 100).toFixed(2)}/night`;
  }

  getActiveAsks(): string[] {
    return Array.from(this.activeAsks.keys());
  }
}

export default EnhancedSellerSkill;
