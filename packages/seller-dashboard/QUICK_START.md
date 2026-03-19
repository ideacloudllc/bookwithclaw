# Seller Dashboard - Quick Start Guide

## 🚀 Start Development Server

```bash
cd packages/seller-dashboard
npm install  # One-time setup
npm run dev
```

Open: http://localhost:5173

---

## 🔐 Test Signup & Login

### Signup Page
- **URL**: http://localhost:5173/sellers
- **Fields**:
  - Hotel Name: "My Hotel"
  - Email: "seller@example.com"
  - Password: "password123" (8+ chars)
  - Confirm: "password123"
- **Test Case**: Enter valid data → Click Sign Up → Should redirect to dashboard
- **Error Test**: Try empty fields or mismatched passwords

### Login Page
- **URL**: http://localhost:5173/sellers/login
- **Fields**:
  - Email: "seller@example.com"
  - Password: "password123"
- **Test Case**: Enter credentials → Click Sign In → Should redirect to dashboard
- **Error Test**: Try invalid email format or short password

---

## 📊 Test Dashboard Features

### Dashboard Tab (Overview)
- Stat cards with icons showing:
  - Active Listings (🏠)
  - Pending Offers (💼)
  - This Month Revenue (💰)
  - Occupancy Rate (📊)
- Quick action buttons to navigate to other tabs
- Recent bookings section with sample data

### Inventory Tab (Room Management)
- **Add Room**:
  1. Click "Add Room" button
  2. Fill form:
     - Room Name: "Deluxe Double"
     - Type: "Deluxe"
     - Base Price: "150.00"
     - Floor Price: "100.00"
     - Max Occupancy: "2"
  3. Click "Save"
  4. Check for error if floor price > base price

- **View Rooms**: Grid view with edit/delete buttons
- **Edit Room**: Click edit button, modify, save
- **Delete Room**: Click delete, confirm, room removed

### Offers Tab (Buyer Intents)
- View incoming offers with:
  - Guest budget ($)
  - Check-in/check-out dates
  - Number of guests
  - Current status badge
- **Counter Offer**:
  1. Click "Counter Offer" button
  2. Enter your price
  3. Click "Submit Counter"
- **Accept**: Click to accept offer

### Bookings Tab (Reservations)
- Table view of confirmed bookings
- Columns: Guest Name | Room | Check-in | Check-out | Rate | Status
- Scroll horizontally on mobile

### Pricing Tab (Rate Management)
- View all rooms with 3-tier pricing:
  - Base Price (standard rate)
  - Floor Price (minimum acceptable)
  - Ceiling Price (maximum during peak)
- **Edit Pricing**:
  1. Click "Edit Pricing"
  2. Modify prices
  3. Click "Save Changes"
- Helpful tips section with strategy guide

### Profile Tab (Hotel Settings)
- **Edit Hotel Info**:
  - Hotel Name
  - Address
  - Phone Number
  - Check-in Time (picker)
  - Check-out Time (picker)
- **Sidebar Cards**:
  - Email (read-only)
  - Stripe Connect Status
  - Account Statistics

---

## 🧪 Form Validation Tests

### Email Validation
- Invalid: "test" → Error: "Invalid email format"
- Invalid: "test@" → Error
- Valid: "user@example.com" → No error

### Password Validation
- Too short: "pass" → Error: "Password must be at least 8 characters"
- Valid: "password123" → No error

### Price Validation
- Floor > Base → Error: "Floor price must be less than base price"
- Valid Floor ≤ Base → No error

### Required Fields
- Leave hotel name empty → Error when submitting form
- Leave address empty → Error in profile tab

---

## 📱 Test Responsive Design

### Desktop (1024px+)
- Sidebar visible on left
- Content takes full width right of sidebar
- 3-column grid for inventory
- Full table width for bookings

### Tablet (768px - 1023px)
- Sidebar visible (narrower)
- 2-column grid for inventory
- Table scrollable horizontally

