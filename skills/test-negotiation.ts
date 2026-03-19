import BuyerSkill from './buyer-skill';
import SellerSkill from './seller-skill';

async function runNegotiation() {
  console.log('='.repeat(70));
  console.log('🚀 BookWithClaw Skill Test: Hotel Negotiation');
  console.log('='.repeat(70));
  console.log();

  // === Step 1: Register Agents ===
  console.log('📋 Step 1: Using test agents...\n');

  const buyerAgentId = 'buyer-test-001';
  const buyerToken = 'test-buyer-token';
  const sellerAgentId = 'seller-test-001';
  const sellerToken = 'test-seller-token';

  // === Step 2: Create Skills ===
  console.log('🎯 Step 2: Instantiating buyer and seller skills...\n');

  const buyerSkill = new BuyerSkill({
    exchangeUrl: 'http://159.65.36.5:8890',
    agentId: buyerAgentId,
    authToken: buyerToken,
    checkInDate: '2026-04-01',
    checkOutDate: '2026-04-05',
    budgetCeiling: 50000, // $500
    occupants: 2,
    preferredTerms: { wifi: true, breakfast: true },
  });

  const sellerSkill = new SellerSkill({
    exchangeUrl: 'http://159.65.36.5:8890',
    agentId: sellerAgentId,
    authToken: sellerToken,
    checkInDate: '2026-04-01',
    checkOutDate: '2026-04-05',
    roomType: 'deluxe',
    floorPrice: 35000,  // $350 minimum
    askPrice: 50000,    // $500 asking price
    maxOccupants: 4,
    amenities: { wifi: true, breakfast: true, balcony: true },
    reputationScore: 95,
    stakeAmount: 10000, // $100 stake
  });

  console.log('✅ Buyer skill created');
  console.log('✅ Seller skill created\n');

  // === Step 3: Seller Publishes Ask ===
  console.log('📊 Step 3: Seller publishing ask...\n');
  const askId = await sellerSkill.publishAsk();
  console.log();

  // === Step 4: Buyer Announces Intent ===
  // Note: This would normally connect to the real exchange
  // For demo purposes, we're simulating the flow
  console.log('🛍️  Step 4: Buyer announcing intent...\n');
  console.log('🛒 [Buyer] Announcing intent for 2026-04-01 to 2026-04-05');
  console.log('✅ [Buyer] Session created: demo-session-12345\n');

  // === Step 5: Negotiate ===
  console.log('🤝 Step 5: Negotiation simulation...\n');

  // Simulate offers
  let sellerAskPrice = 50000;
  let buyerOfferPrice = 40000;
  let round = 0;
  let dealMade = false;

  while (round < 5 && !dealMade) {
    console.log(`\n--- Round ${round + 1} ---`);

    // Buyer evaluates seller's ask
    const buyerEval = await buyerSkill.evaluateOffer({ price: sellerAskPrice });
    console.log(`📊 [Buyer] Evaluating seller ask: $${(sellerAskPrice / 100).toFixed(2)}`);
    console.log(`Buyer decision: ${buyerEval.action.toUpperCase()} - ${buyerEval.reasoning}`);

    if (buyerEval.action === 'accept') {
      console.log(`\n✅ DEAL ACCEPTED by buyer at $${(sellerAskPrice / 100).toFixed(2)}`);
      await buyerSkill.acceptDeal(sellerAskPrice);
      dealMade = true;
      break;
    }

    if (buyerEval.action === 'counter' && buyerEval.price) {
      buyerOfferPrice = buyerEval.price;

      // Seller evaluates buyer's counter
      const sellerEval = await sellerSkill.evaluateOffer(
        { price: buyerOfferPrice },
        'demo-session-12345'
      );
      console.log(`💰 [Seller] Evaluating buyer offer: $${(buyerOfferPrice / 100).toFixed(2)}`);
      console.log(`Seller decision: ${sellerEval.action.toUpperCase()} - ${sellerEval.reasoning}`);

      if (sellerEval.action === 'accept') {
        console.log(`\n✅ DEAL ACCEPTED by seller at $${(buyerOfferPrice / 100).toFixed(2)}`);
        await sellerSkill.acceptDeal('demo-session-12345', buyerOfferPrice);
        dealMade = true;
        break;
      }

      if (sellerEval.action === 'counter' && sellerEval.price) {
        sellerAskPrice = sellerEval.price;
      } else {
        console.log(`\n❌ NEGOTIATION FAILED: ${sellerEval.reasoning}`);
        dealMade = true;
        break;
      }
    } else {
      console.log(`\n❌ NEGOTIATION FAILED: ${buyerEval.reasoning}`);
      dealMade = true;
      break;
    }

    round++;
  }

  if (!dealMade) {
    console.log('\n❌ NEGOTIATION FAILED: Max rounds exceeded');
  }

  console.log('\n' + '='.repeat(70));
  console.log('✅ Test complete!');
  console.log('='.repeat(70));
  console.log('\n📝 Summary:');
  console.log(`   - Rounds: ${round + 1}`);
  console.log(`   - Final Price: $${dealMade ? (buyerOfferPrice / 100).toFixed(2) : 'N/A'}`);
  console.log(`   - Deal Status: ${dealMade ? '✅ COMPLETED' : '❌ FAILED'}\n`);
}

// Run the test
runNegotiation().catch(console.error);
