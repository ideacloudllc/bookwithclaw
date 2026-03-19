import { useState, useEffect } from 'react';
import { useApi } from '../hooks/useApi';
import { sellers } from '../utils/api';
import { Room } from '../types';
import { FormInput } from './FormInput';

export const PricingTab = () => {
  const { data: rooms, loading, refetch } = useApi<Room[]>('/api/sellers/rooms');
  const [editingId, setEditingId] = useState<string | null>(null);
  const [formData, setFormData] = useState<Record<string, any>>({});
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    if (rooms) {
      const data: Record<string, any> = {};
      rooms.forEach(room => {
        data[room.id] = {
          base_price: room.base_price,
          floor_price: room.floor_price,
          ceiling_price: room.ceiling_price || room.base_price * 1.5,
        };
      });
      setFormData(data);
    }
  }, [rooms]);

  const handleFieldChange = (roomId: string, field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [roomId]: {
        ...prev[roomId],
        [field]: parseFloat(value),
      },
    }));
  };

  const handleSave = async (roomId: string) => {
    setIsSaving(true);
    try {
      const room = rooms?.find(r => r.id === roomId);
      if (!room) return;

      await sellers.rooms.update(roomId, {
        name: room.name,
        type: room.type,
        base_price: formData[roomId].base_price,
        floor_price: formData[roomId].floor_price,
        max_occupancy: room.max_occupancy,
      });

      setEditingId(null);
      refetch();
    } catch (error) {
      alert('Failed to save: ' + (error instanceof Error ? error.message : 'Unknown error'));
    } finally {
      setIsSaving(false);
    }
  };

  if (loading) {
    return <div className="text-center py-12 text-gray-500">Loading pricing...</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-bold mb-4">Dynamic Pricing Management</h3>
        <p className="text-gray-600 text-sm mb-6">Manage rates for each room to maximize revenue</p>
      </div>

      {!rooms || rooms.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <p className="text-gray-500 mb-4">No rooms yet. Add rooms from the Inventory tab first.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {rooms.map(room => (
            <div
              key={room.id}
              className="bg-white rounded-lg shadow border-l-4 border-purple-500 p-6"
            >
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
                <div>
                  <h4 className="text-lg font-bold text-gray-900">{room.name}</h4>
                  <p className="text-sm text-gray-500">{room.type}</p>
                </div>

                {editingId === room.id ? (
                  <>
                    <FormInput
                      label="Base Price"
                      name={`base_${room.id}`}
                      type="number"
                      value={formData[room.id]?.base_price?.toString() || ''}
                      onChange={e =>
                        handleFieldChange(room.id, 'base_price', e.target.value)
                      }
                    />
                    <FormInput
                      label="Floor Price"
                      name={`floor_${room.id}`}
                      type="number"
                      value={formData[room.id]?.floor_price?.toString() || ''}
                      onChange={e =>
                        handleFieldChange(room.id, 'floor_price', e.target.value)
                      }
                    />
                    <FormInput
                      label="Ceiling Price"
                      name={`ceiling_${room.id}`}
                      type="number"
                      value={formData[room.id]?.ceiling_price?.toString() || ''}
                      onChange={e =>
                        handleFieldChange(room.id, 'ceiling_price', e.target.value)
                      }
                    />
                  </>
                ) : (
                  <>
                    <div>
                      <p className="text-xs text-gray-600 mb-1">Base Price</p>
                      <p className="text-lg font-bold text-gray-900">
                        ${formData[room.id]?.base_price.toFixed(2) || room.base_price}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-600 mb-1">Floor Price</p>
                      <p className="text-lg font-bold text-blue-600">
                        ${formData[room.id]?.floor_price.toFixed(2) || room.floor_price}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-600 mb-1">Ceiling Price</p>
                      <p className="text-lg font-bold text-green-600">
                        ${formData[room.id]?.ceiling_price?.toFixed(2) || (room.ceiling_price || room.base_price * 1.5)}
                      </p>
                    </div>
                  </>
                )}
              </div>

              <div className="flex gap-2">
                {editingId === room.id ? (
                  <>
                    <button
                      onClick={() => setEditingId(null)}
                      className="px-4 py-2 border border-gray-300 text-gray-700 rounded hover:bg-gray-50 transition text-sm font-medium"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={() => handleSave(room.id)}
                      disabled={isSaving}
                      className="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white rounded transition text-sm font-medium"
                    >
                      {isSaving ? 'Saving...' : 'Save Changes'}
                    </button>
                  </>
                ) : (
                  <button
                    onClick={() => setEditingId(room.id)}
                    className="px-4 py-2 bg-blue-100 hover:bg-blue-200 text-blue-700 rounded transition text-sm font-medium"
                  >
                    ✏️ Edit Pricing
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h4 className="font-bold text-blue-900 mb-3">💡 Pricing Strategy Tips</h4>
        <ul className="space-y-2 text-sm text-blue-800">
          <li>• <strong>Floor Price:</strong> Minimum acceptable rate (covers costs + profit)</li>
          <li>• <strong>Base Price:</strong> Your standard daily rate</li>
          <li>• <strong>Ceiling Price:</strong> Maximum you want to charge during peak seasons</li>
          <li>• Adjust seasonally to maximize occupancy and revenue</li>
          <li>• Monitor competitor rates and guest demand</li>
        </ul>
      </div>
    </div>
  );
};