### Mobile (320px - 767px)
- Sidebar collapses (← → toggle button)
- 1-column grid for inventory
- Stacked form fields
- Full-width buttons
- No horizontal scroll

---

## 🔄 Test Authentication Flow

### Cookie Storage
1. Sign up with email "test@example.com"
2. Open DevTools → Application → Cookies
3. Should see `seller_token` cookie with token value
4. Token should expire in 30 days

### Protected Routes
1. Try accessing `/sellers/portal` without login
2. Should redirect to `/sellers/login`
3. Log in successfully
4. Should be able to access portal

### Logout
1. Click logout button (door icon)
2. Cookie should be cleared
3. Should redirect to login page
4. Try accessing portal → redirects to login

---

## 🐛 Debugging

### Console
- Press F12 → Console tab
- Should see NO errors or warnings
- Network tab shows API calls with proper headers

### Network Requests
1. Open DevTools → Network tab
2. Try signup/login
3. Check request headers:
   - Protected endpoints should have: `Authorization: Bearer <token>`
4. Check response:
   - 200-201: Success
   - 400: Validation error
   - 401: Unauthorized
   - 500: Server error

---

## 🔌 Backend Integration Setup

### Mock API for Development
If backend is not running, you'll see network errors. To test:

1. **Option A**: Start FastAPI backend
   ```bash
   cd backend/
   python main.py  # Runs on http://localhost:8000
   ```

2. **Option B**: Mock responses in browser
   ```javascript
   // In DevTools Console
   // Add mock interceptor (advanced)
   ```

### API Base URL
Default: `/api` (proxies to `http://localhost:8000`)

To change:
```bash
VITE_API_BASE=https://api.example.com npm run dev
```

---

## ✅ Acceptance Criteria Checklist

- [ ] Signup page renders with hero section
- [ ] Login page renders correctly
- [ ] Email validation works
- [ ] Password validation works (8+ chars)
- [ ] Token stored in cookie after signup
- [ ] Protected route redirects when not logged in
- [ ] Dashboard tab shows 4 stat cards
- [ ] Inventory tab shows room grid
- [ ] Can add/edit/delete rooms
- [ ] Offers tab shows offers with counter button
- [ ] Bookings tab shows table of reservations
- [ ] Pricing tab allows editing room rates
- [ ] Profile tab allows updating hotel info
- [ ] Logout clears cookie and redirects
- [ ] Sidebar collapses on mobile
- [ ] No horizontal scroll on mobile
- [ ] Forms show validation errors
- [ ] Loading states display on buttons
- [ ] No console errors or warnings
- [ ] Bundle builds successfully (<3s)

---

## 📚 File Locations

```
Key Files:
- Signup: src/pages/Signup.tsx
- Login: src/pages/Login.tsx
- Dashboard: src/pages/Dashboard.tsx
- Auth Hook: src/hooks/useAuth.ts
- API Client: src/utils/api.ts
- Auth Helpers: src/utils/auth.ts
- Types: src/types/index.ts
```

---

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| `npm install` fails | Delete `node_modules`, run `npm cache clean --force`, retry |
| Port 5173 in use | `lsof -i :5173` to find process, kill it, or change port in vite.config.ts |
| Module not found | Check import paths, ensure TypeScript types are defined |
| API calls fail | Ensure backend is running on `http://localhost:8000` |
| Styles not loading | Check Tailwind CSS is built, clear browser cache |
| Cookie not storing | Check browser allows cookies, not in private mode |

---

## 🎯 Next Steps

1. **Start Dev Server**: `npm run dev`
2. **Test Signup**: Create account at `/sellers`
3. **Explore Dashboard**: Navigate tabs to see features
4. **Test Forms**: Add rooms, edit pricing, submit offers
5. **Check Mobile**: Resize window or use device emulation
6. **Build for Production**: `npm run build` → deploy `dist/`

---

**Ready?** Start the dev server and begin testing! 🚀
