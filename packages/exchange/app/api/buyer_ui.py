"""Buyer Dashboard UI - HTML/CSS/JS"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/buyers", tags=["buyer-ui"])

# Will split into signup, search, detail, and offers pages
# Starting with login/signup + search interface

BUYER_LOGIN_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BookWithClaw - Find Hotels</title>
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
        .logo { font-size: 32px; font-weight: 700; color: #667eea; margin-bottom: 30px; }
        h2 { color: #333; margin-bottom: 10px; }
        .subtitle { color: #666; margin-bottom: 30px; font-size: 14px; }
        
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; font-weight: 500; color: #333; }
        input { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; }
        input:focus { outline: none; border-color: #667eea; box-shadow: 0 0 0 3px rgba(102,126,234,0.1); }
        button { width: 100%; padding: 12px; background: #667eea; color: white; border: none; border-radius: 6px; font-size: 16px; font-weight: 600; cursor: pointer; }
        button:hover { background: #5568d3; }
        .tabs { display: flex; gap: 20px; margin-bottom: 30px; border-bottom: 2px solid #eee; }
        .tab { padding: 12px 0; cursor: pointer; font-weight: 600; color: #999; border-bottom: 3px solid transparent; margin-bottom: -2px; }
        .tab.active { color: #667eea; border-bottom-color: #667eea; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .register-link { text-align: center; margin-top: 20px; font-size: 14px; }
        .register-link a { color: #667eea; text-decoration: none; cursor: pointer; }
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
            <h1>🏨 BookWithClaw</h1>
            <p>Book hotel rooms directly. No middlemen, better rates, instant booking.</p>
            <ul>
                <li>10-50% cheaper than Booking.com</li>
                <li>Instant availability & booking confirmation</li>
                <li>Negotiate rates directly with hotels</li>
                <li>Direct communication with property</li>
                <li>Best rates guaranteed</li>
            </ul>
        </div>
        
        <div class="form-container">
            <div class="logo">📍</div>
            
            <div class="tabs">
                <div class="tab active" onclick="switchAuthTab('login')">Sign In</div>
                <div class="tab" onclick="switchAuthTab('signup')">Create Account</div>
            </div>
            
            <!-- Login Tab -->
            <div id="login" class="tab-content active">
                <h2>Sign In</h2>
                <p class="subtitle">Find and book the perfect room</p>
                <form id="loginForm">
                    <div class="form-group">
                        <label>Email Address</label>
                        <input type="email" id="loginEmail" placeholder="you@example.com" required>
                    </div>
                    <div class="form-group">
                        <label>Password</label>
                        <input type="password" id="loginPassword" placeholder="Enter your password" required>
                    </div>
                    <button type="submit">Sign In</button>
                    <div class="error" id="loginError"></div>
                </form>
            </div>
            
            <!-- Signup Tab -->
            <div id="signup" class="tab-content">
                <h2>Create Account</h2>
                <p class="subtitle">Join and start booking</p>
                <form id="signupForm">
                    <div class="form-group">
                        <label>First Name</label>
                        <input type="text" id="firstName" placeholder="John" required>
                    </div>
                    <div class="form-group">
                        <label>Email Address</label>
                        <input type="email" id="signupEmail" placeholder="you@example.com" required>
                    </div>
                    <div class="form-group">
                        <label>Password</label>
                        <input type="password" id="signupPassword" placeholder="Min 8 characters" required>
                    </div>
                    <button type="submit">Create Account</button>
                    <div class="error" id="signupError"></div>
                </form>
            </div>
        </div>
    </div>

    <script>
        function switchAuthTab(tab) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
            document.getElementById(tab).classList.add('active');
            event.target.classList.add('active');
        }
        
        // Login form
        document.getElementById('loginForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('loginEmail').value;
            const password = document.getElementById('loginPassword').value;
            
            try {
                const response = await fetch('/buyers/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });
                
                if (response.ok) {
                    const data = await response.json();
                    document.cookie = `token=${data.token}; path=/; max-age=2592000`;
                    window.location.href = '/buyers/search';
                } else {
                    const error = await response.json();
                    showError('loginError', error.detail || 'Login failed');
                }
            } catch (err) {
                showError('loginError', 'Error: ' + err.message);
            }
        });
        
        // Signup form
        document.getElementById('signupForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const first_name = document.getElementById('firstName').value;
            const email = document.getElementById('signupEmail').value;
            const password = document.getElementById('signupPassword').value;
            
            if (password.length < 8) {
                showError('signupError', 'Password must be at least 8 characters');
                return;
            }
            
            try {
                const response = await fetch('/buyers/auth/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password, first_name })
                });
                
                if (response.ok) {
                    const data = await response.json();
                    document.cookie = `token=${data.token}; path=/; max-age=2592000`;
                    window.location.href = '/buyers/search';
                } else {
                    const error = await response.json();
                    showError('signupError', error.detail || 'Signup failed');
                }
            } catch (err) {
                showError('signupError', 'Error: ' + err.message);
            }
        });
        
        function showError(id, msg) {
            document.getElementById(id).textContent = msg;
            document.getElementById(id).style.display = 'block';
        }
    </script>
</body>
</html>"""

