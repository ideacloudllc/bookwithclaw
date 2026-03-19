import EnhancedBuyerSkill, { BuyerPreferences } from './buyer-skill-enhanced';
import EnhancedSellerSkill from './seller-skill-enhanced';

async function runEnhancedNegotiation() {
  console.log('='.repeat(80));
  console.log('🚀 BookWithClaw Enhanced Skill Test: Multi-Attribute Hotel Negotiation');
  console.log('='.repeat(80));
  console.log();

  // === Step 1: Define Buyer Profile ===
  console.log('👤 Step 1: Buyer Profile\n');

  const buyerPrefs: BuyerPreferences = {
    location: 'Manhattan',
    checkInDate: '2026-04-01',
    checkOutDate: '2026-04-05',
    budgetCeiling: 60000,  // $600/night
    occupants: 2,
    minStars: 4,
    roomTypePreference: ['deluxe', 'suite'],
    amenityWeights: {
      wifi: 0.9,             // Must have!
      breakfast: 0.8,        // Very important
      lateCheckout: 0.7,    // Nice to have
      parking: 0.6,
      gym: 0.4,
      pool: 0.3,
      concierge: 0.5,
    },
  };

  console.log(`Name: Business traveler with family`);
  console.log(`Location: ${buyerPrefs.location}`);
  console.log(`Dates: ${buyerPrefs.checkInDate} → ${buyerPrefs.checkOutDate}`);
  console.log(`Budget: $${(buyerPrefs.budgetCeiling / 100).toFixed(2)}/night`);
  console.log(`Room Types: ${buyerPrefs.roomTypePreference?.join(', ')}`);
  console.log(`Min Rating: ${buyerPrefs.minStars} stars\n`);

  // === Step 2: Define Seller Property ===
  console.log('🏨 Step 2: Seller Property\n');

  const sellerProp = {
    location: 'Manhattan',
    checkinDate: '2026-04-01',
    checkoutDate: '2026-04-05',
    roomType: 'deluxe',
    floorPrice: 45000,      // $450 minimum
    askPrice: 60000,        // $600 asking
    maxOccupants: 2,
    hotelStars: 4,
    reputationScore: 92,
    stakeAmount: 10000,     // $100 stake
    amenities: {
      wifi: true,
      breakfast: true,
      parking: true,
      gym: true,
      pool: false,
      petFriendly: false,
      lateCheckout: true,
      concierge: true,
      kitchenette: false,
    },
  };

  console.log(`Name: Manhattan Luxury Hotel`);
  console.log(`Location: ${sellerProp.location}`);
  console.log(`Room: ${sellerProp.roomType}`);
  console.log(`Rating: ${sellerProp.hotelStars} stars`);
  console.log(`Asking: $${(sellerProp.askPrice / 100).toFixed(2)}/night`);
  console.log(`Floor: $${(sellerProp.floorPrice / 100).toFixed(2)}/night`);
  console.log(`Reputation: ${sellerProp.reputationScore}/100\n`);

  // === Step 3: Create Skill Instances ===
  console.log('🎯 Step 3: Creating skill instances...\n');

  const buyerSkill = new EnhancedBuyerSkill(buyerPrefs);
  const sellerSkill = new EnhancedSellerSkill(sellerProp);

  console.log('✅ Buyer skill created');
  console.log('✅ Seller skill created\n');

  // === Step 4: Publish Ask ===
  console.log('📊 Step 4: Seller publishing ask...\n');
  const askId = await sellerSkill.publishAsk();

  // === Step 5: Announce Intent ===
  console.log('🛍️  Step 5: Buyer announcing intent...\n');
  console.log(buyerSkill);

  // Simulate announcement without actual API call
  console.log('🛒 [Buyer] Announcing intent:');
  console.log(`   📍 Location: ${buyerPrefs.location}`);
  console.log(`   📅 Dates: ${buyerPrefs.checkInDate} → ${buyerPrefs.checkOutDate}`);
  console.log(`   💰 Budget: $${(buyerPrefs.budgetCeiling / 100).toFixed(2)}`);
  console.log(`   👥 Occupants: ${buyerPrefs.occupants}`);
  console.log(`   ✨ Must-haves: wifi, breakfast, lateCheckout`);
  console.log(`✅ [Buyer] Session created: demo-session-enhanced-001\n`);

  // === Step 6: Negotiate ===
  console.log('🤝 Step 6: Multi-Round Negotiation\n');

  const sessionId = 'demo-session-enhanced-001';

  // Buyer intent for seller to evaluate
  const buyerIntent = {
    location: 'Manhattan',
    checkinDate: buyerPrefs.checkInDate,
    checkoutDate: buyerPrefs.checkOutDate,
    budgetCeiling: buyerPrefs.budgetCeiling,
    occupants: buyerPrefs.occupants,
    preferredAmenities: buyerPrefs.amenityWeights,
    roomTypes: buyerPrefs.roomTypePreference || [],
  };

  let round = 0;
  let dealDone = false;
  let currentPrice = sellerProp.askPrice;

  while (round < 5 && !dealDone) {
    console.log(`\n${'='.repeat(80)}`);
    console.log(`ROUND ${round + 1}`);
    console.log(`${'='.repeat(80)}\n`);

    // Seller publishes ask
    console.log(`💰 [Seller] Current ask: $${(currentPrice / 100).toFixed(2)}/night\n`);

    // Buyer evaluates
    console.log(`[Buyer] Evaluating seller's offer...\n`);

    const buyerEval = await buyerSkill.evaluateOffer({
      price: currentPrice,
      location: sellerProp.location,
      checkinDate: sellerProp.checkinDate,
      checkoutDate: sellerProp.checkoutDate,
      roomType: sellerProp.roomType,
      maxOccupants: sellerProp.maxOccupants,
      amenities: sellerProp.amenities,
      hotelStars: sellerProp.hotelStars,
      sellerReputation: sellerProp.reputationScore,
    });

    console.log(`\n→ ${buyerEval.reasoning}`);

    if (buyerEval.action === 'accept') {
      console.log(`\n✅ BUYER ACCEPTS at $${(currentPrice / 100).toFixed(2)}`);
      await buyerSkill.acceptDeal(currentPrice, {
        price: currentPrice,
        location: sellerProp.location,
        roomType: sellerProp.roomType,
      });
      dealDone = true;
      break;
    }

    if (buyerEval.action === 'counter' && buyerEval.price) {
      console.log(`\n[Buyer] Counter-offer: $${(buyerEval.price / 100).toFixed(2)}`);

      // Seller evaluates buyer counter
      console.log(`\n[Seller] Evaluating buyer counter...\n`);

      const sellerEval = await sellerSkill.evaluateOffer(
        {
          ...buyerIntent,
          budgetCeiling: buyerEval.price, // Approximate buyer's offer
        },
        sessionId
      );

      console.log(`\n→ ${sellerEval.reasoning}`);

      if (sellerEval.amenityBoost) {
        console.log(`   ${sellerEval.amenityBoost}`);
      }

      if (sellerEval.action === 'accept') {
        console.log(`\n✅ SELLER ACCEPTS at $${(buyerEval.price / 100).toFixed(2)}`);
        await sellerSkill.acceptDeal(sessionId, buyerEval.price);
        dealDone = true;
        break;
      }

      if (sellerEval.action === 'counter' && sellerEval.price) {
        currentPrice = sellerEval.price;
        console.log(`\n[Seller] Counter-offer: $${(currentPrice / 100).toFixed(2)}`);
      } else {
        console.log(`\n❌ ${sellerEval.reasoning}`);
        dealDone = true;
        break;
      }
    } else {
      console.log(`\n❌ Buyer rejects: ${buyerEval.reasoning}`);
      dealDone = true;
      break;
    }

    round++;
  }

  console.log('\n' + '='.repeat(80));
  console.log('✅ NEGOTIATION COMPLETE');
  console.log('='.repeat(80));

  if (dealDone) {
    const finalPrice = currentPrice;
    console.log(`\n📈 FINAL SUMMARY:`);
    console.log(`   Seller asked: $${(sellerProp.askPrice / 100).toFixed(2)}`);
    console.log(`   Final price: $${(finalPrice / 100).toFixed(2)}`);
    console.log(`   Difference: -$${((sellerProp.askPrice - finalPrice) / 100).toFixed(2)}`);
    console.log(`   Rounds: ${round + 1}`);
    console.log(`   Status: ✅ DEAL CLOSED\n`);
  }
}

// Run the enhanced negotiation
runEnhancedNegotiation().catch(console.error);
