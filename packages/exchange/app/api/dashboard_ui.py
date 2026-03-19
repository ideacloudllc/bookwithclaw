"""
Seller Dashboard UI - Serve the frontend HTML and login
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/sellers", tags=["dashboard-ui"])

LOGIN_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BookWithClaw - Seller Login</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        .login-container { background: white; border-radius: 8px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); width: 100%; max-width: 400px; padding: 40px; }
        .logo { font-size: 28px; font-weight: 700; color: #667eea; margin-bottom: 30px; text-align: center; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; font-weight: 500; color: #333; }
        input { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; }
        input:focus { outline: none; border-color: #667eea; box-shadow: 0 0 0 3px rgba(102,126,234,0.1); }
        button { width: 100%; padding: 12px; background: #667eea; color: white; border: none; border-radius: 4px; font-size: 16px; font-weight: 600; cursor: pointer; }
        button:hover { background: #5568d3; }
        .register-link { text-align: center; margin-top: 20px; font-size: 14px; }
        .register-link a { color: #667eea; text-decoration: none; }
        .error { color: #e74c3c; font-size: 14px; margin-top: 10px; display: none; }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">📍 BookWithClaw</div>
        <h2 style="margin-bottom: 10px; color: #333;">Seller Dashboard</h2>
        <p style="color: #666; margin-bottom: 30px; font-size: 14px;">Manage your rooms and bookings</p>
        
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
            
            // For MVP: simple auth (in production: validate with backend)
            // Just store in localStorage and redirect
            if (email && password.length >= 4) {
                const agentId = 'seller_' + Math.random().toString(36).substr(2, 8);
                localStorage.setItem('agentId', agentId);
                localStorage.setItem('email', email);
                window.location.href = '/sellers/portal';
            } else {
                document.getElementById('error').textContent = 'Invalid email or password';
                document.getElementById('error').style.display = 'block';
            }
        });
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
        .sidebar { background: #1a1a2e; color: white; padding: 20px; overflow-y: auto; }
        .logo { font-size: 24px; font-weight: 700; color: #667eea; margin-bottom: 30px; }
        .nav { list-style: none; }
        .nav li { margin-bottom: 10px; }
        .nav a { color: #999; text-decoration: none; padding: 12px; display: block; border-radius: 4px; cursor: pointer; }
        .nav a:hover, .nav a.active { color: white; background: #667eea; }
        
        /* Main */
        .main { padding: 30px; }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
        .header h1 { color: #1a1a2e; }
        .logout-btn { padding: 8px 16px; background: #e74c3c; color: white; border: none; border-radius: 4px; cursor: pointer; }
        
        /* Content sections */
        .section { display: none; }
        .section.active { display: block; }
        
        /* Stats grid */
        .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .stat-value { font-size: 32px; font-weight: 700; color: #667eea; }
        .stat-label { font-size: 14px; color: #999; margin-top: 5px; }
        
        /* Tables */
        table { width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        th { background: #f9f9f9; padding: 15px; text-align: left; font-weight: 600; border-bottom: 1px solid #eee; }
        td { padding: 15px; border-bottom: 1px solid #eee; }
        tr:hover { background: #f9f9f9; }
        
        /* Badges */
        .badge { display: inline-block; padding: 4px 8px; border-radius: 3px; font-size: 12px; font-weight: 600; }
        .badge-success { background: #d4edda; color: #155724; }
        .badge-warning { background: #fff3cd; color: #856404; }
        .badge-danger { background: #f8d7da; color: #721c24; }
        
        /* Buttons */
        .btn { padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; margin-right: 10px; }
        .btn-primary { background: #667eea; color: white; }
        .btn-primary:hover { background: #5568d3; }
        .btn-secondary { background: #ddd; color: #333; }
        .btn-success { background: #28a745; color: white; }
        .btn-danger { background: #dc3545; color: white; }
        
        /* Forms */
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 5px; font-weight: 500; }
        input, textarea, select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; }
        input:focus { outline: none; border-color: #667eea; }
        
        /* Modal */
        .modal { display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); justify-content: center; align-items: center; z-index: 1000; }
        .modal.active { display: flex; }
        .modal-content { background: white; padding: 30px; border-radius: 8px; width: 100%; max-width: 500px; }
        .modal-close { float: right; font-size: 24px; cursor: pointer; }
        
        @media (max-width: 1024px) {
            .stats { grid-template-columns: repeat(2, 1fr); }
        }
        
        @media (max-width: 768px) {
            .container { grid-template-columns: 1fr; }
            .sidebar { display: none; }
            .stats { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Sidebar -->
        <div class="sidebar">
            <div class="logo">📍 BWC</div>
            <ul class="nav">
                <li><a onclick="showSection('dashboard')" class="nav-link active">📊 Dashboard</a></li>
                <li><a onclick="showSection('rooms')" class="nav-link">🏠 Rooms</a></li>
                <li><a onclick="showSection('offers')" class="nav-link">📬 Offers</a></li>
                <li><a onclick="showSection('bookings')" class="nav-link">📅 Bookings</a></li>
                <li><a onclick="showSection('pricing')" class="nav-link">💰 Pricing</a></li>
                <li><a onclick="showSection('profile')" class="nav-link">👤 Profile</a></li>
            </ul>
        </div>
        
        <!-- Main Content -->
        <div class="main">
            <div class="header">
                <h1>Seller Dashboard</h1>
                <button class="logout-btn" onclick="logout()">Logout</button>
            </div>
            
            <!-- Dashboard Section -->
            <div id="dashboard" class="section active">
                <h2>Welcome Back!</h2>
                <p style="color: #666; margin-bottom: 30px;">Here's your hotel performance at a glance.</p>
                
                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-value">3</div>
                        <div class="stat-label">Active Listings</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">2</div>
                        <div class="stat-label">Pending Offers</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">5</div>
                        <div class="stat-label">Total Bookings</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">$1,750</div>
                        <div class="stat-label">Total Revenue</div>
                    </div>
                </div>
                
                <h3 style="margin-top: 40px; margin-bottom: 20px;">Recent Offers</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Guest</th>
                            <th>Room Type</th>
                            <th>Dates</th>
                            <th>Offered Price</th>
                            <th>Status</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>John Traveler</td>
                            <td>Deluxe King</td>
                            <td>Mar 22-24</td>
                            <td>$320</td>
                            <td><span class="badge badge-warning">Pending</span></td>
                            <td>
                                <button class="btn btn-success btn-sm" onclick="acceptOffer('off_001')">Accept</button>
                                <button class="btn btn-danger btn-sm" onclick="declineOffer('off_001')">Decline</button>
                            </td>
                        </tr>
                        <tr>
                            <td>Jane Smith ⭐5.0</td>
                            <td>Standard Queen</td>
                            <td>Mar 25-27</td>
                            <td>$280</td>
                            <td><span class="badge badge-warning">Pending</span></td>
                            <td>
                                <button class="btn btn-success btn-sm" onclick="acceptOffer('off_002')">Accept</button>
                                <button class="btn btn-danger btn-sm" onclick="declineOffer('off_002')">Decline</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
            
            <!-- Rooms Section -->
            <div id="rooms" class="section">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                    <h2>Your Rooms</h2>
                    <button class="btn btn-primary" onclick="showModal('addRoomModal')">+ Add Room</button>
                </div>
                
                <table>
                    <thead>
                        <tr>
                            <th>Room Name</th>
                            <th>Capacity</th>
                            <th>Base Rate</th>
                            <th>Floor Price</th>
                            <th>Bookings</th>
                            <th>Status</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Deluxe King</td>
                            <td>2 guests</td>
                            <td>$350</td>
                            <td>$280</td>
                            <td>2</td>
                            <td><span class="badge badge-success">Active</span></td>
                            <td><button class="btn btn-primary btn-sm" onclick="editRoom('rm_1')">Edit</button></td>
                        </tr>
                        <tr>
                            <td>Standard Queen</td>
                            <td>2 guests</td>
                            <td>$250</td>
                            <td>$200</td>
                            <td>1</td>
                            <td><span class="badge badge-success">Active</span></td>
                            <td><button class="btn btn-primary btn-sm" onclick="editRoom('rm_2')">Edit</button></td>
                        </tr>
                        <tr>
                            <td>Suite</td>
                            <td>4 guests</td>
                            <td>$500</td>
                            <td>$400</td>
                            <td>3</td>
                            <td><span class="badge badge-success">Active</span></td>
                            <td><button class="btn btn-primary btn-sm" onclick="editRoom('rm_3')">Edit</button></td>
                        </tr>
                    </tbody>
                </table>
            </div>
            
            <!-- Offers Section -->
            <div id="offers" class="section">
                <h2>Incoming Offers</h2>
                <p style="color: #666; margin-bottom: 20px;">Review and respond to buyer intents.</p>
                
                <table>
                    <thead>
                        <tr>
                            <th>Guest</th>
                            <th>Room</th>
                            <th>Check-in</th>
                            <th>Check-out</th>
                            <th>Your Rate</th>
                            <th>Offered Price</th>
                            <th>Expires</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>John Traveler 🆕</td>
                            <td>Deluxe King</td>
                            <td>Mar 22</td>
                            <td>Mar 24</td>
                            <td>$350</td>
                            <td>$320</td>
                            <td>24h</td>
                            <td>
                                <button class="btn btn-success btn-sm" onclick="acceptOffer('off_001')">✓</button>
                                <button class="btn btn-danger btn-sm" onclick="declineOffer('off_001')">✗</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
            
            <!-- Bookings Section -->
            <div id="bookings" class="section">
                <h2>Your Bookings</h2>
                <p style="color: #666; margin-bottom: 20px;">Confirmed reservations and completed stays.</p>
                
                <table>
                    <thead>
                        <tr>
                            <th>Guest</th>
                            <th>Room</th>
                            <th>Check-in</th>
                            <th>Check-out</th>
                            <th>Price</th>
                            <th>Your Earnings</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Robert Johnson</td>
                            <td>Suite</td>
                            <td>Mar 20</td>
                            <td>Mar 22</td>
                            <td>$450</td>
                            <td>$441.90</td>
                            <td><span class="badge badge-success">Confirmed</span></td>
                        </tr>
                        <tr>
                            <td>Alice Wonder ⭐5.0</td>
                            <td>Deluxe King</td>
                            <td>Mar 15</td>
                            <td>Mar 17</td>
                            <td>$400</td>
                            <td>$392.80</td>
                            <td><span class="badge badge-success">Completed</span></td>
                        </tr>
                    </tbody>
                </table>
            </div>
            
            <!-- Pricing Section -->
            <div id="pricing" class="section">
                <h2>Pricing Management</h2>
                <p style="color: #666; margin-bottom: 30px;">Set rates and floor prices for your rooms.</p>
                
                <div style="background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    <h3>Deluxe King</h3>
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-top: 15px;">
                        <div class="form-group">
                            <label>Base Rate</label>
                            <input type="number" value="350" />
                        </div>
                        <div class="form-group">
                            <label>Floor Price</label>
                            <input type="number" value="280" />
                        </div>
                        <div class="form-group">
                            <label style="opacity: 0;">Action</label>
                            <button class="btn btn-primary" style="width: 100%;">Save</button>
                        </div>
                    </div>
                </div>
                
                <p style="background: #e8f4f8; padding: 15px; border-radius: 4px; margin-top: 20px;">
                    💡 <strong>Tip:</strong> Set your floor price to your break-even point. We won't show offers below this price.
                </p>
            </div>
            
            <!-- Profile Section -->
            <div id="profile" class="section">
                <h2>Hotel Profile</h2>
                
                <div style="background: white; padding: 30px; border-radius: 8px; max-width: 600px;">
                    <div class="form-group">
                        <label>Hotel Name</label>
                        <input type="text" value="Your Hotel Name" />
                    </div>
                    <div class="form-group">
                        <label>Email</label>
                        <input type="email" value="hotel@example.com" />
                    </div>
                    <div class="form-group">
                        <label>Phone</label>
                        <input type="tel" value="+1-555-0000" />
                    </div>
                    <div class="form-group">
                        <label>Location</label>
                        <input type="text" value="San Francisco, CA" />
                    </div>
                    <div class="form-group">
                        <label>Description</label>
                        <textarea rows="4">Beautiful 3-star hotel in downtown</textarea>
                    </div>
                    <div class="form-group">
                        <label>Check-in Time</label>
                        <input type="time" value="15:00" />
                    </div>
                    <div class="form-group">
                        <label>Check-out Time</label>
                        <input type="time" value="11:00" />
                    </div>
                    <button class="btn btn-primary" onclick="saveProfile()">Save Changes</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Check if logged in
        if (!localStorage.getItem('agentId')) {
            window.location.href = '/sellers/login';
        }
        
        function showSection(sectionId) {
            // Hide all sections
            document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
            // Show selected section
            document.getElementById(sectionId).classList.add('active');
            // Update nav
            document.querySelectorAll('.nav-link').forEach(a => a.classList.remove('active'));
            event.target.classList.add('active');
        }
        
        function showModal(modalId) {
            document.getElementById(modalId).classList.add('active');
        }
        
        function acceptOffer(offerId) {
            alert('Offer ' + offerId + ' accepted!\\n\\nGuest will receive confirmation. Prepare your room!');
        }
        
        function declineOffer(offerId) {
            alert('Offer ' + offerId + ' declined.');
        }
        
        function editRoom(roomId) {
            alert('Edit room: ' + roomId);
        }
        
        function saveProfile() {
            alert('Profile updated!');
        }
        
        function logout() {
            localStorage.removeItem('agentId');
            localStorage.removeItem('email');
            window.location.href = '/sellers/login';
        }
    </script>
</body>
</html>"""


@router.get("/login", response_class=HTMLResponse)
async def login_page():
    """Serve login page"""
    return LOGIN_HTML


@router.get("/portal", response_class=HTMLResponse)
async def dashboard_page():
    """Serve seller dashboard portal"""
    return DASHBOARD_HTML