BUYER_SEARCH_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Find Rooms - BookWithClaw</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }
        
        .header { background: white; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .header-top { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 24px; font-weight: 700; color: #667eea; }
        .logout { cursor: pointer; color: #667eea; text-decoration: none; }
        
        .search-bar { background: white; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .search-container { max-width: 1200px; margin: 0 auto; display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; align-items: end; }
        .search-group { display: flex; flex-direction: column; }
        .search-group label { font-size: 12px; font-weight: 600; color: #666; margin-bottom: 5px; text-transform: uppercase; }
        .search-group input { padding: 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; }
        .search-group button { padding: 12px; background: #667eea; color: white; border: none; border-radius: 6px; font-weight: 600; cursor: pointer; }
        .search-group button:hover { background: #5568d3; }
        
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .results-header { margin-bottom: 20px; }
        .results-header h2 { font-size: 24px; color: #333; margin-bottom: 5px; }
        .results-header p { color: #999; font-size: 14px; }
        
        .room-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
        .room-card { background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); cursor: pointer; transition: transform 0.2s; }
        .room-card:hover { transform: translateY(-4px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
        
        .room-image { width: 100%; height: 200px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: flex; align-items: center; justify-content: center; font-size: 48px; }
        .room-info { padding: 15px; }
        .hotel-name { font-size: 14px; color: #999; margin-bottom: 5px; }
        .room-type { font-size: 16px; font-weight: 600; color: #333; margin-bottom: 10px; }
        .room-details { display: flex; justify-content: space-between; font-size: 13px; color: #666; margin-bottom: 10px; }
        .price-row { display: flex; justify-content: space-between; align-items: center; }
        .price { font-size: 18px; font-weight: 700; color: #667eea; }
        .rating { font-size: 13px; color: #999; }
        .cta-button { width: 100%; padding: 10px; background: #667eea; color: white; border: none; border-radius: 4px; font-size: 13px; font-weight: 600; cursor: pointer; margin-top: 10px; }
        .cta-button:hover { background: #5568d3; }
        
        @media (max-width: 768px) {
            .search-container { grid-template-columns: 1fr; }
            .room-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-top">
            <div class="logo">📍 BookWithClaw</div>
            <div>
                <span id="userName" style="margin-right: 20px; color: #333;"></span>
                <a href="#" onclick="logout()" class="logout">Logout</a>
            </div>
        </div>
    </div>
    
    <div class="search-bar">
        <div class="search-container">
            <div class="search-group">
                <label>Check In</label>
                <input type="date" id="checkin" value="2026-03-25">
            </div>
            <div class="search-group">
                <label>Check Out</label>
                <input type="date" id="checkout" value="2026-03-27">
            </div>
            <div class="search-group">
                <label>Location</label>
                <input type="text" id="location" placeholder="City or hotel name" value="San Francisco">
            </div>
            <div class="search-group">
                <button onclick="searchRooms()">Search</button>
            </div>
        </div>
    </div>
    
    <div class="container">
        <div class="results-header">
            <h2 id="resultsTitle">Available Rooms</h2>
            <p id="resultsDesc">Showing results for your dates</p>
        </div>
        
        <div class="room-grid" id="roomGrid">
            <!-- Rooms will be loaded here -->
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
        
        function logout() {
            document.cookie = 'token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 UTC';
            window.location.href = '/buyers';
        }
        
        async function searchRooms() {
            const checkin = document.getElementById('checkin').value;
            const checkout = document.getElementById('checkout').value;
            const location = document.getElementById('location').value;
            
            try {
                const res = await fetch(\`/buyers/search?checkin=\${checkin}&checkout=\${checkout}&location=\${location}\`);
                const data = await res.json();
                renderRooms(data.results);
            } catch (err) {
                console.error('Search error:', err);
            }
        }
        
        function renderRooms(rooms) {
            const grid = document.getElementById('roomGrid');
            grid.innerHTML = '';
            
            rooms.forEach(room => {
                const card = document.createElement('div');
                card.className = 'room-card';
                card.onclick = () => viewRoom(room.room_id);
                card.innerHTML = \`
                    <div class="room-image">🏨</div>
                    <div class="room-info">
                        <div class="hotel-name">\${room.hotel_name}</div>
                        <div class="room-type">\${room.room_type}</div>
                        <div class="room-details">
                            <span>\${room.capacity} guests</span>
                            <span>⭐ \${room.rating}</span>
                        </div>
                        <div class="price-row">
                            <div>
                                <div style="font-size: 12px; color: #999;">from</div>
                                <div class="price">$\${room.base_price}</div>
                            </div>
                            <div class="rating">
                                \${room.reviews} reviews
                            </div>
                        </div>
                        <button class="cta-button" onclick="viewRoom(event, '\${room.room_id}')">View & Book</button>
                    </div>
                \`;
                grid.appendChild(card);
            });
        }
        
        function viewRoom(e, roomId) {
            if (e && e.stopPropagation) e.stopPropagation();
            window.location.href = \`/buyers/room/\${roomId}\`;
        }
        
        // Load initial search on page load
        authToken = getToken();
        if (!authToken) {
            window.location.href = '/buyers';
        } else {
            document.getElementById('userName').textContent = 'Traveler';
            searchRooms();
        }
    </script>
</body>
</html>"""


@router.get("/", response_class=HTMLResponse)
async def buyer_login():
    """Buyer login/signup page."""
    return BUYER_LOGIN_HTML


@router.get("/search", response_class=HTMLResponse)
async def buyer_search():
    """Room search interface."""
    return BUYER_SEARCH_HTML
