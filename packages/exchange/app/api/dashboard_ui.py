"""
Seller Dashboard UI - Serves the frontend HTML
"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["dashboard-ui"])

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BookWithClaw Seller Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: #f5f5f5;
            color: #222;
        }

        .container {
            display: grid;
            grid-template-columns: 250px 1fr;
            height: 100vh;
        }

        /* Sidebar */
        .sidebar {
            background: #1a1a2e;
            color: white;
            padding: 20px;
            overflow-y: auto;
        }

        .logo {
            font-size: 1.3rem;
            font-weight: 700;
            margin-bottom: 30px;
            color: #ff6b35;
        }

        .nav-section {
            margin-bottom: 30px;
        }

        .nav-section h3 {
            font-size: 0.75rem;
            text-transform: uppercase;
            color: #888;
            margin-bottom: 10px;
        }

        .nav-link {
            display: block;
            padding: 10px 15px;
            margin-bottom: 5px;
            border-radius: 5px;
            cursor: pointer;
            transition: background 0.3s;
            color: white;
            text-decoration: none;
        }

        .nav-link:hover,
        .nav-link.active {
            background: #ff6b35;
        }

        /* Main content */
        .main {
            overflow-y: auto;
            padding: 30px;
        }

        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        h1 {
            font-size: 2rem;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }

        .stat-number {
            font-size: 2rem;
            font-weight: 700;
            color: #ff6b35;
            margin-bottom: 5px;
        }

        .stat-label {
            font-size: 0.9rem;
            color: #666;
        }

        .content-section {
            display: none;
        }

        .content-section.active {
            display: block;
        }

        .rooms-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .room-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .room-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }

        .room-name {
            font-size: 1.2rem;
            font-weight: 600;
        }

        .room-status {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 0.8rem;
            background: #e8f5e9;
            color: #388e3c;
        }

        .room-details {
            margin: 15px 0;
            font-size: 0.95rem;
            color: #666;
        }

        .room-details div {
            margin-bottom: 8px;
        }

        .room-rates {
            background: #f5f5f5;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
        }

        .room-rate {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
        }

        .rate-label {
            color: #666;
        }

        .rate-value {
            font-weight: 600;
            color: #ff6b35;
        }

        .button {
            display: inline-block;
            padding: 10px 20px;
            margin-top: 15px;
            background: #ff6b35;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: 600;
            transition: background 0.3s;
            text-decoration: none;
        }

        .button:hover {
            background: #e55a2b;
        }

        .button.secondary {
            background: #1a1a2e;
        }

        .button.secondary:hover {
            background: #000;
        }

        .offers-table {
            width: 100%;
            background: white;
            border-collapse: collapse;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .offers-table thead {
            background: #f5f5f5;
            font-weight: 600;
        }

        .offers-table th,
        .offers-table td {
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }

        .offers-table tbody tr:last-child td {
            border-bottom: none;
        }

        .offers-table tbody tr:hover {
            background: #f9f9f9;
        }

        .offer-status {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 0.8rem;
        }

        .status-negotiating {
            background: #fff3cd;
            color: #856404;
        }

        .status-accepted {
            background: #d4edda;
            color: #155724;
        }

        .empty-state {
            text-align: center;
            padding: 40px 20px;
            color: #999;
        }

        .empty-state p {
            margin-bottom: 20px;
        }

        .form-group {
            margin-bottom: 20px;
        }

        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
        }

        .form-group input {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 1rem;
        }

        @media (max-width: 768px) {
            .container {
                grid-template-columns: 1fr;
            }

            .sidebar {
                display: none;
            }

            .stats-grid {
                grid-template-columns: repeat(2, 1fr);
            }

            .rooms-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="sidebar">
            <div class="logo">🐚 BookWithClaw</div>
            
            <div class="nav-section">
                <h3>Menu</h3>
                <a class="nav-link active" onclick="showSection('dashboard')">📊 Dashboard</a>
                <a class="nav-link" onclick="showSection('rooms')">🏨 Rooms</a>
                <a class="nav-link" onclick="showSection('offers')">💰 Offers</a>
                <a class="nav-link" onclick="showSection('bookings')">📅 Bookings</a>
                <a class="nav-link" onclick="showSection('payouts')">💳 Payouts</a>
            </div>

            <div class="nav-section">
                <h3>Account</h3>
                <a class="nav-link" onclick="showSection('profile')">⚙️ Profile</a>
                <a class="nav-link" onclick="logout()">🚪 Logout</a>
            </div>
        </div>

        <div class="main">
            <!-- Dashboard Section -->
            <div id="dashboard" class="content-section active">
                <div class="header">
                    <h1>Dashboard</h1>
                    <span id="hotel-name" style="color: #666;"></span>
                </div>

                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number" id="stat-rooms">0</div>
                        <div class="stat-label">Active Listings</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="stat-offers">0</div>
                        <div class="stat-label">Pending Offers</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="stat-bookings">0</div>
                        <div class="stat-label">Completed Bookings</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="stat-revenue">$0</div>
                        <div class="stat-label">Total Revenue</div>
                    </div>
                </div>

                <h2>Recent Offers</h2>
                <div id="recent-offers"></div>
            </div>

            <!-- Rooms Section -->
            <div id="rooms" class="content-section">
                <div class="header">
                    <h1>My Rooms</h1>
                    <button class="button" onclick="showAddRoomForm()">+ Add Room</button>
                </div>

                <div id="add-room-form" style="display: none; background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    <h3>Add New Room</h3>
                    <div class="form-group">
                        <label>Room Name</label>
                        <input type="text" id="room-name" placeholder="e.g., Deluxe King">
                    </div>
                    <div class="form-group">
                        <label>Capacity (Guests)</label>
                        <input type="number" id="room-capacity" placeholder="2" min="1">
                    </div>
                    <div class="form-group">
                        <label>Base Rate (per night)</label>
                        <input type="number" id="room-rate" placeholder="350" min="0">
                    </div>
                    <div class="form-group">
                        <label>Floor Price (minimum)</label>
                        <input type="number" id="room-floor" placeholder="250" min="0">
                    </div>
                    <button class="button" onclick="createRoom()">Create Room</button>
                    <button class="button secondary" onclick="hideAddRoomForm()">Cancel</button>
                </div>

                <div class="rooms-grid" id="rooms-list"></div>
            </div>

            <!-- Offers Section -->
            <div id="offers" class="content-section">
                <div class="header">
                    <h1>Active Offers</h1>
                </div>

                <table class="offers-table">
                    <thead>
                        <tr>
                            <th>Room</th>
                            <th>Dates</th>
                            <th>Proposed Price</th>
                            <th>Your Base</th>
                            <th>Status</th>
                            <th>Round</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="offers-list">
                        <tr>
                            <td colspan="7" class="empty-state">No active offers yet</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- Bookings Section -->
            <div id="bookings" class="content-section">
                <div class="header">
                    <h1>Completed Bookings</h1>
                </div>
                <div id="bookings-list" class="empty-state">
                    <p>No completed bookings yet</p>
                </div>
            </div>

            <!-- Payouts Section -->
            <div id="payouts" class="content-section">
                <div class="header">
                    <h1>Payouts</h1>
                </div>
                <div id="payouts-list" class="empty-state">
                    <p>No payouts yet</p>
                </div>
            </div>

            <!-- Profile Section -->
            <div id="profile" class="content-section">
                <div class="header">
                    <h1>Hotel Profile</h1>
                </div>
                <div style="background: white; padding: 20px; border-radius: 8px; max-width: 500px;">
                    <div class="form-group">
                        <label>Hotel Name</label>
                        <input type="text" id="hotel-name-input" placeholder="My Hotel">
                    </div>
                    <div class="form-group">
                        <label>Email</label>
                        <input type="email" id="hotel-email" placeholder="hotel@example.com">
                    </div>
                    <div class="form-group">
                        <label>Location</label>
                        <input type="text" id="hotel-location" placeholder="City, State">
                    </div>
                    <button class="button" onclick="updateProfile()">Save Changes</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        const API_BASE = window.location.origin;
        let authToken = localStorage.getItem('authToken');

        if (!authToken) {
            window.location.href = '/sellers';
        }

        function showSection(section) {
            document.querySelectorAll('.content-section').forEach(el => el.classList.remove('active'));
            document.getElementById(section).classList.add('active');
            
            document.querySelectorAll('.nav-link').forEach(el => el.classList.remove('active'));
            event.target.classList.add('active');

            if (section === 'dashboard') loadDashboard();
            if (section === 'rooms') loadRooms();
            if (section === 'offers') loadOffers();
        }

        async function loadDashboard() {
            try {
                const response = await fetch(`${API_BASE}/sellers/dashboard`, {
                    headers: { 'Authorization': `Bearer ${authToken}` }
                });
                const data = await response.json();

                document.getElementById('hotel-name').textContent = data.profile.name;
                document.getElementById('stat-rooms').textContent = data.stats.active_listings;
                document.getElementById('stat-offers').textContent = data.stats.pending_offers;
                document.getElementById('stat-bookings').textContent = data.stats.completed_bookings;
                document.getElementById('stat-revenue').textContent = `$${data.stats.total_revenue}`;

                const offersHTML = data.recent_offers.length > 0 
                    ? data.recent_offers.map(o => `<div style="background: white; padding: 15px; border-radius: 5px; margin-bottom: 10px;">
                        <strong>${o.room_name}</strong> - ${o.proposed_price} (${o.status})
                      </div>`).join('')
                    : '<p style="color: #999;">No recent offers</p>';
                document.getElementById('recent-offers').innerHTML = offersHTML;
            } catch (error) {
                console.error('Error loading dashboard:', error);
            }
        }

        async function loadRooms() {
            try {
                const response = await fetch(`${API_BASE}/sellers/rooms`, {
                    headers: { 'Authorization': `Bearer ${authToken}` }
                });
                const rooms = await response.json();

                const html = rooms.map(room => `
                    <div class="room-card">
                        <div class="room-header">
                            <div class="room-name">${room.name}</div>
                            <span class="room-status">${room.status}</span>
                        </div>
                        <div class="room-details">
                            <div>👥 Capacity: ${room.capacity} guests</div>
                            <div>👁️ Views: ${room.views}</div>
                            <div>💬 Inquiries: ${room.inquiries}</div>
                        </div>
                        <div class="room-rates">
                            <div class="room-rate">
                                <span class="rate-label">Base Rate:</span>
                                <span class="rate-value">$${room.base_rate}</span>
                            </div>
                            <div class="room-rate">
                                <span class="rate-label">Floor Price:</span>
                                <span class="rate-value">$${room.floor_price}</span>
                            </div>
                        </div>
                        <button class="button secondary" onclick="editRoom('${room.room_id}')">Edit</button>
                    </div>
                `).join('');

                document.getElementById('rooms-list').innerHTML = html;
            } catch (error) {
                console.error('Error loading rooms:', error);
            }
        }

        async function loadOffers() {
            try {
                const response = await fetch(`${API_BASE}/sellers/offers`, {
                    headers: { 'Authorization': `Bearer ${authToken}` }
                });
                const offers = await response.json();

                if (offers.length === 0) {
                    document.getElementById('offers-list').innerHTML = '<tr><td colspan="7" class="empty-state">No active offers</td></tr>';
                    return;
                }

                const html = offers.map(offer => `
                    <tr>
                        <td>${offer.room_name}</td>
                        <td>${offer.dates.checkin} → ${offer.dates.checkout}</td>
                        <td>$${offer.proposed_price}</td>
                        <td>$${offer.your_base}</td>
                        <td><span class="offer-status status-${offer.status}">${offer.status}</span></td>
                        <td>${offer.round}</td>
                        <td>
                            <button class="button" onclick="acceptOffer('${offer.offer_id}')">Accept</button>
                            <button class="button secondary" onclick="rejectOffer('${offer.offer_id}')">Reject</button>
                        </td>
                    </tr>
                `).join('');

                document.getElementById('offers-list').innerHTML = html;
            } catch (error) {
                console.error('Error loading offers:', error);
            }
        }

        function showAddRoomForm() {
            document.getElementById('add-room-form').style.display = 'block';
        }

        function hideAddRoomForm() {
            document.getElementById('add-room-form').style.display = 'none';
        }

        async function createRoom() {
            const roomData = {
                name: document.getElementById('room-name').value,
                capacity: parseInt(document.getElementById('room-capacity').value),
                base_rate: parseInt(document.getElementById('room-rate').value),
                floor_price: parseInt(document.getElementById('room-floor').value),
            };

            try {
                const response = await fetch(`${API_BASE}/sellers/rooms`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${authToken}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(roomData)
                });

                if (response.ok) {
                    hideAddRoomForm();
                    loadRooms();
                    alert('Room created successfully!');
                }
            } catch (error) {
                console.error('Error creating room:', error);
                alert('Failed to create room');
            }
        }

        async function acceptOffer(offerId) {
            try {
                const response = await fetch(`${API_BASE}/sellers/offers/${offerId}/accept`, {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${authToken}` }
                });

                if (response.ok) {
                    loadOffers();
                    alert('Offer accepted!');
                }
            } catch (error) {
                console.error('Error accepting offer:', error);
                alert('Failed to accept offer');
            }
        }

        async function rejectOffer(offerId) {
            try {
                const response = await fetch(`${API_BASE}/sellers/offers/${offerId}/reject`, {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${authToken}` }
                });

                if (response.ok) {
                    loadOffers();
                    alert('Offer rejected');
                }
            } catch (error) {
                console.error('Error rejecting offer:', error);
                alert('Failed to reject offer');
            }
        }

        function editRoom(roomId) {
            alert('Edit room: ' + roomId);
        }

        function updateProfile() {
            alert('Profile updated');
        }

        function logout() {
            localStorage.removeItem('authToken');
            window.location.href = '/sellers';
        }

        // Load dashboard on page load
        loadDashboard();
    </script>
</body>
</html>
"""


@router.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard_ui():
    """Serve seller dashboard HTML"""
    return DASHBOARD_HTML
