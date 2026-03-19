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
                const response = await fetch('/api/sellers/auth/register', {
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
                const response = await fetch('/api/sellers/auth/login', {
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
                const meRes = await fetch('/api/sellers/me', {
                    headers: { 'cookie': `token=${authToken}` }
                });
                if (!meRes.ok) throw new Error('Auth failed');
                const me = await meRes.json();
                document.getElementById('hotelName').textContent = me.hotel_name || 'Hotel';
                document.getElementById('sellerEmail').textContent = me.email;
                
                // Load dashboard overview
                const dashRes = await fetch('/api/sellers/dashboard', {
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
                const res = await fetch('/api/sellers/rooms', {
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
                const res = await fetch('/api/sellers/offers', {
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
                const res = await fetch('/api/sellers/bookings', {
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
                html += '<tr>' +
                    '<td><strong>' + room.name + '</strong></td>' +
                    '<td>' + room.capacity + ' guests</td>' +
                    '<td class="price">$' + room.base_rate + '</td>' +
                    '<td class="price">$' + room.floor_price + '</td>' +
                    '<td><span class="status ' + room.status + '">' + room.status + '</span></td>' +
                    '<td>' + room.views + '</td>' +
                    '<td>' + room.bookings + '</td>' +
                    '</tr>';
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
                const nightsLabel = nights > 1 ? 's' : '';
                html += '<tr>' +
                    '<td>' + offer.buyer_name + '</td>' +
                    '<td>' + offer.room_type + '</td>' +
                    '<td>' + offer.checkin + ' → ' + offer.checkout + ' (' + nights + ' night' + nightsLabel + ')</td>' +
                    '<td class="price">$' + offer.offered_price + '/night</td>' +
                    '<td><span class="status ' + offer.status + '">' + offer.status + '</span></td>' +
                    '</tr>';
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
                const nightsLabel = nights > 1 ? 's' : '';
                html += '<tr>' +
                    '<td>' + booking.guest_name + '</td>' +
                    '<td>' + booking.room_type + '</td>' +
                    '<td>' + booking.checkin + ' → ' + booking.checkout + ' (' + nights + ' night' + nightsLabel + ')</td>' +
                    '<td class="price">$' + booking.total + '</td>' +
                    '<td><span class="status ' + booking.status + '">' + booking.status + '</span></td>' +
                    '</tr>';
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


# ==================== BUYER DASHBOARD ====================

BUYER_LANDING_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BookWithClaw - Find Your Perfect Room</title>
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
            <h1>🌍 BookWithClaw</h1>
            <p>Negotiate direct with hoteliers. Better rates, instant bookings.</p>
            <ul>
                <li>Save 10% vs OTA fees</li>
                <li>Direct negotiation with hotels</li>
                <li>Instant confirmation</li>
                <li>Real-time rate updates</li>
                <li>Transparent pricing</li>
            </ul>
        </div>
        
        <div class="form-container">
            <h2>Create Your Account</h2>
            <p>Start booking in 2 minutes</p>
            
            <form id="signupForm">
                <div class="form-group">
                    <label for="first_name">Your Name</label>
                    <input type="text" id="first_name" name="first_name" placeholder="John Doe" required>
                </div>
                <div class="form-group">
                    <label for="email">Email Address</label>
                    <input type="email" id="email" name="email" placeholder="you@example.com" required>
                </div>
                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" placeholder="Min 8 characters" required>
                </div>
                <button type="submit">Create Account</button>
                <div class="error" id="error"></div>
            </form>
            
            <div class="login-link">
                Already have an account? <a href="/buyers/login">Sign in here</a>
            </div>
        </div>
    </div>

    <script>
        document.getElementById('signupForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const first_name = document.getElementById('first_name').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            if (password.length < 8) {
                showError('Password must be at least 8 characters');
                return;
            }

            try {
                const response = await fetch('/api/buyers/auth/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password, first_name })
                });
                
                if (response.ok) {
                    const data = await response.json();
                    document.cookie = `token=${data.token}; path=/; max-age=2592000`;
                    window.location.href = '/api/buyers/search';
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
        }
    </script>
</body>
</html>"""

BUYER_LOGIN_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BookWithClaw - Buyer Login</title>
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
        <div class="logo">🌍</div>
        <h2>BookWithClaw</h2>
        <p class="subtitle">Buyer Login</p>
        
        <form id="loginForm">
            <div class="form-group">
                <label for="email">Email Address</label>
                <input type="email" id="email" name="email" placeholder="you@example.com" required>
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" placeholder="Enter your password" required>
            </div>
            <button type="submit">Sign In</button>
            <div class="error" id="error"></div>
        </form>
        
        <div class="register-link">
            Don't have an account? <a href="/buyers">Sign up here</a>
        </div>
    </div>

    <script>
        document.getElementById('loginForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            try {
                const response = await fetch('/api/buyers/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });
                
                if (response.ok) {
                    const data = await response.json();
                    document.cookie = `token=${data.token}; path=/; max-age=2592000`;
                    window.location.href = '/api/buyers/search';
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

BUYER_SEARCH_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Search Rooms - BookWithClaw</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; color: #333; }
        
        .navbar { background: white; border-bottom: 1px solid #eee; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        .logo { font-size: 24px; font-weight: 700; color: #667eea; }
        .nav-links { display: flex; gap: 30px; }
        .nav-links a { text-decoration: none; color: #333; font-size: 14px; cursor: pointer; }
        .nav-links a:hover { color: #667eea; }
        .logout { color: #e74c3c; }
        
        .container { max-width: 1200px; margin: 0 auto; padding: 30px; }
        
        .search-bar { background: white; padding: 30px; border-radius: 8px; margin-bottom: 30px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .search-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 15px; margin-bottom: 15px; }
        .search-input { display: flex; flex-direction: column; }
        .search-input label { font-size: 12px; font-weight: 600; margin-bottom: 5px; color: #666; text-transform: uppercase; }
        .search-input input { padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; }
        .search-button { grid-column: 5; display: flex; align-items: flex-end; }
        .search-button button { width: 100%; padding: 10px; background: #667eea; color: white; border: none; border-radius: 4px; font-weight: 600; cursor: pointer; }
        .search-button button:hover { background: #5568d3; }
        
        .results-header { margin-bottom: 20px; }
        .results-header h2 { margin-bottom: 5px; }
        .results-count { color: #666; font-size: 14px; }
        
        .rooms-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
        .room-card { background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); cursor: pointer; transition: transform 0.2s, box-shadow 0.2s; }
        .room-card:hover { transform: translateY(-5px); box-shadow: 0 8px 16px rgba(0,0,0,0.15); }
        
        .room-image { width: 100%; height: 200px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: flex; align-items: center; justify-content: center; color: white; font-size: 48px; }
        .room-details { padding: 20px; }
        .room-name { font-weight: 600; font-size: 16px; margin-bottom: 5px; }
        .room-location { color: #999; font-size: 13px; margin-bottom: 10px; }
        .room-amenities { display: flex; gap: 5px; flex-wrap: wrap; margin-bottom: 10px; }
        .amenity { background: #f0f0f0; padding: 2px 8px; border-radius: 12px; font-size: 11px; color: #666; }
        .room-price { display: flex; gap: 10px; margin-bottom: 15px; align-items: baseline; }
        .price-current { font-size: 20px; font-weight: 700; color: #667eea; }
        .price-base { font-size: 14px; color: #999; text-decoration: line-through; }
        .room-rating { color: #ffc107; font-size: 13px; margin-bottom: 15px; }
        .room-button { width: 100%; padding: 10px; background: #667eea; color: white; border: none; border-radius: 4px; font-weight: 600; cursor: pointer; }
        .room-button:hover { background: #5568d3; }
        
        .empty { text-align: center; padding: 60px 20px; color: #999; }
        
        @media (max-width: 1200px) {
            .rooms-grid { grid-template-columns: repeat(2, 1fr); }
            .search-grid { grid-template-columns: repeat(3, 1fr); }
        }
        
        @media (max-width: 768px) {
            .rooms-grid { grid-template-columns: 1fr; }
            .search-grid { grid-template-columns: 1fr; }
            .search-button { grid-column: 1; }
        }
    </style>
</head>
<body>
    <div class="navbar">
        <div class="logo">🌍 BookWithClaw</div>
        <div class="nav-links">
            <a onclick="goToOffers()">💬 My Offers</a>
            <a onclick="goToBookings()">📅 My Bookings</a>
            <a onclick="logout()" class="logout">🚪 Logout</a>
        </div>
    </div>
    
    <div class="container">
        <div class="search-bar">
            <div class="search-grid">
                <div class="search-input">
                    <label>Check-in</label>
                    <input type="date" id="checkin" value="2026-03-25">
                </div>
                <div class="search-input">
                    <label>Check-out</label>
                    <input type="date" id="checkout" value="2026-03-27">
                </div>
                <div class="search-input">
                    <label>Location</label>
                    <input type="text" id="location" placeholder="City or hotel">
                </div>
                <div class="search-input">
                    <label>Max Price</label>
                    <input type="number" id="maxprice" placeholder="e.g., 500">
                </div>
                <div class="search-button">
                    <button onclick="search()">🔍 Search</button>
                </div>
            </div>
        </div>
        
        <div class="results-header">
            <h2>Available Rooms</h2>
            <div class="results-count" id="resultsCount">Loading...</div>
        </div>
        
        <div class="rooms-grid" id="roomsGrid">
            <div class="empty">Loading rooms...</div>
        </div>
    </div>

    <script>
        let authToken = null;
        
        function getToken() {
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                const [name, value] = cookie.trim().split('=');
                if (name === 'token') return value;
            }
            return null;
        }
        
        async function checkAuth() {
            authToken = getToken();
            if (!authToken) {
                window.location.href = '/buyers/login';
                return;
            }
            search();
        }
        
        async function search() {
            try {
                const checkin = document.getElementById('checkin').value;
                const checkout = document.getElementById('checkout').value;
                const location = document.getElementById('location').value;
                const maxprice = document.getElementById('maxprice').value;
                
                let url = `/buyers/search?checkin=${checkin}&checkout=${checkout}`;
                if (location) url += '&location=' + encodeURIComponent(location);
                if (maxprice) url += '&max_price=' + maxprice;
                
                const res = await fetch(url, {
                    headers: { 'cookie': `token=${authToken}` }
                });
                const data = await res.json();
                
                document.getElementById('resultsCount').textContent = data.total + ' rooms available';
                
                if (!data.results || data.results.length === 0) {
                    document.getElementById('roomsGrid').innerHTML = '<div class="empty">No rooms found. Try adjusting your search.</div>';
                    return;
                }
                
                let html = '';
                data.results.forEach(room => {
                    const savings = room.base_price - room.floor_price;
                    html += '<div class="room-card" onclick="viewRoom(' + room.room_id.replace('rm_', '') + ')">' +
                        '<div class="room-image">🏨</div>' +
                        '<div class="room-details">' +
                        '<div class="room-name">' + room.hotel_name + '</div>' +
                        '<div class="room-location">' + room.location + '</div>' +
                        '<div class="room-amenities">';
                    (room.amenities || []).slice(0, 3).forEach(a => {
                        html += '<span class="amenity">' + a + '</span>';
                    });
                    html += '</div>' +
                        '<div class="room-price">' +
                        '<span class="price-current">$' + room.floor_price + '/night</span>' +
                        '<span class="price-base">$' + room.base_price + '</span>' +
                        '</div>' +
                        '<div class="room-rating">⭐ ' + room.rating + ' (' + room.reviews + ' reviews)</div>' +
                        '<button class="room-button">View & Make Offer →</button>' +
                        '</div>' +
                        '</div>';
                });
                document.getElementById('roomsGrid').innerHTML = html;
            } catch (err) {
                console.error('Error searching:', err);
                document.getElementById('roomsGrid').innerHTML = '<div class="empty">Error loading rooms</div>';
            }
        }
        
        function viewRoom(roomId) {
            window.location.href = '/api/buyers/rooms/' + roomId;
        }
        
        function goToOffers() {
            window.location.href = '/api/buyers/my-offers';
        }
        
        function goToBookings() {
            window.location.href = '/api/buyers/my-bookings';
        }
        
        function logout() {
            document.cookie = 'token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 UTC';
            window.location.href = '/buyers/login';
        }
        
        checkAuth();
    </script>
</body>
</html>"""

BUYER_ROOM_DETAIL_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Room Details - BookWithClaw</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; color: #333; }
        
        .navbar { background: white; border-bottom: 1px solid #eee; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 24px; font-weight: 700; color: #667eea; }
        .back { color: #667eea; cursor: pointer; font-weight: 600; }
        
        .container { max-width: 1000px; margin: 0 auto; padding: 30px; }
        
        .breadcrumb { color: #999; font-size: 14px; margin-bottom: 20px; }
        .breadcrumb a { color: #667eea; cursor: pointer; text-decoration: none; }
        
        .detail-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 30px; }
        
        .gallery { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 8px; padding: 40px; text-align: center; color: white; min-height: 300px; display: flex; align-items: center; justify-content: center; font-size: 80px; }
        
        .info { }
        .title { font-size: 28px; font-weight: 700; margin-bottom: 5px; }
        .location { color: #999; font-size: 14px; margin-bottom: 20px; }
        .rating { margin-bottom: 20px; }
        .star { color: #ffc107; }
        
        .specs { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .spec { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #eee; }
        .spec:last-child { border: none; }
        
        .amenities { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .amenities h3 { margin-bottom: 15px; font-size: 14px; font-weight: 600; }
        .amenity-list { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
        .amenity { padding: 8px; background: #f9f9f9; border-radius: 4px; font-size: 13px; }
        
        .description { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; line-height: 1.6; }
        
        .offer-panel { background: white; padding: 20px; border-radius: 8px; border: 2px solid #667eea; }
        .offer-header { font-size: 18px; font-weight: 700; margin-bottom: 15px; }
        .price-range { display: flex; justify-content: space-between; margin-bottom: 15px; padding: 15px; background: #f9f9f9; border-radius: 4px; }
        .price-item { text-align: center; }
        .price-label { font-size: 12px; color: #999; margin-bottom: 5px; }
        .price-value { font-size: 20px; font-weight: 700; color: #667eea; }
        
        .offer-form { margin-bottom: 15px; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; font-size: 12px; font-weight: 600; margin-bottom: 5px; color: #666; text-transform: uppercase; }
        .form-group input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; }
        
        .buttons { display: flex; gap: 10px; }
        .btn { flex: 1; padding: 12px; border: none; border-radius: 4px; font-weight: 600; cursor: pointer; }
        .btn-primary { background: #667eea; color: white; }
        .btn-primary:hover { background: #5568d3; }
        .btn-secondary { background: #f0f0f0; color: #333; }
        .btn-secondary:hover { background: #e0e0e0; }
        
        @media (max-width: 768px) {
            .detail-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="navbar">
        <div class="logo">🌍 BookWithClaw</div>
        <a class="back" onclick="window.location.href='/api/buyers/search'">← Back to Search</a>
    </div>
    
    <div class="container">
        <div class="breadcrumb">
            <a onclick="window.location.href='/api/buyers/search'">Search</a> → Room Details
        </div>
        
        <div class="detail-grid">
            <div>
                <div class="gallery" id="gallery">🏨</div>
                <div class="description" id="description"></div>
            </div>
            
            <div>
                <div class="title" id="title">Loading...</div>
                <div class="location" id="location"></div>
                <div class="rating" id="rating"></div>
                
                <div class="specs" id="specs"></div>
                <div class="amenities" id="amenities"></div>
                
                <div class="offer-panel">
                    <div class="offer-header">Make an Offer</div>
                    <div class="price-range">
                        <div class="price-item">
                            <div class="price-label">Floor Price</div>
                            <div class="price-value" id="floorPrice">$280</div>
                        </div>
                        <div class="price-item">
                            <div class="price-label">Your Offer</div>
                            <div class="price-value" id="yourOffer">—</div>
                        </div>
                        <div class="price-item">
                            <div class="price-label">Base Price</div>
                            <div class="price-value" id="basePrice">$350</div>
                        </div>
                    </div>
                    
                    <div class="offer-form">
                        <div class="form-group">
                            <label>Your Offer Price/Night</label>
                            <input type="number" id="offerPrice" placeholder="$300" oninput="updateOffer()">
                        </div>
                        <div class="form-group">
                            <label>Check-in</label>
                            <input type="date" id="checkin" value="2026-03-25">
                        </div>
                        <div class="form-group">
                            <label>Check-out</label>
                            <input type="date" id="checkout" value="2026-03-27">
                        </div>
                        <div class="form-group">
                            <label>Total (2 nights)</label>
                            <div style="font-size: 20px; font-weight: 700; color: #667eea;" id="total">$600</div>
                        </div>
                    </div>
                    
                    <div class="buttons">
                        <button class="btn btn-primary" onclick="submitOffer()">Submit Offer</button>
                        <button class="btn btn-secondary" onclick="window.location.href='/api/buyers/search'">Cancel</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let authToken = null;
        let roomData = null;
        
        function getToken() {
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                const [name, value] = cookie.trim().split('=');
                if (name === 'token') return value;
            }
            return null;
        }
        
        async function loadRoom() {
            authToken = getToken();
            if (!authToken) {
                window.location.href = '/buyers/login';
                return;
            }
            
            const roomId = window.location.pathname.split('/').pop();
            try {
                const res = await fetch(`/buyers/rooms/${roomId}`, {
                    headers: { 'cookie': `token=${authToken}` }
                });
                roomData = await res.json();
                renderRoom();
            } catch (err) {
                console.error('Error loading room:', err);
            }
        }
        
        function renderRoom() {
            document.getElementById('title').textContent = roomData.hotel_name;
            document.getElementById('location').textContent = roomData.location;
            document.getElementById('rating').innerHTML = '⭐ ' + roomData.rating + ' (' + roomData.reviews + ' reviews)';
            document.getElementById('description').textContent = roomData.description;
            document.getElementById('floorPrice').textContent = '$' + roomData.floor_price;
            document.getElementById('basePrice').textContent = '$' + roomData.base_price;
            
            let specs = '<div style="font-weight: 600; margin-bottom: 10px;">Room Details</div>';
            specs += '<div class="spec"><span>Type</span><strong>' + roomData.room_type + '</strong></div>';
            specs += '<div class="spec"><span>Capacity</span><strong>' + roomData.capacity + ' guests</strong></div>';
            specs += '<div class="spec"><span>Check-in</span><strong>' + roomData.check_in_time + '</strong></div>';
            specs += '<div class="spec"><span>Check-out</span><strong>' + roomData.check_out_time + '</strong></div>';
            document.getElementById('specs').innerHTML = specs;
            
            let amenities = '<h3>Amenities</h3><div class="amenity-list">';
            roomData.amenities.forEach(a => {
                amenities += '<div class="amenity">✓ ' + a + '</div>';
            });
            amenities += '</div>';
            document.getElementById('amenities').innerHTML = amenities;
        }
        
        function updateOffer() {
            const price = parseFloat(document.getElementById('offerPrice').value) || 0;
            document.getElementById('yourOffer').textContent = price > 0 ? '$' + price : '—';
            
            const checkin = new Date(document.getElementById('checkin').value);
            const checkout = new Date(document.getElementById('checkout').value);
            const nights = Math.ceil((checkout - checkin) / (1000 * 60 * 60 * 24));
            const total = price * nights;
            
            document.getElementById('total').textContent = total > 0 ? '$' + total : '$0';
        }
        
        async function submitOffer() {
            const price = parseFloat(document.getElementById('offerPrice').value);
            const checkin = document.getElementById('checkin').value;
            const checkout = document.getElementById('checkout').value;
            
            if (!price || price < roomData.floor_price) {
                alert('Offer must be at least $' + roomData.floor_price + '/night');
                return;
            }
            
            try {
                const res = await fetch('/api/buyers/make-offer', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'cookie': `token=${authToken}`
                    },
                    body: JSON.stringify({
                        room_id: 'rm_' + window.location.pathname.split('/').pop(),
                        checkin,
                        checkout,
                        offered_price: price
                    })
                });
                
                if (res.ok) {
                    alert('Offer submitted! View progress in My Offers.');
                    window.location.href = '/api/buyers/my-offers';
                } else {
                    alert('Error submitting offer');
                }
            } catch (err) {
                alert('Error: ' + err.message);
            }
        }
        
        loadRoom();
    </script>
</body>
</html>"""

BUYER_OFFERS_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Offers - BookWithClaw</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; color: #333; }
        
        .navbar { background: white; border-bottom: 1px solid #eee; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 24px; font-weight: 700; color: #667eea; }
        .nav-links { display: flex; gap: 30px; }
        .nav-links a { text-decoration: none; color: #333; font-size: 14px; cursor: pointer; }
        .nav-links a:hover { color: #667eea; }
        
        .container { max-width: 1000px; margin: 0 auto; padding: 30px; }
        .header { margin-bottom: 30px; }
        .header h1 { margin-bottom: 5px; }
        .header p { color: #999; font-size: 14px; }
        
        .offer-card { background: white; border-radius: 8px; margin-bottom: 20px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .offer-header { display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: 20px; padding: 20px; background: #f9f9f9; }
        .offer-title { font-weight: 600; }
        .offer-price { text-align: center; }
        .offer-status { text-align: right; }
        .status-badge { display: inline-block; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600; }
        .status-awaiting { background: #fff3cd; color: #856404; }
        .status-confirmed { background: #d4edda; color: #155724; }
        
        .offer-messages { padding: 20px; }
        .message { padding: 15px; margin-bottom: 10px; border-radius: 4px; font-size: 13px; line-height: 1.5; }
        .message.you { background: #e7f0ff; color: #0066cc; }
        .message.seller { background: #f0f0f0; color: #666; }
        .message-meta { font-size: 12px; opacity: 0.7; margin-bottom: 5px; }
        
        .offer-actions { padding: 20px; border-top: 1px solid #eee; display: flex; gap: 10px; }
        .btn { padding: 10px 15px; border: none; border-radius: 4px; font-weight: 600; cursor: pointer; font-size: 13px; }
        .btn-primary { background: #667eea; color: white; }
        .btn-secondary { background: #f0f0f0; color: #333; }
        .btn-danger { background: #e74c3c; color: white; }
        .btn:hover { opacity: 0.8; }
        
        .empty { text-align: center; padding: 60px 20px; color: #999; }
        
        @media (max-width: 768px) {
            .offer-header { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="navbar">
        <div class="logo">🌍 BookWithClaw</div>
        <div class="nav-links">
            <a onclick="goToSearch()">🔍 Search</a>
            <a onclick="goToBookings()">📅 My Bookings</a>
            <a onclick="logout()" style="color: #e74c3c;">🚪 Logout</a>
        </div>
    </div>
    
    <div class="container">
        <div class="header">
            <h1>💬 My Offers</h1>
            <p>Track your active negotiations and past bookings</p>
        </div>
        
        <div id="offersList"></div>
    </div>

    <script>
        let authToken = null;
        
        function getToken() {
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                const [name, value] = cookie.trim().split('=');
                if (name === 'token') return value;
            }
            return null;
        }
        
        async function loadOffers() {
            authToken = getToken();
            if (!authToken) {
                window.location.href = '/buyers/login';
                return;
            }
            
            try {
                const res = await fetch('/api/buyers/my-offers', {
                    headers: { 'cookie': `token=${authToken}` }
                });
                const data = await res.json();
                renderOffers(data.offers);
            } catch (err) {
                console.error('Error loading offers:', err);
                document.getElementById('offersList').innerHTML = '<div class="empty">Error loading offers</div>';
            }
        }
        
        function renderOffers(offers) {
            if (!offers || offers.length === 0) {
                document.getElementById('offersList').innerHTML = '<div class="empty">No active offers. <a onclick="goToSearch()" style="color: #667eea; cursor: pointer;">Start searching</a></div>';
                return;
            }
            
            let html = '';
            offers.forEach(offer => {
                const statusClass = offer.status === 'confirmed' ? 'status-confirmed' : 'status-awaiting';
                html += '<div class="offer-card">' +
                    '<div class="offer-header">' +
                    '<div><div class="offer-title">' + offer.hotel_name + '</div><div style="color: #999; font-size: 13px; margin-top: 3px;">' + offer.room_type + ' • ' + offer.checkin + ' → ' + offer.checkout + '</div></div>' +
                    '<div class="offer-price"><div style="color: #999; font-size: 12px;">Your Offer</div><div style="font-size: 20px; font-weight: 700; color: #667eea;">$' + offer.offered_price + '</div></div>' +
                    '<div style="font-size: 13px;"><div style="color: #999; margin-bottom: 5px;">Seller Response</div><div style="font-weight: 600;">' + (offer.seller_counter ? '$' + offer.seller_counter : '—') + '</div></div>' +
                    '<div class="offer-status"><span class="status-badge ' + statusClass + '">' + offer.status.replace('_', ' ').toUpperCase() + '</span></div>' +
                    '</div>' +
                    '<div class="offer-messages">';
                
                offer.messages.forEach(msg => {
                    const msgClass = msg.from === 'you' ? 'you' : 'seller';
                    html += '<div class="message ' + msgClass + '">' +
                        '<div class="message-meta">' + (msg.from === 'you' ? 'You' : 'Seller') + ' • ' + msg.at + '</div>' +
                        msg.text +
                        '</div>';
                });
                
                html += '</div>';
                
                if (offer.status === 'awaiting_your_response') {
                    html += '<div class="offer-actions">' +
                        '<button class="btn btn-primary" onclick="counterOffer(' + offer.offer_id + ')">Make Counter-Offer</button>' +
                        '<button class="btn btn-secondary" onclick="acceptOffer(' + offer.offer_id + ')">Accept</button>' +
                        '<button class="btn btn-danger" onclick="rejectOffer(' + offer.offer_id + ')">Reject</button>' +
                        '</div>';
                } else if (offer.status === 'awaiting_seller_response') {
                    html += '<div class="offer-actions">' +
                        '<p style="color: #999; font-size: 13px;">⏳ Waiting for seller response...</p>' +
                        '</div>';
                }
                
                html += '</div>';
            });
            
            document.getElementById('offersList').innerHTML = html;
        }
        
        function counterOffer(offerId) {
            const price = prompt('Enter your counter-offer price:');
            if (price) {
                fetch('/api/buyers/offers/' + offerId + '/counter', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'cookie': `token=${authToken}` },
                    body: JSON.stringify({ counter_price: parseInt(price) })
                }).then(() => loadOffers());
            }
        }
        
        function acceptOffer(offerId) {
            if (confirm('Accept this offer?')) {
                fetch('/api/buyers/offers/' + offerId + '/accept', {
                    method: 'POST',
                    headers: { 'cookie': `token=${authToken}` }
                }).then(() => {
                    alert('Offer accepted! Proceeding to payment...');
                    loadOffers();
                });
            }
        }
        
        function rejectOffer(offerId) {
            if (confirm('Reject this offer?')) {
                fetch('/api/buyers/offers/' + offerId + '/reject', {
                    method: 'POST',
                    headers: { 'cookie': `token=${authToken}` }
                }).then(() => loadOffers());
            }
        }
        
        function goToSearch() {
            window.location.href = '/api/buyers/search';
        }
        
        function goToBookings() {
            window.location.href = '/api/buyers/my-bookings';
        }
        
        function logout() {
            document.cookie = 'token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 UTC';
            window.location.href = '/buyers/login';
        }
        
        loadOffers();
    </script>
</body>
</html>"""

BUYER_BOOKINGS_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Bookings - BookWithClaw</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; color: #333; }
        
        .navbar { background: white; border-bottom: 1px solid #eee; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 24px; font-weight: 700; color: #667eea; }
        .nav-links { display: flex; gap: 30px; }
        .nav-links a { text-decoration: none; color: #333; font-size: 14px; cursor: pointer; }
        .nav-links a:hover { color: #667eea; }
        
        .container { max-width: 1000px; margin: 0 auto; padding: 30px; }
        .header { margin-bottom: 30px; }
        .header h1 { margin-bottom: 5px; }
        
        .booking-card { background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .booking-grid { display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 20px; }
        .booking-info h3 { margin-bottom: 5px; font-size: 16px; }
        .booking-meta { color: #999; font-size: 13px; line-height: 1.5; }
        .booking-meta div { margin: 2px 0; }
        .booking-dates { text-align: center; }
        .booking-dates div { margin-bottom: 5px; }
        .booking-dates .dates-label { color: #999; font-size: 12px; }
        .booking-dates .dates-value { font-size: 14px; font-weight: 600; }
        .booking-price { text-align: right; }
        .booking-price .label { color: #999; font-size: 12px; margin-bottom: 5px; }
        .booking-price .amount { font-size: 24px; font-weight: 700; color: #667eea; }
        .booking-price .confirmation { color: #999; font-size: 12px; margin-top: 10px; }
        
        .booking-actions { margin-top: 20px; padding-top: 20px; border-top: 1px solid #eee; display: flex; gap: 10px; }
        .btn { padding: 10px 15px; border: none; border-radius: 4px; font-weight: 600; cursor: pointer; font-size: 13px; }
        .btn-secondary { background: #f0f0f0; color: #333; }
        .btn-secondary:hover { background: #e0e0e0; }
        
        .empty { text-align: center; padding: 60px 20px; color: #999; }
        
        @media (max-width: 768px) {
            .booking-grid { grid-template-columns: 1fr; }
            .booking-price { text-align: left; }
        }
    </style>
</head>
<body>
    <div class="navbar">
        <div class="logo">🌍 BookWithClaw</div>
        <div class="nav-links">
            <a onclick="goToSearch()">🔍 Search</a>
            <a onclick="goToOffers()">💬 My Offers</a>
            <a onclick="logout()" style="color: #e74c3c;">🚪 Logout</a>
        </div>
    </div>
    
    <div class="container">
        <div class="header">
            <h1>📅 My Bookings</h1>
        </div>
        
        <div id="bookingsList"></div>
    </div>

    <script>
        let authToken = null;
        
        function getToken() {
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                const [name, value] = cookie.trim().split('=');
                if (name === 'token') return value;
            }
            return null;
        }
        
        async function loadBookings() {
            authToken = getToken();
            if (!authToken) {
                window.location.href = '/buyers/login';
                return;
            }
            
            try {
                const res = await fetch('/api/buyers/my-bookings', {
                    headers: { 'cookie': `token=${authToken}` }
                });
                const data = await res.json();
                renderBookings(data.bookings);
            } catch (err) {
                console.error('Error loading bookings:', err);
                document.getElementById('bookingsList').innerHTML = '<div class="empty">Error loading bookings</div>';
            }
        }
        
        function renderBookings(bookings) {
            if (!bookings || bookings.length === 0) {
                document.getElementById('bookingsList').innerHTML = '<div class="empty">No confirmed bookings yet. <a onclick="goToSearch()" style="color: #667eea; cursor: pointer;">Start booking</a></div>';
                return;
            }
            
            let html = '';
            bookings.forEach(booking => {
                html += '<div class="booking-card">' +
                    '<div class="booking-grid">' +
                    '<div class="booking-info">' +
                    '<h3>' + booking.hotel_name + '</h3>' +
                    '<div class="booking-meta">' +
                    '<div>📍 ' + booking.location + '</div>' +
                    '<div>🏨 ' + booking.room_type + ' • ' + booking.nights + ' night' + (booking.nights > 1 ? 's' : '') + '</div>' +
                    '<div>✓ Confirmation: ' + booking.booking_id + '</div>' +
                    '</div>' +
                    '</div>' +
                    '<div class="booking-dates">' +
                    '<div class="dates-label">Check-in — Check-out</div>' +
                    '<div class="dates-value">' + booking.checkin + ' — ' + booking.checkout + '</div>' +
                    '<div class="dates-label" style="margin-top: 10px;">Status</div>' +
                    '<div class="dates-value" style="color: #27ae60;">Confirmed ✓</div>' +
                    '</div>' +
                    '<div class="booking-price">' +
                    '<div class="label">Total Paid</div>' +
                    '<div class="amount">$' + booking.total_price + '</div>' +
                    '<div class="confirmation">Check-in: 3:00 PM</div>' +
                    '</div>' +
                    '</div>' +
                    '<div class="booking-actions">' +
                    '<button class="btn btn-secondary" onclick="viewDetails(' + booking.booking_id + ')">View Details</button>' +
                    '</div>' +
                    '</div>';
            });
            
            document.getElementById('bookingsList').innerHTML = html;
        }
        
        function viewDetails(bookingId) {
            alert('Booking Details: ' + bookingId + '\\n\\nView full details and check-in instructions coming soon.');
        }
        
        function goToSearch() {
            window.location.href = '/api/buyers/search';
        }
        
        function goToOffers() {
            window.location.href = '/api/buyers/my-offers';
        }
        
        function logout() {
            document.cookie = 'token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 UTC';
            window.location.href = '/buyers/login';
        }
        
        loadBookings();
    </script>
</body>
</html>"""


# Buyer routes
buyer_router = APIRouter(prefix="/buyers", tags=["buyer-dashboard-ui"])

@buyer_router.get("/", response_class=HTMLResponse)
async def buyers_landing():
    """Buyer signup landing page."""
    return BUYER_LANDING_HTML

@buyer_router.get("/login", response_class=HTMLResponse)
async def buyers_login():
    """Buyer login page."""
    return BUYER_LOGIN_HTML

@buyer_router.get("/search", response_class=HTMLResponse)
async def buyers_search():
    """Buyer search/discovery page."""
    return BUYER_SEARCH_HTML

@buyer_router.get("/rooms/{room_id}", response_class=HTMLResponse)
async def buyer_room_detail(room_id: str):
    """Buyer room detail and offer page."""
    return BUYER_ROOM_DETAIL_HTML

@buyer_router.get("/my-offers", response_class=HTMLResponse)
async def buyer_offers():
    """Buyer negotiation/offers page."""
    return BUYER_OFFERS_HTML

@buyer_router.get("/my-bookings", response_class=HTMLResponse)
async def buyer_bookings():
    """Buyer bookings page."""
    return BUYER_BOOKINGS_HTML
