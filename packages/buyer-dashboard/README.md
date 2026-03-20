# BookWithClaw Buyer Dashboard

A modern React + TypeScript dashboard for guests to search for hotels, make offers, negotiate prices, and manage bookings.

## Features

- **Authentication**: Signup and login with email and password
- **Search Tab**: Browse available hotels/rooms with filters for dates, occupancy, and room type
- **My Offers Tab**: View all offers made with status tracking (pending, negotiating, accepted, rejected)
- **Negotiations Tab**: Active negotiation sessions with counter-offer capability
- **Bookings Tab**: Confirmed bookings with booking references and invoice download option
- **Profile Tab**: Manage personal information, payment methods, and account settings

## Tech Stack

- **React 18.3.1** - UI library
- **TypeScript 5.3.3** - Type safety
- **Vite 5.0.8** - Build tool
- **Tailwind CSS 3.3.6** - Styling
- **React Router DOM 6.20.0** - Routing

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── FormInput.tsx   # Form input field
│   ├── Modal.tsx       # Modal dialog
│   ├── Layout.tsx      # Dashboard layout with sidebar
│   ├── ProtectedRoute.tsx  # Route protection
│   ├── SearchTab.tsx   # Search & room discovery
│   ├── MyOffersTab.tsx # Offers management
│   ├── NegotiationsTab.tsx # Negotiation interface
│   ├── BookingsTab.tsx # Bookings display
│   └── ProfileTab.tsx  # User profile management
├── pages/              # Page components
│   ├── Signup.tsx      # Signup form
│   ├── Login.tsx       # Login form
│   └── Dashboard.tsx   # Main dashboard layout
├── hooks/              # Custom React hooks
│   ├── useAuth.ts      # Authentication logic
│   └── useApi.ts       # API data fetching
├── utils/              # Utility functions
│   ├── auth.ts         # Auth token & validation helpers
│   └── api.ts          # API client & endpoints
├── types/              # TypeScript type definitions
│   └── index.ts        # Type interfaces
├── App.tsx             # App root component
├── main.tsx            # Entry point
└── index.css           # Global styles
```

## Setup & Installation

### Prerequisites
- Node.js 16+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Development

The development server runs on `http://localhost:5174` with API proxy to `http://159.65.36.5:8890`.

### Available Routes

- `/buyers/` - Signup page
- `/buyers/login` - Login page
- `/buyers/portal/search` - Search hotels/rooms
- `/buyers/portal/offers` - View offers
- `/buyers/portal/negotiations` - Manage negotiations
- `/buyers/portal/bookings` - View bookings
- `/buyers/portal/profile` - User profile

## API Integration

The dashboard integrates with the BookWithClaw backend API:

### Authentication
- `POST /api/buyers/auth/register` - Signup
- `POST /api/buyers/auth/login` - Login

### Search
- `GET /api/buyers/search` - Search available rooms

### Offers
- `POST /api/buyers/offers` - Create offer
- `GET /api/buyers/offers` - List offers
- `GET /api/buyers/offers/{id}` - Get offer details

### Negotiations
- `GET /api/buyers/negotiations` - List negotiations
- `GET /api/buyers/negotiations/{id}` - Get negotiation details
- `POST /api/buyers/negotiations/{id}/counter` - Submit counter offer
- `POST /api/buyers/negotiations/{id}/accept` - Accept offer
- `POST /api/buyers/negotiations/{id}/reject` - Reject offer
- `POST /api/buyers/negotiations/{id}/walkaway` - Walk away from negotiation

### Bookings
- `GET /api/buyers/bookings` - List confirmed bookings
- `GET /api/buyers/bookings/{id}` - Get booking details

### Profile
- `GET /api/buyers/profile` - Get user profile
- `PUT /api/buyers/profile` - Update profile

## Authentication Flow

1. User signs up with email, password, and name
2. API returns JWT token
3. Token stored in `buyer_token` cookie
4. Token sent with all API requests via Authorization header
5. Protected routes check for valid token
6. Logout clears token and redirects to login

## Build & Deployment

### Production Build
```bash
npm run build
```

Creates optimized production files in `dist/` folder.

### Deployment
The built files in `dist/` can be served from `http://159.65.36.5:8890/buyers/` by configuring your web server.

For Docker deployment:
```dockerfile
FROM node:18
WORKDIR /app
COPY . .
RUN npm install
RUN npm run build
# Serve dist/ folder from web server
```

## File Structure

- `package.json` - Dependencies and scripts
- `vite.config.ts` - Vite configuration with API proxy
- `tsconfig.json` - TypeScript configuration
- `tailwind.config.js` - Tailwind CSS configuration
- `postcss.config.js` - PostCSS configuration
- `index.html` - HTML entry point

## Styling

- Uses Tailwind CSS utility classes
- Custom colors defined in tailwind.config.js
- Responsive design with mobile-first approach
- Dark mode ready sidebar with light content areas

## Error Handling

- API errors displayed to users in error alerts
- Form validation with field-level error messages
- Loading states during API calls
- Graceful fallbacks for missing data

## Future Enhancements

- [ ] Payment processing integration (Stripe)
- [ ] Email notifications
- [ ] Multi-language support
- [ ] Advanced search filters
- [ ] Review and rating system
- [ ] Chat for negotiations
- [ ] Mobile app version
- [ ] Calendar view for dates
- [ ] Wishlist feature

## License

© 2024 BookWithClaw. All rights reserved.
