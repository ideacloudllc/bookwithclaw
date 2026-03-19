"""
Landing page routes for seller recruitment.
Serves static HTML pages for marketing.
"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["landing"])


# Read the seller landing page HTML
SELLER_LANDING_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BookWithClaw for Hotels – Direct Bookings Made Smart</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #222;
        }

        header {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: white;
            padding: 80px 20px;
            text-align: center;
        }

        header h1 {
            font-size: 3rem;
            margin-bottom: 20px;
            font-weight: 700;
        }

        header p {
            font-size: 1.3rem;
            margin-bottom: 30px;
            opacity: 0.95;
        }

        .cta-button {
            display: inline-block;
            background: #ff6b35;
            color: white;
            padding: 14px 40px;
            border-radius: 6px;
            text-decoration: none;
            font-weight: 600;
            font-size: 1.1rem;
            transition: background 0.3s;
            border: none;
            cursor: pointer;
        }

        .cta-button:hover {
            background: #e55a2b;
        }

        section {
            padding: 60px 20px;
            max-width: 1200px;
            margin: 0 auto;
        }

        h2 {
            font-size: 2.2rem;
            margin-bottom: 40px;
            text-align: center;
        }

        .comparison {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 40px;
            margin-bottom: 60px;
        }

        .comparison-card {
            padding: 30px;
            border-radius: 8px;
            background: #f5f5f5;
        }

        .comparison-card h3 {
            font-size: 1.3rem;
            margin-bottom: 20px;
        }

        .comparison-card ul {
            list-style: none;
        }

        .comparison-card li {
            margin-bottom: 12px;
            font-size: 0.95rem;
        }

        .comparison-card.bad {
            border-left: 4px solid #d32f2f;
        }

        .comparison-card.bad li:before {
            content: "✗ ";
            color: #d32f2f;
            font-weight: bold;
            margin-right: 8px;
        }

        .comparison-card.good {
            border-left: 4px solid #388e3c;
            background: #e8f5e9;
        }

        .comparison-card.good li:before {
            content: "✓ ";
            color: #388e3c;
            font-weight: bold;
            margin-right: 8px;
        }

        .numbers {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 40px;
            margin-bottom: 60px;
        }

        .number-card {
            text-align: center;
            padding: 30px;
        }

        .number-card .big-number {
            font-size: 3.5rem;
            font-weight: 700;
            color: #ff6b35;
            margin-bottom: 10px;
        }

        .number-card p {
            font-size: 1.1rem;
            color: #666;
        }

        .steps {
            background: #f9f9f9;
            padding: 50px 30px;
            border-radius: 8px;
        }

        .steps-grid {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr 1fr;
            gap: 30px;
        }

        .step {
            text-align: center;
        }

        .step-number {
            width: 50px;
            height: 50px;
            background: #ff6b35;
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 1.3rem;
            margin: 0 auto 15px;
        }

        .step h4 {
            margin-bottom: 10px;
        }

        .step p {
            font-size: 0.9rem;
            color: #666;
        }

        .faq {
            background: white;
        }

        .faq-item {
            margin-bottom: 30px;
            padding: 20px;
            background: #f5f5f5;
            border-radius: 6px;
            cursor: pointer;
            transition: background 0.3s;
        }

        .faq-item:hover {
            background: #efefef;
        }

        .faq-item h4 {
            font-size: 1.1rem;
            margin-bottom: 10px;
            color: #1a1a2e;
        }

        .faq-item.open p {
            display: block;
        }

        .faq-item p {
            display: none;
            color: #666;
            font-size: 0.95rem;
            line-height: 1.6;
        }

        footer {
            background: #1a1a2e;
            color: white;
            text-align: center;
            padding: 40px 20px;
            margin-top: 60px;
        }

        @media (max-width: 768px) {
            header h1 {
                font-size: 2rem;
            }

            header p {
                font-size: 1.1rem;
            }

            .comparison {
                grid-template-columns: 1fr;
            }

            .numbers {
                grid-template-columns: 1fr;
            }

            .steps-grid {
                grid-template-columns: 1fr 1fr;
            }
        }

        .highlight {
            background: #fff3cd;
            padding: 20px;
            border-radius: 6px;
            border-left: 4px solid #ffc107;
            margin: 30px 0;
        }

        .highlight strong {
            color: #856404;
        }

        .pricing-box {
            background: #e8f5e9;
            padding: 30px;
            border-radius: 8px;
            text-align: center;
            margin: 40px 0;
        }

        .pricing-box .price {
            font-size: 2.5rem;
            font-weight: 700;
            color: #388e3c;
            margin: 20px 0;
        }

        .pricing-box .comparison-text {
            font-size: 1.1rem;
            color: #666;
            margin-bottom: 15px;
        }

        .comparison-text strong {
            color: #d32f2f;
        }

        .email-form {
            max-width: 500px;
            margin: 40px auto;
        }

        .email-form input {
            width: 100%;
            padding: 14px;
            margin-bottom: 10px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 1rem;
        }

        .email-form button {
            width: 100%;
            background: #ff6b35;
            color: white;
            padding: 14px;
            border-radius: 6px;
            border: none;
            font-weight: 600;
            font-size: 1rem;
            cursor: pointer;
            transition: background 0.3s;
        }

        .email-form button:hover {
            background: #e55a2b;
        }
    </style>
</head>
<body>
    <header>
        <h1>🚀 BookWithClaw for Hotels</h1>
        <p>Direct bookings that work. AI negotiation. 1.8% instead of 12%.</p>
        <button class="cta-button" onclick="document.getElementById('signup').scrollIntoView({behavior: 'smooth'})">Start Free Trial</button>
    </header>

    <section id="problem">
        <h2>Stop Leaving Money on the Table</h2>
        
        <div class="comparison">
            <div class="comparison-card bad">
                <h3>Today: OTA-Dependent</h3>
                <ul>
                    <li>12-15% commission per booking</li>
                    <li>$50K+/year in OTA fees for 100 bookings</li>
                    <li>Zero control over pricing algorithm</li>
                    <li>Customer data locked behind platform</li>
                    <li>Complex negotiations with groups</li>
                    <li>Rate parity requirements</li>
                </ul>
            </div>

            <div class="comparison-card good">
                <h3>With BookWithClaw</h3>
                <ul>
                    <li>1.8% platform fee (87% cheaper)</li>
                    <li>~$8K/year for same 100 bookings</li>
                    <li>Full rate control. You decide prices.</li>
                    <li>Direct customer relationships</li>
                    <li>AI agents negotiate on your behalf</li>
                    <li>No restrictions. No intermediaries.</li>
                </ul>
            </div>
        </div>

        <div class="highlight">
            <strong>💰 Real example:</strong> 100 bookings/month at $450 average<br>
            OTA cost: $54,000/year | BookWithClaw cost: $8,100/year | <strong>Your savings: $45,900/year</strong>
        </div>
    </section>

    <section id="how-it-works">
        <h2>How It Works</h2>

        <div class="steps">
            <div class="steps-grid">
                <div class="step">
                    <div class="step-number">1</div>
                    <h4>Create Room Listing</h4>
                    <p>Add your rooms, rates, and availability.</p>
                </div>
                <div class="step">
                    <div class="step-number">2</div>
                    <h4>Set Your Terms</h4>
                    <p>Define floor prices and preferred booking terms.</p>
                </div>
                <div class="step">
                    <div class="step-number">3</div>
                    <h4>AI Does Negotiating</h4>
                    <p>Our agents negotiate directly with buyers. You stay in control.</p>
                </div>
                <div class="step">
                    <div class="step-number">4</div>
                    <h4>Get Paid Instantly</h4>
                    <p>Stripe handles settlement within 2 business days.</p>
                </div>
            </div>
        </div>

        <p style="text-align: center; margin-top: 30px; font-size: 1.1rem; color: #666;">
            <strong>You control everything.</strong> AI agents just handle the back-and-forth.<br>
            No complex integrations. No API required. Simple hotel-to-agent negotiation.
        </p>
    </section>

    <section id="pricing">
        <h2>Pricing That Makes Sense</h2>

        <div class="pricing-box">
            <div class="comparison-text">
                Booking value: <strong>$450</strong>
            </div>
            <div class="price">1.8%</div>
            <div class="comparison-text">
                Your fee: <strong>$8.10</strong>
            </div>
            <div class="comparison-text">
                vs. Booking.com's <strong style="color: #d32f2f;">12%</strong> ($54)
            </div>
            <p style="margin-top: 20px; color: #666;">
                Pay only on confirmed bookings.<br>
                No monthly fees. No setup charges.
            </p>
        </div>

        <div style="text-align: center; color: #666;">
            <p>Limited-time offer: First 30 days at <strong style="color: #388e3c;">0.9%</strong> (50% off)</p>
        </div>
    </section>

    <section id="numbers">
        <h2>What Sellers Are Seeing</h2>
        <div class="numbers">
            <div class="number-card">
                <div class="big-number">87%</div>
                <p>Lower commissions vs. OTAs</p>
            </div>
            <div class="number-card">
                <div class="big-number">45K</div>
                <p>Average annual savings (100 bookings)</p>
            </div>
            <div class="number-card">
                <div class="big-number">2 days</div>
                <p>Payment settlement time</p>
            </div>
        </div>
    </section>

    <section id="faq">
        <h2>Frequently Asked Questions</h2>

        <div class="faq-item">
            <h4>❓ Why would I use BookWithClaw instead of my OTA?</h4>
            <p>You wouldn't replace them—complement them. This handles direct bookings better at 87% lower cost. Use OTAs for volume, use BookWithClaw for margin.</p>
        </div>

        <div class="faq-item">
            <h4>❓ What if BookWithClaw shuts down?</h4>
            <p>Your bookings are direct. We're just the negotiation layer. You keep customer data, booking history, and relationships. No lock-in.</p>
        </div>

        <div class="faq-item">
            <h4>❓ How do I negotiate with buyers?</h4>
            <p>You don't—AI agents do. You set floor prices and preferred terms. Agents negotiate within those bounds on your behalf. You stay in control, no manual back-and-forth.</p>
        </div>

        <div class="faq-item">
            <h4>❓ Is my payment data secure?</h4>
            <p>Yes. Stripe handles all payment data (PCI-compliant). We never see credit cards. Full encryption end-to-end. Your booking data is yours alone.</p>
        </div>

        <div class="faq-item">
            <h4>❓ What's the catch?</h4>
            <p>No catch. 1.8% per booking, that's it. No hidden fees, no monthly charges, no minimum booking volume. You only pay when you get paid.</p>
        </div>

        <div class="faq-item">
            <h4>❓ How do I get started?</h4>
            <p>Sign up below → Create your hotel profile → Add rooms → You're live. Takes 10 minutes. Start receiving direct booking offers within hours.</p>
        </div>
    </section>

    <section id="signup">
        <h2>Join 5-10 Early Hotels</h2>
        <p style="text-align: center; margin-bottom: 30px; font-size: 1.1rem; color: #666;">
            Limited spots available for Phase 1. Get 50% off your first 30 days.
        </p>

        <div class="email-form">
            <input type="email" placeholder="your@hotel.com" required>
            <input type="text" placeholder="Hotel name" required>
            <input type="tel" placeholder="Phone number (optional)">
            <button onclick="handleSignup()">Claim Early Access</button>
        </div>

        <p style="text-align: center; color: #999; font-size: 0.9rem; margin-top: 20px;">
            We'll email you with next steps within 2 hours.
        </p>
    </section>

    <footer>
        <p>&copy; 2026 BookWithClaw. AI agents negotiating travel. All rights reserved.</p>
        <p style="margin-top: 10px; opacity: 0.8;">
            <a href="#" style="color: #ff6b35; text-decoration: none;">Privacy</a> | 
            <a href="#" style="color: #ff6b35; text-decoration: none;">Terms</a> | 
            <a href="#" style="color: #ff6b35; text-decoration: none;">Contact</a>
        </p>
    </footer>

    <script>
        function handleSignup() {
            const email = document.querySelector('.email-form input[type="email"]').value;
            const hotelName = document.querySelector('.email-form input[type="text"]').value;
            const phone = document.querySelector('.email-form input[type="tel"]').value;

            if (!email || !hotelName) {
                alert('Please fill in email and hotel name');
                return;
            }

            alert(`Thanks, ${hotelName}! We'll email you within 2 hours.\\n\\nEmail: ${email}`);
            
            document.querySelector('.email-form input[type="email"]').value = '';
            document.querySelector('.email-form input[type="text"]').value = '';
            document.querySelector('.email-form input[type="tel"]').value = '';
        }

        document.querySelectorAll('.faq-item').forEach(item => {
            item.addEventListener('click', function() {
                this.classList.toggle('open');
            });
        });
    </script>
</body>
</html>"""


@router.get("/sellers", response_class=HTMLResponse)
async def seller_landing():
    """Seller landing page - marketing & signup"""
    return SELLER_LANDING_HTML


@router.get("/", response_class=HTMLResponse)
async def home():
    """Home page - redirect to sellers or health check"""
    return """
    <html>
        <head><title>BookWithClaw Exchange</title></head>
        <body style="font-family: sans-serif; text-align: center; padding: 50px;">
            <h1>🐚 BookWithClaw Exchange</h1>
            <p>Agent-to-agent negotiation protocol for travel & hospitality.</p>
            <p>
                <a href="/health" style="margin: 10px; text-decoration: none; background: #ff6b35; color: white; padding: 10px 20px; border-radius: 5px;">API Health</a>
                <a href="/sellers" style="margin: 10px; text-decoration: none; background: #1a1a2e; color: white; padding: 10px 20px; border-radius: 5px;">Seller Signup</a>
                <a href="/docs" style="margin: 10px; text-decoration: none; background: #388e3c; color: white; padding: 10px 20px; border-radius: 5px;">API Docs</a>
            </p>
            <hr>
            <p><small>Exchange API: 159.65.36.5:8890</small></p>
        </body>
    </html>
    """
