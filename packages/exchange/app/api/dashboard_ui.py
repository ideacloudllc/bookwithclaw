"""Seller Dashboard UI - Serve the frontend HTML and login"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/sellers", tags=["dashboard-ui"])

LANDING_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BookWithClaw - Seller Signup</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        .container { display: grid; grid-template-columns: 1fr 1fr; gap: 40px; width: 100%; max-width: 1000px; padding: 40px; align-items: center; }
        .hero { color: white; }
        .hero h1 { font-size: 48px; margin-bottom: 20px; font-weight: 700; }
        .hero p { font-size: 18px; margin-bottom: 30px; opacity: 0.9; line-height: 1.6; }
        .hero ul { list-style: none; margin-bottom: 30px; }
        .hero li { margin-bottom: 15px; font-size: 16px; display: flex; align-items: center; }
        .hero li:before { content: "✓"; display: inline-block; margin-right: 12px; background: white; color: #667eea; width: 24px; height: 24px; border-radius: 50%; text-align: center; line-height: 24px; font-weight: bold; }
        
        .form-container { background: white; border-radius: 12px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); padding: 50px; }
        .form-container h2 { margin-bottom: 10px; color: #333; font-size: 28px; }
        .form-container p { color: #666; margin-bottom: 30px; }
        
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; font-weight: 500; color: #333; }
        input { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; }
        input:focus { outline: none; border-color: #667eea; box-shadow: 0 0 0 3px rgba(102,126,234,0.1); }
        button { width: 100%; padding: 12px; background: #667eea; color: white; border: none; border-radius: 6px; font-size: 16px; font-weight: 600; cursor: pointer; margin-top: 10px; }
        button:hover { background: #5568d3; }
        .login-link { text-align: center; margin-top: 20px; font-size: 14px; color: #666; }
        .login-link a { color: #667eea; text-decoration: none; }
        .error { color: #e74c3c; font-size: 14px; margin-top: 10px; display: none; }
        .success { color: #27ae60; font-size: 14px; margin-top: 10px; display: none; }
        
        @media (max-width: 768px) {
            .container { grid-template-columns: 1fr; padding: 20px; }
            .form-container { padding: 30px; }
            .hero h1 { font-size: 32px; }
            .container { gap: 20px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="hero">
            <h1>📍 BookWithClaw</h1>
            <p>Direct bookings for your hotel rooms. Skip the OTA fees and connect with guests instantly.</p>
            <ul>
                <li>Save 10% on booking fees (vs 12% OTAs)</li>
                <li>Instant notifications & direct communication</li>
                <li>Real-time rate management</li>
                <li>One-click booking confirmation</li>
                <li>Secure payment processing</li>
            </ul>
        </div>
        
        <div class="form-container">
            <h2>Create Your Account</h2>
            <p>Get started in 2 minutes</p>
            
            <form id="signupForm">
                <div class="form-group">
                    <label for="hotel_name">Hotel Name</label>
                    <input type="text" id="hotel_name" name="hotel_name" placeholder="Your Hotel" required>
                </div>
                <div class="form-group">
                    <label for="email">Email Address</label>
                    <input type="email" id="email" name="email" placeholder="your@hotel.com" required>
                </div>
                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" placeholder="Min 8 characters" required>
                </div>
                <button type="submit">Create Account</button>
                <div class="error" id="error"></div>
                <div class="success" id="success"></div>
            </form>
            
            <div class="login-link">
                Already have an account? <a href="/sellers/login">Sign in here</a>
            </div>
        </div>
    </div>

    <script>
        document.getElementById('signupForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const hotel_name = document.getElementById('hotel_name').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            if (password.length < 8) {
                showError('Password must be at least 8 characters');
                return;
            }
            
            try {
                const response = await fetch('/sellers/auth/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password, hotel_name })
                });
                
                if (response.ok) {
                    const data = await response.json();
                    // Store token in cookie
                    document.cookie = `token=${data.token}; path=/; max-age=2592000`;
                    // Redirect to portal
                    window.location.href = '/sellers/portal';
                } else {
                    const error = await response.json();
                    showError(error.detail || 'Signup failed');
                }
            } catch (err) {
                showError('Error: ' + err.message);
            }
        });
        
        function showError(msg) {
            document.getElementById('error').textContent = msg;
            document.getElementById('error').style.display = 'block';
            document.getElementById('success').style.display = 'none';
        }
    </script>
</body>
</html>"""

