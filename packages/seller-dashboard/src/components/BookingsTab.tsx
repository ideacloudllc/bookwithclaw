import { useApi } from '../hooks/useApi';
import { Booking } from '../types';

export const BookingsTab = () => {
  const { data: bookings, loading } = useApi<Booking[]>('/api/sellers/bookings');

  if (loading) {
    return <div className="text-center py-12 text-gray-500">Loading bookings...</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-bold mb-4">Confirmed Reservations</h3>
      </div>

      {!bookings || bookings.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <p className="text-gray-500">No bookings yet. Your confirmed reservations will appear here.</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="bg-gray-100 border-b">
                <th className="px-6 py-3 text-left text-sm font-bold text-gray-700">Guest</th>
                <th className="px-6 py-3 text-left text-sm font-bold text-gray-700">Room</th>
                <th className="px-6 py-3 text-left text-sm font-bold text-gray-700">Check-in</th>
                <th className="px-6 py-3 text-left text-sm font-bold text-gray-700">Check-out</th>
                <th className="px-6 py-3 text-left text-sm font-bold text-gray-700">Rate</th>
                <th className="px-6 py-3 text-left text-sm font-bold text-gray-700">Status</th>
              </tr>
            </thead>
            <tbody>
              {bookings.map((booking, idx) => (
                <tr key={booking.id} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">{booking.guest_name}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">{booking.room}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">
                    {new Date(booking.check_in).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">
                    {new Date(booking.check_out).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 text-sm font-bold text-green-600">${booking.rate}</td>
                  <td className="px-6 py-4 text-sm">
                    <span className="px-3 py-1 rounded-full text-xs font-bold bg-green-100 text-green-800">
                      {booking.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
