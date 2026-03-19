import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';

export interface BuyerPreferences {
  location: string;           // e.g., "Manhattan", "Downtown San Francisco"
  checkInDate: string;        // YYYY-MM-DD
  checkOutDate: string;       // YYYY-MM-DD
  budgetCeiling: number;      // in cents (e.g., 50000 = $500)
  occupants: number;
  
  // Amenity preferences with priority weights (0-1)
  amenityWeights: {
    wifi?: number;            // High-speed internet (default: 0.8)
    breakfast?: number;       // Complimentary breakfast (default: 0.7)
    parking?: number;         // Free/paid parking (default: 0.5)
    gym?: number;             // Fitness center (default: 0.3)
    pool?: number;            // Swimming pool (default: 0.4)
    petFriendly?: number;     // Allows pets (default: 0.2)
    lateCheckout?: number;    // Late checkout available (default: 0.6)
    concierge?: number;       // Concierge service (default: 0.4)
    kitchenette?: number;     // In-room kitchen (default: 0.5)
    [key: string]: number | undefined;
  };
  
  // Room preferences
  roomTypePreference?: string[]; // e.g., ["deluxe", "suite"]
  minStars?: number;             // Minimum hotel rating (1-5)
}

export interface SellerOffer {
  price: number;
  location?: string;
  checkinDate?: string;
  checkoutDate?: string;
  roomType?: string;
  maxOccupants?: number;
  amenities?: { [key: string]: boolean };
  hotelStars?: number;
  sellerReputation?: number;  // 0-100
  stakeAmount?: number;
}

export interface EvaluationScore {
  priceScore: number;
  locationScore: number;
  dateScore: number;
  amenityScore: number;
  overallScore: number;
  details: string;
}

export class EnhancedBuyerSkill {
  private preferences: BuyerPreferences;
  private currentSessionId: string | null = null;
  private counterOfferCount: number = 0;
  private maxRounds: number = 5;

  constructor(prefs: BuyerPreferences) {
    // Set default amenity weights
    const defaults = {
      wifi: 0.8,
      breakfast: 0.7,
      parking: 0.5,
      gym: 0.3,
      pool: 0.4,
      petFriendly: 0.2,
      lateCheckout: 0.6,
      concierge: 0.4,
      kitchenette: 0.5,
    };

    this.preferences = {
      ...prefs,
      amenityWeights: {
        ...defaults,
        ...prefs.amenityWeights,
      },
    };
  }

  /**
   * Announce intent with full preferences
   */
  async announce(exchangeUrl: string, authToken: string, agentId: string): Promise<any> {
    console.log(`🛒 [Buyer] Announcing intent:`);
    console.log(`   📍 Location: ${this.preferences.location}`);
    console.log(`   📅 Dates: ${this.preferences.checkInDate} → ${this.preferences.checkOutDate}`);
    console.log(`   💰 Budget: $${(this.preferences.budgetCeiling / 100).toFixed(2)}`);
    console.log(`   👥 Occupants: ${this.preferences.occupants}`);
    console.log(`   ✨ Must-haves: ${this.getTopAmenities()}`);

    try {
      const response = await axios.post(
        `${exchangeUrl}/sessions`,
        {
          intent: {
            location: this.preferences.location,
            checkin_date: this.preferences.checkInDate,
            checkout_date: this.preferences.checkOutDate,
            budget_ceiling: this.preferences.budgetCeiling,
            occupants: this.preferences.occupants,
            preferred_amenities: this.preferences.amenityWeights,
            room_types: this.preferences.roomTypePreference || [],
            min_stars: this.preferences.minStars || 0,
          },
        },
        {
          headers: {
            Authorization: `Bearer ${authToken}`,
          },
        }
      );

      this.currentSessionId = response.data.session_id;
      console.log(`✅ [Buyer] Session created: ${this.currentSessionId}\n`);

      return {
        sessionId: this.currentSessionId,
        status: 'intent_announced',
      };
    } catch (error: any) {
      console.error(`❌ [Buyer] Failed:`, error.response?.data || error.message);
      throw error;
    }
  }

  /**
   * Get top amenities based on weights
   */
  private getTopAmenities(): string {
    return Object.entries(this.preferences.amenityWeights)
      .sort(([, a], [, b]) => (b || 0) - (a || 0))
      .slice(0, 3)
      .map(([amenity]) => amenity)
      .join(', ');
  }

