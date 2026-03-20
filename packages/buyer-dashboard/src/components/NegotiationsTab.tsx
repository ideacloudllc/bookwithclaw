import { useState } from 'react';
import { useApi } from '../hooks/useApi';
import { buyers } from '../utils/api';
import { Negotiation } from '../types';
import { Modal } from './Modal';
import { FormInput } from './FormInput';

interface NegotiationsResponse {
  negotiations?: Negotiation[];
}

export const NegotiationsTab = () => {
  const { data: negoData, loading, refetch } = useApi<NegotiationsResponse>('/api/buyers/negotiations');
  const negotiations = negoData?.negotiations || [];
  const [selectedNego, setSelectedNego] = useState<Negotiation | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [counterPrice, setCounterPrice] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleOpenCounter = (nego: Negotiation) => {
    setSelectedNego(nego);
    setCounterPrice(nego.current_price.toString());
    setIsModalOpen(true);
  };

  const handleSubmitCounter = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedNego || !counterPrice) return;

    setIsSubmitting(true);
    try {
      await buyers.negotiations.counter(selectedNego.id, {
        counter_price: parseFloat(counterPrice),
      });
      setIsModalOpen(false);
      refetch();
    } catch (error) {
      alert('Failed to submit counter: ' + (error instanceof Error ? error.message : 'Unknown error'));
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleAccept = async (negoId: string) => {
    if (!confirm('Accept this negotiation?')) return;

    try {
      await buyers.negotiations.accept(negoId);
      refetch();
    } catch (error) {
      alert('Failed to accept: ' + (error instanceof Error ? error.message : 'Unknown error'));
    }
  };

  const handleReject = async (negoId: string) => {
    if (!confirm('Reject this negotiation?')) return;

    try {
      await buyers.negotiations.reject(negoId);
      refetch();
    } catch (error) {
      alert('Failed to reject: ' + (error instanceof Error ? error.message : 'Unknown error'));
    }
  };

  const handleWalkaway = async (negoId: string) => {
    if (!confirm('Walk away from this negotiation?')) return;

    try {
      await buyers.negotiations.walkaway(negoId);
      refetch();
    } catch (error) {
      alert('Failed to walkaway: ' + (error instanceof Error ? error.message : 'Unknown error'));
    }
  };

  if (loading) {
    return <div className="text-center py-12 text-gray-500">Loading negotiations...</div>;
  }

  const activeNegos = negotiations.filter(n => n.status === 'active');

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-bold mb-4">Active Negotiations</h3>
        <p className="text-gray-600 mb-6">You have {activeNegos.length} active negotiation(s)</p>
      </div>

      {!activeNegos || activeNegos.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <p className="text-gray-500">No active negotiations. Check your offers to start negotiating!</p>
        </div>
      ) : (
        <div className="space-y-4">
          {activeNegos.map(nego => (
            <div
              key={nego.id}
              className="bg-white rounded-lg shadow p-6 border-l-4 border-blue-500 hover:shadow-lg transition"
            >
              <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                <div className="flex-1">
                  <div className="mb-2">
                    <h4 className="text-lg font-bold">{nego.hotel_name}</h4>
                    <p className="text-sm text-gray-600">{nego.room_type}</p>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <p className="text-gray-600">Current Price</p>
                      <p className="font-bold text-blue-600">${nego.current_price}/night</p>
                    </div>
                    <div>
                      <p className="text-gray-600">Round</p>
                      <p className="font-bold">#{nego.round}</p>
                    </div>
                    <div>
                      <p className="text-gray-600">Last Message</p>
                      <p className="font-bold text-sm truncate">{nego.last_message}</p>
                    </div>
                    <div>
                      <p className="text-gray-600">Updated</p>
                      <p className="font-bold text-sm">
                        {new Date(nego.last_updated).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="flex flex-col gap-2">
                  <button
                    onClick={() => handleOpenCounter(nego)}
                    className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition text-sm"
                  >
                    Counter Offer
                  </button>
                  <button
                    onClick={() => handleAccept(nego.id)}
                    className="bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded-lg transition text-sm"
                  >
                    Accept
                  </button>
                  <button
                    onClick={() => handleReject(nego.id)}
                    className="bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-lg transition text-sm"
                  >
                    Reject
                  </button>
                  <button
                    onClick={() => handleWalkaway(nego.id)}
                    className="bg-gray-600 hover:bg-gray-700 text-white font-medium py-2 px-4 rounded-lg transition text-sm"
                  >
                    Walk Away
                  </button>
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
        {selectedNego && (
          <form className="space-y-4">
            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="text-sm text-gray-600">Current Price</p>
              <p className="text-2xl font-bold text-gray-900">${selectedNego.current_price}/night</p>
            </div>

            <FormInput
              label="Your Counter Price (per night)"
              name="counterPrice"
              type="number"
              step="0.01"
              value={counterPrice}
              onChange={e => setCounterPrice(e.target.value)}
              required
              placeholder="140.00"
            />

            <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg text-sm text-blue-800">
              <p className="font-medium mb-1">💡 Negotiation Tip:</p>
              <p>Make incremental adjustments to show good faith. Round {selectedNego.round + 1} - be strategic!</p>
            </div>
          </form>
        )}
      </Modal>
    </div>
  );
};
