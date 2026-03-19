import { useState } from 'react';
import { useApi } from '../hooks/useApi';
import { sellers } from '../utils/api';
import { Offer } from '../types';
import { Modal } from './Modal';
import { FormInput } from './FormInput';

const statusColors = {
  pending: 'bg-yellow-100 text-yellow-800',
  negotiating: 'bg-blue-100 text-blue-800',
  accepted: 'bg-green-100 text-green-800',
  rejected: 'bg-red-100 text-red-800',
};

export const OffersTab = () => {
  const { data: offers, loading, refetch } = useApi<Offer[]>('/api/sellers/offers');
  const [selectedOffer, setSelectedOffer] = useState<Offer | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [counterPrice, setCounterPrice] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleOpenCounter = (offer: Offer) => {
    setSelectedOffer(offer);
    setCounterPrice(offer.guest_budget.toString());
    setIsModalOpen(true);
  };

  const handleSubmitCounter = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedOffer || !counterPrice) return;

    setIsSubmitting(true);
    try {
      await sellers.offers.counter(selectedOffer.id, {
        counter_price: parseFloat(counterPrice),
      });
      setIsModalOpen(false);
      refetch();
    } catch (error) {
      alert('Failed to submit counter offer: ' + (error instanceof Error ? error.message : 'Unknown error'));
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleAccept = async (offerId: string) => {
    if (!confirm('Accept this offer?')) return;

    try {
      await sellers.offers.accept(offerId);
      refetch();
    } catch (error) {
      alert('Failed to accept offer: ' + (error instanceof Error ? error.message : 'Unknown error'));
    }
  };

  if (loading) {
    return <div className="text-center py-12 text-gray-500">Loading offers...</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-bold mb-4">Guest Offers & Inquiries</h3>
      </div>

      {!offers || offers.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <p className="text-gray-500">No offers yet. Check back soon!</p>
        </div>
      ) : (
        <div className="space-y-4">
          {offers.map(offer => (
            <div
              key={offer.id}
              className="bg-white rounded-lg shadow p-6 border-l-4 border-orange-500"
            >
              <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h4 className="text-lg font-bold">{offer.room_type}</h4>
                    <span className={`px-3 py-1 rounded-full text-xs font-bold ${statusColors[offer.status]}`}>
                      {offer.status}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <p className="text-gray-600">Check-in</p>
                      <p className="font-bold">{new Date(offer.dates.check_in).toLocaleDateString()}</p>
                    </div>
                    <div>
                      <p className="text-gray-600">Check-out</p>
                      <p className="font-bold">{new Date(offer.dates.check_out).toLocaleDateString()}</p>
                    </div>
                    <div>
                      <p className="text-gray-600">Guests</p>
                      <p className="font-bold">{offer.occupancy}</p>
                    </div>
                    <div>
                      <p className="text-gray-600">Budget</p>
                      <p className="font-bold text-green-600">${offer.guest_budget}</p>
                    </div>
                  </div>
                </div>

                <div className="flex flex-col gap-2 md:flex-row">
                  <button
                    onClick={() => handleOpenCounter(offer)}
                    className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition text-sm"
                  >
                    Counter Offer
                  </button>
                  {offer.status !== 'accepted' && (
                    <button
                      onClick={() => handleAccept(offer.id)}
                      className="bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded-lg transition text-sm"
                    >
                      Accept
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Counter Offer Modal */}
      <Modal
        isOpen={isModalOpen}
        title="Submit Counter Offer"
        onClose={() => setIsModalOpen(false)}
        actions={
          <div className="flex gap-3">
            <button
              onClick={() => setIsModalOpen(false)}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              onClick={handleSubmitCounter}
              disabled={isSubmitting}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded"
            >
              {isSubmitting ? 'Submitting...' : 'Submit Counter'}
            </button>
          </div>
        }
      >
        {selectedOffer && (
          <form className="space-y-4">
            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="text-sm text-gray-600">Guest Budget</p>
              <p className="text-2xl font-bold text-gray-900">${selectedOffer.guest_budget}</p>
            </div>

            <FormInput
              label="Your Counter Price (per night)"
              name="counterPrice"
              type="number"
              value={counterPrice}
              onChange={e => setCounterPrice(e.target.value)}
              required
              placeholder="180.00"
            />

            <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg text-sm text-blue-800">
              <p className="font-medium mb-1">💡 Tip:</p>
              <p>Counter with a price that reflects your minimum but shows willingness to negotiate.</p>
            </div>
          </form>
        )}
      </Modal>
    </div>
  );
};
