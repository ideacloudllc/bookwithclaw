import { useState } from 'react';
import { useApi } from '../hooks/useApi';
import { buyers } from '../utils/api';
import { Room } from '../types';
import { FormInput } from './FormInput';
import { Modal } from './Modal';

interface SearchResponse {
  rooms?: Room[];
}

export const SearchTab = () => {
  const [filters, setFilters] = useState({
    check_in: '',
    check_out: '',
    occupancy: '1',
    room_type: '',
  });
  const [searched, setSearched] = useState(false);
  const { data: searchData, loading, error } = useApi<SearchResponse>(
    searched && filters.check_in && filters.check_out
      ? `/api/buyers/search?check_in=${filters.check_in}&check_out=${filters.check_out}&occupancy=${filters.occupancy}${filters.room_type ? `&room_type=${filters.room_type}` : ''}`
      : '',
    [filters, searched]
  );

  const [selectedRoom, setSelectedRoom] = useState<Room | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [offerPrice, setOfferPrice] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleFilterChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFilters(prev => ({ ...prev, [name]: value }));
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!filters.check_in || !filters.check_out) {
      alert('Please select check-in and check-out dates');
      return;
    }
    setSearched(true);
  };

  const handleBookClick = (room: Room) => {
    setSelectedRoom(room);
    setOfferPrice(room.price.toString());
    setIsModalOpen(true);
  };

  const handleSubmitOffer = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedRoom || !offerPrice) return;

    setIsSubmitting(true);
    try {
      await buyers.offers.create({
        room_id: selectedRoom.id,
        offered_price: parseFloat(offerPrice),
      });
      setIsModalOpen(false);
      alert('Offer submitted successfully!');
      setOfferPrice('');
      setSelectedRoom(null);
    } catch (err) {
      alert('Failed to submit offer: ' + (err instanceof Error ? err.message : 'Unknown error'));
    } finally {
      setIsSubmitting(false);
    }
  };

  const rooms = searchData?.rooms || [];

  return (
    <div className="space-y-6">
      {/* Search Form */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-xl font-bold mb-4">Search Hotels & Rooms</h3>
        <form onSubmit={handleSearch} className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <FormInput
            label="Check-in Date"
            name="check_in"
            type="date"
            value={filters.check_in}
            onChange={handleFilterChange}
            required
          />
          <FormInput
            label="Check-out Date"
            name="check_out"
            type="date"
            value={filters.check_out}
            onChange={handleFilterChange}
            required
          />
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Occupancy
            </label>
            <select
              name="occupancy"
              value={filters.occupancy}
              onChange={handleFilterChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="1">1 Guest</option>
              <option value="2">2 Guests</option>
              <option value="3">3 Guests</option>
              <option value="4">4 Guests</option>
              <option value="5">5+ Guests</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Room Type
            </label>
            <select
              name="room_type"
              value={filters.room_type}
              onChange={handleFilterChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Any</option>
              <option value="single">Single</option>
              <option value="double">Double</option>
              <option value="suite">Suite</option>
              <option value="deluxe">Deluxe</option>
            </select>
          </div>
          <div className="flex items-end">
            <button
              type="submit"
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg transition"
            >
              Search
            </button>
          </div>
        </form>
      </div>

      {/* Results */}
      {searched && (
        <div>
          {loading && (
            <div className="text-center py-12 text-gray-500">Loading results...</div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          {!loading && rooms.length === 0 && (
            <div className="text-center py-12 bg-gray-50 rounded-lg">
              <p className="text-gray-500">No rooms available for selected dates</p>
            </div>
          )}

          {!loading && rooms.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {rooms.map(room => (
                <div key={room.id} className="bg-white rounded-lg shadow overflow-hidden hover:shadow-lg transition">
                  <div className="p-6">
                    <h4 className="text-lg font-bold text-gray-900 mb-2">{room.hotel_name}</h4>
                    <p className="text-sm text-gray-600 mb-4">{room.room_type}</p>

                    <div className="space-y-2 mb-4 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Check-in:</span>
                        <span className="font-medium">{new Date(room.check_in).toLocaleDateString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Check-out:</span>
                        <span className="font-medium">{new Date(room.check_out).toLocaleDateString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Max Occupancy:</span>
                        <span className="font-medium">{room.occupancy} guests</span>
                      </div>
                    </div>

                    <div className="bg-blue-50 border border-blue-200 rounded p-3 mb-4">
                      <p className="text-sm text-gray-600">Price per Night</p>
                      <p className="text-2xl font-bold text-blue-600">${room.price}</p>
                    </div>

                    <button
                      onClick={() => handleBookClick(room)}
                      className="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded-lg transition"
                    >
                      Make Offer
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Offer Modal */}
      <Modal
        isOpen={isModalOpen}
        title="Make an Offer"
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
              onClick={handleSubmitOffer}
              disabled={isSubmitting}
              className="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white rounded"
            >
              {isSubmitting ? 'Submitting...' : 'Submit Offer'}
            </button>
          </div>
        }
      >
        {selectedRoom && (
          <form className="space-y-4">
            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">{selectedRoom.hotel_name}</p>
              <p className="text-lg font-bold text-gray-900">{selectedRoom.room_type}</p>
            </div>

            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-600">Check-in</p>
                <p className="font-medium">{new Date(selectedRoom.check_in).toLocaleDateString()}</p>
              </div>
              <div>
                <p className="text-gray-600">Check-out</p>
                <p className="font-medium">{new Date(selectedRoom.check_out).toLocaleDateString()}</p>
              </div>
            </div>

            <FormInput
              label="Your Offer (per night)"
              name="offerPrice"
              type="number"
              step="0.01"
              value={offerPrice}
              onChange={e => setOfferPrice(e.target.value)}
              required
              placeholder="150.00"
            />

            <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg text-sm text-blue-800">
              <p className="font-medium mb-1">💡 Tip:</p>
              <p>Make your offer competitive but reasonable. You can negotiate after the hotel responds.</p>
            </div>
          </form>
        )}
      </Modal>
    </div>
  );
};
