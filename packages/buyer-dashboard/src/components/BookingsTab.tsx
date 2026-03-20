import { useApi } from '../hooks/useApi';
import { Booking } from '../types';
import { Modal } from './Modal';
import { useState } from 'react';

interface BookingsResponse {
  bookings?: Booking[];
}

export const BookingsTab = () => {
  const { data: bookingsData, loading } = useApi<BookingsResponse>('/api/buyers/bookings');
  const bookings = bookingsData?.bookings || [];
  const [selectedBooking, setSelectedBooking] = useState<Booking | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleViewDetails = (booking: Booking) => {
    setSelectedBooking(booking);
    setIsModalOpen(true);
  };

  const handleDownloadInvoice = (bookingId: string) => {
    // Placeholder for invoice download
    alert(`Downloading invoice for booking ${bookingId}...`);
  };

  if (loading) {
    return <div className="text-center py-12 text-gray-500">Loading bookings...</div>;
  }

  const confirmedBookings = bookings.filter(b => b.status === 'completed');

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-bold mb-4">My Bookings</h3>
        <p className="text-gray-600 mb-6">You have {confirmedBookings.length} confirmed booking(s)</p>
      </div>

      {!confirmedBookings || confirmedBookings.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <p className="text-gray-500">You don't have any confirmed bookings yet.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {confirmedBookings.map(booking => (
            <div
              key={booking.id}
              className="bg-white rounded-lg shadow overflow-hidden hover:shadow-lg transition border-t-4 border-green-500"
            >
              <div className="p-6">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h4 className="text-lg font-bold text-gray-900">{booking.hotel_name}</h4>
                    <p className="text-sm text-gray-600">{booking.room_type}</p>
                  </div>
                  <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-xs font-bold">
                    Confirmed
                  </span>
                </div>

                <div className="space-y-3 mb-6 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Check-in:</span>
                    <span className="font-medium">{new Date(booking.check_in).toLocaleDateString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Check-out:</span>
                    <span className="font-medium">{new Date(booking.check_out).toLocaleDateString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Guests:</span>
                    <span className="font-medium">{booking.occupancy}</span>
                  </div>
                  <div className="flex justify-between border-t pt-3">
                    <span className="text-gray-600">Final Price:</span>
                    <span className="font-bold text-green-600">${booking.final_price}/night</span>
                  </div>
                </div>

                <div className="bg-gray-50 p-3 rounded mb-4">
                  <p className="text-xs text-gray-600">Booking Reference</p>
                  <p className="font-mono font-bold text-sm">{booking.booking_ref}</p>
                </div>

                <div className="flex gap-2">
                  <button
                    onClick={() => handleViewDetails(booking)}
                    className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition text-sm"
                  >
                    View Details
                  </button>
                  <button
                    onClick={() => handleDownloadInvoice(booking.id)}
                    className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-900 font-medium py-2 px-4 rounded-lg transition text-sm"
                  >
                    Invoice
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Details Modal */}
      <Modal
        isOpen={isModalOpen}
        title="Booking Details"
        onClose={() => setIsModalOpen(false)}
      >
        {selectedBooking && (
          <div className="space-y-4">
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="text-lg font-bold text-gray-900 mb-1">{selectedBooking.hotel_name}</h4>
              <p className="text-sm text-gray-600">{selectedBooking.room_type}</p>
            </div>

            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-600">Check-in Date</p>
                <p className="font-bold">{new Date(selectedBooking.check_in).toLocaleDateString()}</p>
              </div>
              <div>
                <p className="text-gray-600">Check-out Date</p>
                <p className="font-bold">{new Date(selectedBooking.check_out).toLocaleDateString()}</p>
              </div>
              <div>
                <p className="text-gray-600">Number of Guests</p>
                <p className="font-bold">{selectedBooking.occupancy}</p>
              </div>
              <div>
                <p className="text-gray-600">Final Price</p>
                <p className="font-bold text-green-600">${selectedBooking.final_price}/night</p>
              </div>
            </div>

            <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Booking Reference</p>
              <p className="font-mono font-bold">{selectedBooking.booking_ref}</p>
            </div>

            <div className="bg-green-50 border border-green-200 p-4 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Status</p>
              <p className="text-lg font-bold text-green-600">Confirmed</p>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};