LOGIN_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BookWithClaw - Seller Login</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        .login-container { background: white; border-radius: 12px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); width: 100%; max-width: 400px; padding: 50px; }
        .logo { font-size: 32px; font-weight: 700; color: #667eea; margin-bottom: 30px; text-align: center; }
        h2 { color: #333; margin-bottom: 10px; }
        .subtitle { color: #666; margin-bottom: 30px; font-size: 14px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; font-weight: 500; color: #333; }
        input { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; }
        input:focus { outline: none; border-color: #667eea; box-shadow: 0 0 0 3px rgba(102,126,234,0.1); }
        button { width: 100%; padding: 12px; background: #667eea; color: white; border: none; border-radius: 6px; font-size: 16px; font-weight: 600; cursor: pointer; }
        button:hover { background: #5568d3; }
        .register-link { text-align: center; margin-top: 20px; font-size: 14px; }
        .register-link a { color: #667eea; text-decoration: none; }
        .error { color: #e74c3c; font-size: 14px; margin-top: 10px; display: none; }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">📍</div>
        <h2>BookWithClaw</h2>
        <p class="subtitle">Seller Dashboard</p>
        
        <form id="loginForm">
            <div class="form-group">
                <label for="email">Email Address</label>
                <input type="email" id="email" name="email" placeholder="your@hotel.com" required>
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" placeholder="Enter your password" required>
            </div>
            <button type="submit">Sign In</button>
            <div class="error" id="error"></div>
        </form>
        
        <div class="register-link">
            Don't have an account? <a href="/sellers">Sign up here</a>
        </div>
    </div>

    <script>
        document.getElementById('loginForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            try {
                const response = await fetch('/sellers/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });
                
                if (response.ok) {
                    const data = await response.json();
                    // Store token in cookie
                    document.cookie = `token=${data.token}; path=/; max-age=2592000`;
                    // Redirect to portal
                    window.location.href = '/sellers/portal';
                } else {
                    const error = await response.json();
                    showError(error.detail || 'Login failed');
                }
            } catch (err) {
                showError('Error: ' + err.message);
            }
        });
        
        function showError(msg) {
            document.getElementById('error').textContent = msg;
            document.getElementById('error').style.display = 'block';
        }
    </script>
</body>
</html>"""

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Seller Dashboard - BookWithClaw</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; color: #333; }
        
        .container { display: grid; grid-template-columns: 250px 1fr; min-height: 100vh; }
        
        /* Sidebar */
        .sidebar { background: #1a1a2e; color: white; padding: 20px; overflow-y: auto; position: sticky; top: 0; }
        .logo { font-size: 24px; font-weight: 700; color: #667eea; margin-bottom: 30px; }
        .seller-info { background: rgba(102,126,234,0.1); padding: 15px; border-radius: 6px; margin-bottom: 30px; font-size: 13px; }
        .seller-name { font-weight: 600; margin-bottom: 5px; }
        .nav { list-style: none; }
        .nav li { margin-bottom: 10px; }
        .nav a { color: #999; text-decoration: none; padding: 12px; display: block; border-radius: 4px; cursor: pointer; font-size: 14px; }
        .nav a:hover, .nav a.active { color: white; background: #667eea; }
        .logout { margin-top: 30px; padding-top: 20px; border-top: 1px solid #333; }
        .logout a { color: #e74c3c; }
        
        /* Main */
        .main { padding: 30px; overflow-y: auto; }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
        h1 { color: #1a1a2e; font-size: 32px; }
        
        /* Tabs */
        .tabs { display: flex; gap: 20px; margin-bottom: 30px; border-bottom: 2px solid #ddd; }
        .tab { padding: 12px 0; cursor: pointer; font-size: 14px; font-weight: 500; color: #999; border-bottom: 3px solid transparent; margin-bottom: -2px; }
        .tab:hover { color: #667eea; }
        .tab.active { color: #667eea; border-bottom-color: #667eea; }
        
        /* Cards */
        .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .stat-value { font-size: 28px; font-weight: 700; color: #667eea; }
        .stat-label { font-size: 12px; color: #999; margin-top: 5px; text-transform: uppercase; }
        
        /* Tables */
        .data-table { background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        table { width: 100%; border-collapse: collapse; }
        th { background: #f9f9f9; padding: 15px; text-align: left; font-size: 12px; font-weight: 600; color: #666; text-transform: uppercase; }
        td { padding: 15px; border-top: 1px solid #eee; font-size: 14px; }
        tr:hover { background: #f9f9f9; }
        .status { padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600; }
        .status.pending { background: #fff3cd; color: #856404; }
        .status.confirmed { background: #d4edda; color: #155724; }
        .status.active { background: #d4edda; color: #155724; }
        .price { color: #667eea; font-weight: 600; }
        
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        
        .empty { text-align: center; padding: 40px; color: #999; }
        
        @media (max-width: 768px) {
            .container { grid-template-columns: 1fr; }
            .sidebar { position: relative; }
            .stats { grid-template-columns: repeat(2, 1fr); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="sidebar">
            <div class="logo">📍 BWC</div>
            <div class="seller-info">
                <div class="seller-name" id="hotelName">Hotel Name</div>
                <div id="sellerEmail">email@example.com</div>
            </div>
            <ul class="nav">
                <li><a class="nav-link active" onclick="switchTab(this, 'dashboard')">📊 Dashboard</a></li>
                <li><a class="nav-link" onclick="switchTab(this, 'rooms')">🏨 Rooms</a></li>
                <li><a class="nav-link" onclick="switchTab(this, 'offers')">💬 Offers</a></li>
                <li><a class="nav-link" onclick="switchTab(this, 'bookings')">📅 Bookings</a></li>
                <li><a class="nav-link" onclick="switchTab(this, 'pricing')">💰 Pricing</a></li>
                <li><a class="nav-link" onclick="switchTab(this, 'profile')">👤 Profile</a></li>
            </ul>
            <div class="logout">
                <a onclick="logout()" style="cursor: pointer;">🚪 Logout</a>
            </div>
        </div>
        
        <div class="main">
            <div class="header">
                <h1 id="pageTitle">Dashboard</h1>
            </div>
            
            <!-- Dashboard Tab -->
            <div id="dashboard" class="tab-content active">
                <div class="stats" id="dashboardStats">
                    <div class="stat-card"><div class="stat-value">-</div><div class="stat-label">Active Listings</div></div>
                    <div class="stat-card"><div class="stat-value">-</div><div class="stat-label">Pending Offers</div></div>
                    <div class="stat-card"><div class="stat-value">-</div><div class="stat-label">This Month Bookings</div></div>
                    <div class="stat-card"><div class="stat-value">-</div><div class="stat-label">This Month Revenue</div></div>
                </div>
                <h3 style="margin-bottom: 20px;">Recent Offers</h3>
                <div id="recentOffers"></div>
                <h3 style="margin: 30px 0 20px;">Recent Bookings</h3>
                <div id="recentBookings"></div>
            </div>
            
            <!-- Rooms Tab -->
            <div id="rooms" class="tab-content">
                <div id="roomsList"></div>
            </div>
            
            <!-- Offers Tab -->
            <div id="offers" class="tab-content">
                <div id="offersList"></div>
            </div>
            
            <!-- Bookings Tab -->
            <div id="bookings" class="tab-content">
                <div id="bookingsList"></div>
            </div>
            
            <!-- Pricing Tab -->
            <div id="pricing" class="tab-content">
                <p>Pricing management coming soon</p>
            </div>
            
            <!-- Profile Tab -->
            <div id="profile" class="tab-content">
                <p>Profile editor coming soon</p>
            </div>
        </div>
    </div>

    <script>
        let authToken = null;
        
        // Get token from cookie
        function getToken() {
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                const [name, value] = cookie.trim().split('=');
                if (name === 'token') return value;
            }
            return null;
        }
        
        // Check authentication
        async function checkAuth() {
            authToken = getToken();
            if (!authToken) {
                window.location.href = '/sellers/login';
                return;
            }
            loadDashboard();
        }
        
        // Load dashboard data
        async function loadDashboard() {
            try {
                // Load seller info
                const meRes = await fetch('/sellers/me', {
                    headers: { 'cookie': `token=${authToken}` }
                });
                if (!meRes.ok) throw new Error('Auth failed');
                const me = await meRes.json();
                document.getElementById('hotelName').textContent = me.hotel_name || 'Hotel';
                document.getElementById('sellerEmail').textContent = me.email;
                
                // Load dashboard overview
                const dashRes = await fetch('/sellers/dashboard', {
                    headers: { 'cookie': `token=${authToken}` }
                });
                const dashboard = await dashRes.json();
                
                // Update stats
                const stats = dashboard.stats;
                document.querySelector('#dashboardStats > div:nth-child(1) .stat-value').textContent = stats.active_listings;
                document.querySelector('#dashboardStats > div:nth-child(2) .stat-value').textContent = stats.pending_offers;
                document.querySelector('#dashboardStats > div:nth-child(3) .stat-value').textContent = stats.this_month_bookings;
                document.querySelector('#dashboardStats > div:nth-child(4) .stat-value').textContent = '$' + stats.this_month_revenue.toFixed(2);
                
                // Update recent offers
                renderOffers(dashboard.recent_offers, 'recentOffers');
                
                // Update recent bookings
                renderBookings(dashboard.recent_bookings, 'recentBookings');
            } catch (err) {
                console.error('Error loading dashboard:', err);
            }
        }
        
        // Switch tabs
        function switchTab(clickedElement, tab) {
            // Update nav links
            document.querySelectorAll('.nav-link').forEach(link => link.classList.remove('active'));
            clickedElement.classList.add('active');
            
            // Update page title
            const titles = {
                dashboard: 'Dashboard',
                rooms: 'My Rooms',
                offers: 'Pending Offers',
                bookings: 'Confirmed Bookings',
                pricing: 'Pricing',
                profile: 'Profile'
            };
            document.getElementById('pageTitle').textContent = titles[tab];
            
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            const tabElement = document.getElementById(tab);
            if (tabElement) {
                tabElement.classList.add('active');
            }
            
            // Load tab data (async but don't wait)
            if (tab === 'rooms') loadRooms();
            else if (tab === 'offers') loadOffers();
            else if (tab === 'bookings') loadBookings();
        }
        
        // Load rooms
        async function loadRooms() {
            try {
                const res = await fetch('/sellers/rooms', {
                    headers: { 'cookie': `token=${authToken}` }
                });
                const data = await res.json();
                renderRoomsList(data.rooms);
            } catch (err) {
                console.error('Error loading rooms:', err);
            }
        }
        
        // Load offers
        async function loadOffers() {
            try {
                const res = await fetch('/sellers/offers', {
                    headers: { 'cookie': `token=${authToken}` }
                });
                const data = await res.json();
                renderOffers(data.offers, 'offersList');
            } catch (err) {
                console.error('Error loading offers:', err);
            }
        }
        
        // Load bookings
        async function loadBookings() {
            try {
                const res = await fetch('/sellers/bookings', {
                    headers: { 'cookie': `token=${authToken}` }
                });
                const data = await res.json();
                renderBookings(data.bookings, 'bookingsList');
            } catch (err) {
                console.error('Error loading bookings:', err);
            }
        }
        
        // Render rooms list
        function renderRoomsList(rooms) {
            let html = '<div class="data-table"><table><thead><tr><th>Room</th><th>Capacity</th><th>Base Rate</th><th>Floor Price</th><th>Status</th><th>Views</th><th>Bookings</th></tr></thead><tbody>';
            rooms.forEach(room => {
                html += \`<tr>
                    <td><strong>\${room.name}</strong></td>
                    <td>\${room.capacity} guests</td>
                    <td class="price">$\${room.base_rate}</td>
                    <td class="price">$\${room.floor_price}</td>
                    <td><span class="status \${room.status}">\${room.status}</span></td>
                    <td>\${room.views}</td>
                    <td>\${room.bookings}</td>
                </tr>\`;
            });
            html += '</tbody></table></div>';
            document.getElementById('roomsList').innerHTML = html;
        }
        
        // Render offers
        function renderOffers(offers, containerId) {
            if (!offers || offers.length === 0) {
                document.getElementById(containerId).innerHTML = '<div class="empty">No offers yet</div>';
                return;
            }
            let html = '<div class="data-table"><table><thead><tr><th>Guest</th><th>Room</th><th>Dates</th><th>Offered Price</th><th>Status</th></tr></thead><tbody>';
            offers.forEach(offer => {
                const nights = offer.nights || 1;
                html += \`<tr>
                    <td>\${offer.buyer_name}</td>
                    <td>\${offer.room_type}</td>
                    <td>\${offer.checkin} → \${offer.checkout} (\${nights} night\${nights > 1 ? 's' : ''})</td>
                    <td class="price">$\${offer.offered_price}/night</td>
                    <td><span class="status \${offer.status}">\${offer.status}</span></td>
                </tr>\`;
            });
            html += '</tbody></table></div>';
            document.getElementById(containerId).innerHTML = html;
        }
        
        // Render bookings
        function renderBookings(bookings, containerId) {
            if (!bookings || bookings.length === 0) {
                document.getElementById(containerId).innerHTML = '<div class="empty">No bookings yet</div>';
                return;
            }
            let html = '<div class="data-table"><table><thead><tr><th>Guest</th><th>Room</th><th>Dates</th><th>Total Revenue</th><th>Status</th></tr></thead><tbody>';
            bookings.forEach(booking => {
                const nights = booking.nights || 1;
                html += \`<tr>
                    <td>\${booking.guest_name}</td>
                    <td>\${booking.room_type}</td>
                    <td>\${booking.checkin} → \${booking.checkout} (\${nights} night\${nights > 1 ? 's' : ''})</td>
                    <td class="price">$\${booking.total}</td>
                    <td><span class="status \${booking.status}">\${booking.status}</span></td>
                </tr>\`;
            });
            html += '</tbody></table></div>';
            document.getElementById(containerId).innerHTML = html;
        }
        
        // Logout
        function logout() {
            document.cookie = 'token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 UTC';
            window.location.href = '/sellers/login';
        }
        
        // Initialize on page load
        checkAuth();
    </script>
</body>
</html>"""


@router.get("/", response_class=HTMLResponse)
async def sellers_landing():
    """Seller signup landing page."""
    return LANDING_HTML


@router.get("/login", response_class=HTMLResponse)
async def sellers_login():
    """Seller login page."""
    return LOGIN_HTML


@router.get("/portal", response_class=HTMLResponse)
async def sellers_portal():
    """Seller dashboard portal."""
    return DASHBOARD_HTML
