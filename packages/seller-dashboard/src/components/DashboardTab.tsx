import { useApi } from '../hooks/useApi';
import { StatCard } from './StatCard';
import { Room, Offer, Booking } from '../types';

interface OffersResponse {
  offers?: Offer[];
}

interface BookingsResponse {
  bookings?: Booking[];
}

export const DashboardTab = ({ onNavigate }: { onNavigate: (tab: string) => void }) => {
  const { data: rooms, loading: roomsLoading } = useApi<Room[]>('/api/sellers/rooms');
  const { data: offersData, loading: offersLoading } = useApi<OffersResponse>('/api/sellers/offers');
  const { data: bookingsData, loading: bookingsLoading } = useApi<BookingsResponse>('/api/sellers/bookings');

  const loading = roomsLoading || offersLoading || bookingsLoading;

  // Extract offers and bookings from wrapped responses
  const offers = offersData?.offers || [];
  const bookings = bookingsData?.bookings || [];

  // Calculate stats
  const activeListings = rooms?.length || 0;
  const pendingOffers = (offers as any[]).filter((o: any) => o.status === 'pending').length || 0;
  const revenue = (bookings as any[]).reduce((sum: number, b: any) => sum + (b.final_price || 0), 0) || 0;
  const occupancyRate = activeListings > 0 
    ? Math.round((bookings as any[]).length / activeListings * 100) 
    : 0;

  if (loading) {
    return <div className="text-center py-12 text-gray-500">Loading dashboard...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard 
          label="Active Listings" 
          value={activeListings.toString()} 
          icon="🏠" 
          color="blue" 
        />
        <StatCard 
          label="Pending Offers" 
          value={pendingOffers.toString()} 
          icon="💼" 
          color="orange" 
        />
        <StatCard 
          label="Total Revenue" 
          value={`$${revenue.toLocaleString()}`} 
          icon="💰" 
          color="green" 
        />
        <StatCard 
          label="Occupancy Rate" 
          value={`${occupancyRate}%`} 
          icon="📊" 
          color="purple" 
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Quick Actions */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-bold mb-4">Quick Actions</h3>
          <div className="space-y-3">
            <button
              onClick={() => onNavigate('inventory')}
              className="w-full bg-blue-50 hover:bg-blue-100 border border-blue-200 text-blue-700 font-medium py-3 px-4 rounded-lg transition"
            >
              ➕ Add New Room
            </button>
            <button
              onClick={() => onNavigate('pricing')}
              className="w-full bg-green-50 hover:bg-green-100 border border-green-200 text-green-700 font-medium py-3 px-4 rounded-lg transition"
            >
              💰 Update Pricing
            </button>
            <button
              onClick={() => onNavigate('offers')}
              className="w-full bg-orange-50 hover:bg-orange-100 border border-orange-200 text-orange-700 font-medium py-3 px-4 rounded-lg transition"
            >
              💬 View Offers
            </button>
          </div>
        </div>

        {/* Recent Bookings */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-bold mb-4">Recent Bookings</h3>
          {bookings && (bookings as any[]).length > 0 ? (
            <div className="space-y-3">
              {(bookings as any[]).slice(0, 3).map((booking: any, idx: number) => (
                <div key={idx} className="border-l-4 border-blue-500 pl-4 py-2">
                  <p className="font-medium text-gray-900">{booking.room_name || booking.room || 'Room'}</p>
                  <p className="text-sm text-gray-500">
                    {booking.guest_name || 'Guest'} • {booking.checkin_date || booking.checkin || 'TBD'}
                  </p>
                  <p className="text-sm font-bold text-green-600 mt-1">
                    ${booking.final_price || booking.agreed_price || booking.total || 0}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-6">No bookings yet</p>
          )}
        </div>
      </div>
    </div>
  );
};
