import { useState, useEffect } from 'react';
import { useApi } from '../hooks/useApi';
import { buyers } from '../utils/api';
import { UserProfile } from '../types';
import { FormInput } from './FormInput';

export const ProfileTab = () => {
  const { data: profileData, loading, refetch } = useApi<UserProfile>('/api/buyers/profile');
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
  });

  useEffect(() => {
    if (profileData) {
      setFormData({
        name: profileData.name || '',
        email: profileData.email || '',
        phone: profileData.phone || '',
      });
    }
  }, [profileData]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    try {
      await buyers.profile.update({
        name: formData.name,
        phone: formData.phone,
      });
      setIsEditing(false);
      refetch();
    } catch (error) {
      alert('Failed to update profile: ' + (error instanceof Error ? error.message : 'Unknown error'));
    } finally {
      setIsSaving(false);
    }
  };

  if (loading) {
    return <div className="text-center py-12 text-gray-500">Loading profile...</div>;
  }

  return (
    <div className="max-w-2xl space-y-6">
      {/* Guest Information */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-bold">Guest Information</h3>
          <button
            onClick={() => setIsEditing(!isEditing)}
            className="text-blue-600 hover:text-blue-700 font-medium"
          >
            {isEditing ? 'Cancel' : 'Edit'}
          </button>
        </div>

        {isEditing ? (
          <form onSubmit={handleSave} className="space-y-4">
            <FormInput
              label="Full Name"
              name="name"
              type="text"
              value={formData.name}
              onChange={handleChange}
              required
            />

            <FormInput
              label="Email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              required
              disabled
            />

            <FormInput
              label="Phone Number"
              name="phone"
              type="tel"
              value={formData.phone}
              onChange={handleChange}
              placeholder="+1 (555) 000-0000"
            />

            <button
              type="submit"
              disabled={isSaving}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-bold py-2 px-4 rounded-lg transition"
            >
              {isSaving ? 'Saving...' : 'Save Changes'}
            </button>
          </form>
        ) : (
          <div className="space-y-4">
            <div>
              <p className="text-sm text-gray-600">Full Name</p>
              <p className="text-lg font-semibold text-gray-900">{formData.name}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Email Address</p>
              <p className="text-lg font-semibold text-gray-900">{formData.email}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Phone Number</p>
              <p className="text-lg font-semibold text-gray-900">{formData.phone || 'Not provided'}</p>
            </div>
          </div>
        )}
      </div>

      {/* Payment Methods */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-bold">Payment Methods</h3>
          <button className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition text-sm">
            Add Payment Method
          </button>
        </div>

        <div className="space-y-3">
          {profileData?.payment_methods && profileData.payment_methods.length > 0 ? (
            profileData.payment_methods.map(method => (
              <div key={method.id} className="border border-gray-200 rounded-lg p-4 flex justify-between items-center">
                <div>
                  <p className="text-sm text-gray-600 capitalize">{method.type}</p>
                  <p className="font-semibold">•••• {method.last_four}</p>
                  <p className="text-xs text-gray-500">Expires: {method.expiry_date}</p>
                </div>
                <button className="text-red-600 hover:text-red-700 font-medium">Remove</button>
              </div>
            ))
          ) : (
            <p className="text-gray-500">No payment methods added. Add one to make bookings easier.</p>
          )}
        </div>
      </div>

      {/* Booking History */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-xl font-bold mb-4">Booking History Summary</h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-blue-50 rounded-lg p-4">
            <p className="text-sm text-gray-600 mb-2">Total Bookings</p>
            <p className="text-3xl font-bold text-blue-600">0</p>
          </div>
          <div className="bg-green-50 rounded-lg p-4">
            <p className="text-sm text-gray-600 mb-2">Total Spent</p>
            <p className="text-3xl font-bold text-green-600">$0</p>
          </div>
          <div className="bg-purple-50 rounded-lg p-4">
            <p className="text-sm text-gray-600 mb-2">Avg. per Night</p>
            <p className="text-3xl font-bold text-purple-600">$0</p>
          </div>
        </div>
      </div>

      {/* Account Settings */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-xl font-bold mb-4">Account Settings</h3>

        <div className="space-y-3">
          <button className="w-full text-left px-4 py-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition">
            <p className="font-medium text-gray-900">Change Password</p>
            <p className="text-sm text-gray-600">Update your password regularly</p>
          </button>
          <button className="w-full text-left px-4 py-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition">
            <p className="font-medium text-gray-900">Email Preferences</p>
            <p className="text-sm text-gray-600">Manage notification settings</p>
          </button>
          <button className="w-full text-left px-4 py-3 border border-red-200 rounded-lg hover:bg-red-50 transition">
            <p className="font-medium text-red-600">Delete Account</p>
            <p className="text-sm text-red-600">Permanently delete your account</p>
          </button>
        </div>
      </div>
    </div>
  );
};