  /**
   * Comprehensive offer evaluation
   */
  async evaluateOffer(offer: SellerOffer): Promise<{
    action: 'accept' | 'counter' | 'reject';
    price?: number;
    score?: EvaluationScore;
    reasoning: string;
  }> {
    console.log(`\n📊 [Buyer] Evaluating offer at $${(offer.price / 100).toFixed(2)}`);

    // Hard rejection: exceeds budget
    if (offer.price > this.preferences.budgetCeiling) {
      return {
        action: 'reject',
        reasoning: `❌ Price $${(offer.price / 100).toFixed(2)} exceeds budget ceiling $${(this.preferences.budgetCeiling / 100).toFixed(2)}`,
      };
    }

    // Hard rejection: location mismatch
    if (offer.location && !this.isLocationCompatible(offer.location)) {
      return {
        action: 'reject',
        reasoning: `❌ Location "${offer.location}" doesn't match requirement "${this.preferences.location}"`,
      };
    }

    // Hard rejection: date mismatch
    if (!this.areDatesCompatible(offer.checkinDate, offer.checkoutDate)) {
      return {
        action: 'reject',
        reasoning: `❌ Dates ${offer.checkinDate} → ${offer.checkoutDate} don't match requirement`,
      };
    }

    // Hard rejection: occupancy
    if (offer.maxOccupants && offer.maxOccupants < this.preferences.occupants) {
      return {
        action: 'reject',
        reasoning: `❌ Room only fits ${offer.maxOccupants} but need ${this.preferences.occupants} occupants`,
      };
    }

    // Calculate comprehensive score
    const score = this.scoreOffer(offer);
    console.log(`   Price: ${(score.priceScore * 100).toFixed(0)}%`);
    console.log(`   Location: ${(score.locationScore * 100).toFixed(0)}%`);
    console.log(`   Dates: ${(score.dateScore * 100).toFixed(0)}%`);
    console.log(`   Amenities: ${(score.amenityScore * 100).toFixed(0)}%`);
    console.log(`   Overall: ${(score.overallScore * 100).toFixed(0)}%`);

    // Accept excellent offers (>90%)
    if (score.overallScore >= 0.9) {
      return {
        action: 'accept',
        score,
        reasoning: `✅ Excellent match (${(score.overallScore * 100).toFixed(0)}%)! Accepting.`,
      };
    }

    // Counter good-but-not-great offers (70-90%)
    if (score.overallScore >= 0.7 && this.counterOfferCount < this.maxRounds) {
      const counterPrice = this.generateCounterOffer(offer);
      this.counterOfferCount++;
      return {
        action: 'counter',
        price: counterPrice,
        score,
        reasoning: `🤔 Good but pricey (${(score.overallScore * 100).toFixed(0)}%). Countering with $${(counterPrice / 100).toFixed(2)}`,
      };
    }

    // Counter moderate offers (50-70%)
    if (score.overallScore >= 0.5 && this.counterOfferCount < this.maxRounds) {
      const counterPrice = this.generateCounterOffer(offer);
      this.counterOfferCount++;
      return {
        action: 'counter',
        price: counterPrice,
        score,
        reasoning: `💭 Mediocre (${(score.overallScore * 100).toFixed(0)}%). Need better terms.`,
      };
    }

    // Reject poor offers
    return {
      action: 'reject',
      score,
      reasoning: `❌ Poor match (${(score.overallScore * 100).toFixed(0)}%). Too many compromises needed.`,
    };
  }

  /**
   * Score offer across multiple dimensions (0-1 scale)
   */
  private scoreOffer(offer: SellerOffer): EvaluationScore {
    // Price score: 1.0 when free, 0.0 when at ceiling
    const priceScore = 1.0 - (offer.price / this.preferences.budgetCeiling);

    // Location score: 1.0 if match, 0.5 if nearby, 0.0 if wrong
    const locationScore = this.scoreLocation(offer.location);

    // Date score: 1.0 if perfect, 0.8 if close, 0.0 if incompatible
    const dateScore = this.scoreDates(offer.checkinDate, offer.checkoutDate);

    // Amenity score: fraction of weighted amenities provided
    const amenityScore = this.scoreAmenities(offer.amenities);

    // Weighted overall score
    const overallScore =
      priceScore * 0.40 +      // Price is 40% of decision
      locationScore * 0.15 +   // Location is 15%
      dateScore * 0.15 +       // Dates are 15%
      amenityScore * 0.30;     // Amenities are 30%

    return {
      priceScore,
      locationScore,
      dateScore,
      amenityScore,
      overallScore,
      details: `Price ${(priceScore * 100).toFixed(0)}% + Location ${(locationScore * 100).toFixed(0)}% + Dates ${(dateScore * 100).toFixed(0)}% + Amenities ${(amenityScore * 100).toFixed(0)}%`,
    };
  }

