# BookWithClaw Seller Dashboard

A production-ready React + TypeScript + Tailwind CSS dashboard for hotel sellers to manage inventory, offers, bookings, and earnings on the BookWithClaw platform.

## Features

- ✅ **Authentication**: Signup/Login with cookie-based token storage
- ✅ **Dashboard**: Key metrics and quick action buttons
- ✅ **Inventory Management**: Add, edit, delete rooms with pricing
- ✅ **Offers Tab**: View guest offers and submit counter-offers
- ✅ **Bookings Tab**: View confirmed reservations
- ✅ **Dynamic Pricing**: Manage base, floor, and ceiling prices per room
- ✅ **Profile Management**: Edit hotel information and Stripe Connect status
- ✅ **Mobile Responsive**: Works on 320px+ screens
- ✅ **Tailwind CSS**: Production-ready styling with no custom CSS

## Tech Stack

- **Frontend**: React 18 + TypeScript
- **Build**: Vite 5
- **Styling**: Tailwind CSS 3
- **Routing**: React Router 6
- **HTTP**: Fetch API with cookie-based auth
- **Package Manager**: npm

## Quick Start

### Prerequisites

- Node.js 18+
- npm 9+

### Installation

```bash
cd packages/seller-dashboard
npm install
```

### Development

```bash
npm run dev
```

Opens at `http://localhost:5173`

### Build

```bash
npm run build
```

Outputs to `dist/` directory.

### Preview

```bash
npm run preview
```

## Project Structure

```
src/
├── main.tsx              # Entry point
├── App.tsx              # Main router
├── index.css            # Tailwind imports
├── pages/
│   ├── Signup.tsx       # Signup page with hero section
│   ├── Login.tsx        # Login page
│   └── Dashboard.tsx    # Main portal with tabs
├── components/
│   ├── Layout.tsx       # Sidebar navigation
│   ├── ProtectedRoute.tsx
│   ├── DashboardTab.tsx
│   ├── InventoryTab.tsx
│   ├── OffersTab.tsx
│   ├── BookingsTab.tsx
│   ├── PricingTab.tsx
│   ├── ProfileTab.tsx
│   ├── StatCard.tsx
│   ├── Modal.tsx
│   └── FormInput.tsx
├── hooks/
│   ├── useAuth.ts       # Authentication logic
│   └── useApi.ts        # Data fetching with auth
├── types/
│   └── index.ts         # TypeScript interfaces
└── utils/
    ├── api.ts           # API client
    └── auth.ts          # Auth helpers
```

## API Integration

### Authentication Endpoints

```typescript
POST /api/sellers/auth/register
{
  email: string;
  password: string;
  hotel_name: string;
}
Response: { access_token: string }

POST /api/sellers/auth/login
{
  email: string;
  password: string;
}
Response: { access_token: string }
```

### Protected Endpoints

All protected endpoints require `Authorization: Bearer <token>` header.

```typescript
GET /api/sellers/profile
PUT /api/sellers/profile

GET /api/sellers/rooms
POST /api/sellers/rooms
PUT /api/sellers/rooms/{id}
DELETE /api/sellers/rooms/{id}

GET /api/sellers/offers
POST /api/sellers/offers/{id}/counter
POST /api/sellers/offers/{id}/accept

GET /api/sellers/bookings
```

## Authentication Flow

1. **Signup**: User creates account → Token stored in cookie → Redirects to dashboard
2. **Login**: User enters credentials → Token stored in cookie → Redirects to dashboard
3. **Protected Routes**: Check cookie for token → Send as Bearer token in requests
4. **Logout**: Clear cookie → Redirect to login

## Key Components

### Signup & Login
- Email validation
- Password strength check (8+ chars)
- Error handling and display
- Success redirects to dashboard

### Dashboard Overview
- 4 stat cards (listings, offers, revenue, occupancy)
- Quick action buttons to navigate tabs
- Recent bookings preview

### Inventory Management
- Grid view of all rooms
- Add room modal with form validation
- Edit/delete buttons per room
- Room type selection (standard, deluxe, suite, economy)

### Offers Management
- List all offers with status badges
- Guest budget and dates display
- Counter-offer modal with price input
- Accept/reject buttons

### Bookings List
- Table view with guest name, room, dates, rate
- Status badges
- Sortable columns (future enhancement)

### Dynamic Pricing
- Edit base, floor, and ceiling prices per room
- Save individual room pricing
- Tips and strategy guide

### Profile Management
- Edit hotel name, address, phone
- Check-in/check-out time settings
- Email verification status
- Stripe Connect status
- Account statistics

## Styling

- **Colors**: Tailwind defaults with custom primary (sky/blue) palette
- **Layout**: Sidebar navigation + main content area
- **Responsive**: Mobile-first, full support for sm/md/lg/xl breakpoints
- **Components**: Reusable StatCard, Modal, FormInput, Layout

## Form Validation

- **Email**: Valid format check
- **Password**: Minimum 8 characters
- **Hotel Name**: Required, non-empty
- **Price Fields**: Valid numbers, floor ≤ base
- **Phone**: Required for profile
- **Address**: Required for profile

## Error Handling

- API errors caught and displayed to user
- Form validation errors per field
- Loading states on buttons
- Toast/alert messages for success/failure

## Future Enhancements

- [ ] Photo upload for hotel and rooms
- [ ] Calendar picker for availability
- [ ] Seasonal pricing rules
- [ ] Revenue charts and analytics
- [ ] Message inbox for guest communications
- [ ] Email notifications
- [ ] Two-factor authentication
- [ ] CSV export for bookings

## Browser Support

- Chrome/Edge: Latest 2 versions
- Firefox: Latest 2 versions
- Safari: Latest 2 versions
- Mobile browsers: iOS Safari 12+, Chrome Android

## Performance

- **Gzip bundle size**: ~61 KB
- **Build time**: <3s
- **Dev server**: Instant HMR
- **API calls**: Optimized with proper caching

## Environment Variables

Create `.env.local` if you need to override the API base:

```
VITE_API_BASE=/api
```

Default is `/api` with proxy to `http://localhost:8000`.

## Testing

Run dev server and test manually:

```bash
npm run dev
```

Visit:
- Signup: http://localhost:5173/sellers
- Login: http://localhost:5173/sellers/login
- Dashboard: http://localhost:5173/sellers/portal (requires auth)

## Deployment

1. Build the production bundle:
   ```bash
   npm run build
   ```

2. Deploy `dist/` to your static host (Vercel, Netlify, S3, etc.)

3. Configure your backend API endpoint in environment variables

4. Ensure CORS is configured properly on the FastAPI backend

## Code Quality

- **TypeScript**: Strict mode enabled
- **No ESLint warnings**: Clean build output
- **No console errors**: Production-ready
- **Component structure**: Clean separation of concerns
- **Reusable components**: DRY principles followed

## License

Part of BookWithClaw platform. All rights reserved.

## Support

For issues or questions, contact the development team.
