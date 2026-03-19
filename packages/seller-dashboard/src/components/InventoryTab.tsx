import { useState } from 'react';
import { useApi } from '../hooks/useApi';
import { sellers } from '../utils/api';
import { Room } from '../types';
import { Modal } from './Modal';
import { FormInput } from './FormInput';

export const InventoryTab = () => {
  const { data: rooms, loading, refetch } = useApi<Room[]>('/api/sellers/rooms');
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [editingRoom, setEditingRoom] = useState<Room | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    type: 'standard',
    base_price: '',
    floor_price: '',
    max_occupancy: '2',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleOpenAdd = () => {
    setEditingRoom(null);
    setFormData({
      name: '',
      type: 'standard',
      base_price: '',
      floor_price: '',
      max_occupancy: '2',
    });
    setErrors({});
    setIsAddModalOpen(true);
  };

  const handleOpenEdit = (room: Room) => {
    setEditingRoom(room);
    setFormData({
      name: room.name,
      type: room.type,
      base_price: room.base_price.toString(),
      floor_price: room.floor_price.toString(),
      max_occupancy: room.max_occupancy.toString(),
    });
    setErrors({});
    setIsAddModalOpen(true);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) newErrors.name = 'Room name is required';
    if (!formData.base_price) newErrors.base_price = 'Base price is required';
    if (!formData.floor_price) newErrors.floor_price = 'Floor price is required';
    if (parseFloat(formData.floor_price) > parseFloat(formData.base_price)) {
      newErrors.floor_price = 'Floor price must be less than base price';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    setIsSubmitting(true);
    try {
      const payload = {
        name: formData.name,
        type: formData.type,
        base_price: parseFloat(formData.base_price),
        floor_price: parseFloat(formData.floor_price),
        max_occupancy: parseInt(formData.max_occupancy),
      };

      if (editingRoom) {
        await sellers.rooms.update(editingRoom.id, payload);
      } else {
        await sellers.rooms.create(payload);
      }

      setIsAddModalOpen(false);
      refetch();
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to save room';
      setErrors({ submit: message });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (roomId: string) => {
    if (!confirm('Are you sure you want to delete this room?')) return;

    try {
      await sellers.rooms.delete(roomId);
      refetch();
    } catch (error) {
      alert('Failed to delete room: ' + (error instanceof Error ? error.message : 'Unknown error'));
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="text-xl font-bold">Inventory Management</h3>
        <button
          onClick={handleOpenAdd}
          className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg"
        >
          ➕ Add Room
        </button>
      </div>

      {loading ? (
        <div className="text-center py-12 text-gray-500">Loading inventory...</div>
      ) : !rooms || rooms.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <p className="text-gray-500 mb-4">No rooms added yet</p>
          <button
            onClick={handleOpenAdd}
            className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg"
          >
            Add Your First Room
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {rooms.map(room => (
            <div key={room.id} className="bg-white rounded-lg shadow p-6 border-l-4 border-blue-500">
              <h4 className="text-lg font-bold mb-2">{room.name}</h4>
              <p className="text-sm text-gray-600 mb-3">{room.type}</p>

              <div className="space-y-2 mb-4">
                <div className="flex justify-between">
                  <span className="text-gray-600 text-sm">Base Price:</span>
                  <span className="font-bold">${room.base_price}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 text-sm">Max Occupancy:</span>
                  <span className="font-bold">{room.max_occupancy} guests</span>
                </div>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={() => handleOpenEdit(room)}
                  className="flex-1 bg-blue-100 hover:bg-blue-200 text-blue-700 font-medium py-2 px-3 rounded transition text-sm"
                >
                  Edit
                </button>
                <button
                  onClick={() => handleDelete(room.id)}
                  className="flex-1 bg-red-100 hover:bg-red-200 text-red-700 font-medium py-2 px-3 rounded transition text-sm"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add/Edit Room Modal */}
      <Modal
        isOpen={isAddModalOpen}
        title={editingRoom ? 'Edit Room' : 'Add New Room'}
        onClose={() => setIsAddModalOpen(false)}
        actions={
          <div className="flex gap-3">
            <button
              onClick={() => setIsAddModalOpen(false)}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              onClick={handleSubmit}
              disabled={isSubmitting}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded"
            >
              {isSubmitting ? 'Saving...' : 'Save'}
            </button>
          </div>
        }
      >
        <form className="space-y-4">
          <FormInput
            label="Room Name"
            name="name"
            value={formData.name}
            onChange={handleChange}
            error={errors.name}
            required
            placeholder="e.g., Deluxe Double Room"
          />

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Room Type <span className="text-red-500">*</span>
            </label>
            <select
              name="type"
              value={formData.type}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="standard">Standard</option>
              <option value="deluxe">Deluxe</option>
              <option value="suite">Suite</option>
              <option value="economy">Economy</option>
            </select>
          </div>

          <FormInput
            label="Base Price (per night)"
            name="base_price"
            type="number"
            value={formData.base_price}
            onChange={handleChange}
            error={errors.base_price}
            required
            placeholder="150.00"
          />

          <FormInput
            label="Floor Price"
            name="floor_price"
            type="number"
            value={formData.floor_price}
            onChange={handleChange}
            error={errors.floor_price}
            required
            placeholder="100.00"
          />

          <FormInput
            label="Max Occupancy"
            name="max_occupancy"
            type="number"
            value={formData.max_occupancy}
            onChange={handleChange}
            required
          />

          {errors.submit && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-3 py-2 rounded">
              {errors.submit}
            </div>
          )}
        </form>
      </Modal>
    </div>
  );
};