  /**
   * Score location match
   */
  private scoreLocation(offerLocation?: string): number {
    if (!offerLocation) return 0.5; // Unknown location = neutral
    if (offerLocation.toLowerCase() === this.preferences.location.toLowerCase()) return 1.0;
    if (offerLocation.toLowerCase().includes(this.preferences.location.toLowerCase())) return 0.8;
    return 0.0; // Wrong location
  }

  /**
   * Score date compatibility
   */
  private scoreDates(checkinDate?: string, checkoutDate?: string): number {
    if (!checkinDate || !checkoutDate) return 0.5; // Unknown = neutral

    const offerCheckIn = new Date(checkinDate);
    const offerCheckOut = new Date(checkoutDate);
    const desiredCheckIn = new Date(this.preferences.checkInDate);
    const desiredCheckOut = new Date(this.preferences.checkOutDate);

    const checkInDiff = Math.abs(offerCheckIn.getTime() - desiredCheckIn.getTime()) / (1000 * 60 * 60 * 24);
    const checkOutDiff = Math.abs(offerCheckOut.getTime() - desiredCheckOut.getTime()) / (1000 * 60 * 60 * 24);

    if (checkInDiff === 0 && checkOutDiff === 0) return 1.0; // Perfect match
    if (checkInDiff <= 1 && checkOutDiff <= 1) return 0.8;   // Within 1 day
    if (checkInDiff <= 3 && checkOutDiff <= 3) return 0.5;   // Within 3 days
    return 0.0; // Too far off
  }

  /**
   * Score amenities provided vs preferred
   */
  private scoreAmenities(offerAmenities?: { [key: string]: boolean }): number {
    if (!offerAmenities || Object.keys(offerAmenities).length === 0) return 0.3; // No info = slight negative

    let totalScore = 0;
    let totalWeight = 0;

    for (const [amenity, weight] of Object.entries(this.preferences.amenityWeights)) {
      if (!weight) continue;
      totalWeight += weight;
      if (offerAmenities[amenity]) totalScore += weight;
    }

    return totalWeight > 0 ? totalScore / totalWeight : 0.5;
  }

  /**
   * Check location compatibility
   */
  private isLocationCompatible(offerLocation: string): boolean {
    return offerLocation.toLowerCase().includes(this.preferences.location.toLowerCase());
  }

  /**
   * Check date compatibility
   */
  private areDatesCompatible(checkinDate?: string, checkoutDate?: string): boolean {
    if (!checkinDate || !checkoutDate) return true; // Can't verify, so assume yes

    const offerCheckIn = new Date(checkinDate);
    const offerCheckOut = new Date(checkoutDate);
    const desiredCheckIn = new Date(this.preferences.checkInDate);
    const desiredCheckOut = new Date(this.preferences.checkOutDate);

    return offerCheckIn <= desiredCheckIn && offerCheckOut >= desiredCheckOut;
  }

  /**
   * Generate intelligent counter-offer
   */
  private generateCounterOffer(offer: SellerOffer): number {
    // Start with 10% reduction
    let counterPrice = Math.floor(offer.price * 0.9);

    // Adjust based on amenity gaps
    const amenityGap = this.scoreAmenities(offer.amenities);
    if (amenityGap < 0.5) {
      // Big amenity gap = bigger price reduction
      counterPrice = Math.floor(offer.price * 0.8);
    }

    // Don't go below 70% of budget ceiling
    const minPrice = Math.floor(this.preferences.budgetCeiling * 0.7);
    return Math.max(counterPrice, minPrice);
  }

  /**
   * Accept a deal
   */
  async acceptDeal(finalPrice: number, offer: SellerOffer): Promise<void> {
    console.log(`\n✅ [Buyer] DEAL ACCEPTED at $${(finalPrice / 100).toFixed(2)}`);
    if (offer.location) console.log(`   📍 Location: ${offer.location}`);
    if (offer.roomType) console.log(`   🏨 Room: ${offer.roomType}`);
    console.log(`   💰 Final Price: $${(finalPrice / 100).toFixed(2)}`);
  }

  getSessionId(): string | null {
    return this.currentSessionId;
  }
}

export default EnhancedBuyerSkill;
