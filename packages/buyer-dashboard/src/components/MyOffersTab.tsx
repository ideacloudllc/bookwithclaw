import { useState } from 'react';
import { useApi } from '../hooks/useApi';
import { Offer } from '../types';
import { Modal } from './Modal';

interface OffersResponse {
  offers?: Offer[];
}

const statusColors = {
  pending: 'bg-yellow-100 text-yellow-800',
  negotiating: 'bg-blue-100 text-blue-800',
  accepted: 'bg-green-100 text-green-800',
  rejected: 'bg-red-100 text-red-800',
};

export const MyOffersTab = () => {
  const { data: offersData, loading } = useApi<OffersResponse>('/api/buyers/offers');
  const offers = offersData?.offers || [];
  const [selectedOffer, setSelectedOffer] = useState<Offer | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleViewDetails = (offer: Offer) => {
    setSelectedOffer(offer);
    setIsModalOpen(true);
  };

  const stats = {
    total: offers.length,
    pending: offers.filter(o => o.status === 'pending').length,
    negotiating: offers.filter(o => o.status === 'negotiating').length,
    accepted: offers.filter(o => o.status === 'accepted').length,
    rejected: offers.filter(o => o.status === 'rejected').length,
  };

  if (loading) {
    return <div className="text-center py-12 text-gray-500">Loading offers...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-gray-600 text-sm">Total Offers</p>
          <p className="text-3xl font-bold text-gray-900">{stats.total}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-gray-600 text-sm">Pending</p>
          <p className="text-3xl font-bold text-yellow-600">{stats.pending}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-gray-600 text-sm">Negotiating</p>
          <p className="text-3xl font-bold text-blue-600">{stats.negotiating}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-gray-600 text-sm">Accepted</p>
          <p className="text-3xl font-bold text-green-600">{stats.accepted}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-gray-600 text-sm">Rejected</p>
          <p className="text-3xl font-bold text-red-600">{stats.rejected}</p>
        </div>
      </div>

      {/* Offers List */}
      <div>
        <h3 className="text-xl font-bold mb-4">My Offers</h3>

        {!offers || offers.length === 0 ? (
          <div className="text-center py-12 bg-gray-50 rounded-lg">
            <p className="text-gray-500">You haven't made any offers yet. Start searching for rooms!</p>
          </div>
        ) : (
          <div className="space-y-4">
            {offers.map(offer => (
              <div
                key={offer.id}
                className="bg-white rounded-lg shadow p-6 border-l-4 border-orange-500 hover:shadow-lg transition"
              >
                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h4 className="text-lg font-bold">{offer.hotel_name}</h4>
                      <span className={`px-3 py-1 rounded-full text-xs font-bold ${statusColors[offer.status]}`}>
                        {offer.status}
                      </span>
                    </div>

                    <p className="text-sm text-gray-600 mb-3">{offer.room_type}</p>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <p className="text-gray-600">Check-in</p>
                        <p className="font-bold">
                          {new Date(offer.check_in).toLocaleDateString()}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-600">Check-out</p>
                        <p className="font-bold">
                          {new Date(offer.check_out).toLocaleDateString()}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-600">Occupancy</p>
                        <p className="font-bold">{offer.occupancy} guest(s)</p>
                      </div>
                      <div>
                        <p className="text-gray-600">Your Offer</p>
                        <p className="font-bold text-orange-600">${offer.offered_price}/night</p>
                      </div>
                    </div>
                  </div>

                  <div className="flex flex-col gap-2">
                    <button
                      onClick={() => handleViewDetails(offer)}
                      className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition text-sm"
                    >
                      View Details
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Details Modal */}
      <Modal
        isOpen={isModalOpen}
        title="Offer Details"
        onClose={() => setIsModalOpen(false)}
      >
        {selectedOffer && (
          <div className="space-y-4">
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="text-lg font-bold text-gray-900 mb-2">{selectedOffer.hotel_name}</h4>
              <p className="text-sm text-gray-600">{selectedOffer.room_type}</p>
            </div>

            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-600">Check-in Date</p>
                <p className="font-bold">{new Date(selectedOffer.check_in).toLocaleDateString()}</p>
              </div>
              <div>
                <p className="text-gray-600">Check-out Date</p>
                <p className="font-bold">{new Date(selectedOffer.check_out).toLocaleDateString()}</p>
              </div>
              <div>
                <p className="text-gray-600">Occupancy</p>
                <p className="font-bold">{selectedOffer.occupancy} guest(s)</p>
              </div>
              <div>
                <p className="text-gray-600">Your Offer</p>
                <p className="font-bold text-orange-600">${selectedOffer.offered_price}/night</p>
              </div>
            </div>

            <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Status</p>
              <p className={`text-lg font-bold ${
                selectedOffer.status === 'accepted' ? 'text-green-600' :
                selectedOffer.status === 'rejected' ? 'text-red-600' :
                selectedOffer.status === 'negotiating' ? 'text-blue-600' : 'text-yellow-600'
              }`}>
                {selectedOffer.status.charAt(0).toUpperCase() + selectedOffer.status.slice(1)}
              </p>
            </div>

            <div className="text-sm text-gray-600">
              <p>Submitted: {new Date(selectedOffer.created_at).toLocaleDateString()}</p>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};
