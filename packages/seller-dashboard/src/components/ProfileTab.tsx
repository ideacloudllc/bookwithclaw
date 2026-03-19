import { useState, useEffect } from 'react';
import { useApi } from '../hooks/useApi';
import { sellers } from '../utils/api';
import { SellerProfile } from '../types';
import { FormInput } from './FormInput';

export const ProfileTab = () => {
  const { data: profile, loading, refetch } = useApi<SellerProfile>('/api/sellers/profile');
  const [formData, setFormData] = useState({
    hotel_name: '',
    address: '',
    phone: '',
    check_in_time: '14:00',
    check_out_time: '11:00',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSaving, setIsSaving] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  useEffect(() => {
    if (profile) {
      setFormData({
        hotel_name: profile.hotel_name || '',
        address: profile.address || '',
        phone: profile.phone || '',
        check_in_time: profile.check_in_time || '14:00',
        check_out_time: profile.check_out_time || '11:00',
      });
    }
  }, [profile]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
    setSuccessMessage('');
  };

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.hotel_name.trim()) {
      newErrors.hotel_name = 'Hotel name is required';
    }
    if (!formData.address.trim()) {
      newErrors.address = 'Address is required';
    }
    if (!formData.phone.trim()) {
      newErrors.phone = 'Phone is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    setIsSaving(true);
    try {
      await sellers.profile.update({
        hotel_name: formData.hotel_name,
        address: formData.address,
        phone: formData.phone,
        check_in_time: formData.check_in_time,
        check_out_time: formData.check_out_time,
      });

      setSuccessMessage('Profile updated successfully!');
      setTimeout(() => setSuccessMessage(''), 3000);
      refetch();
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to update profile';
      setErrors({ submit: message });
    } finally {
      setIsSaving(false);
    }
  };

  if (loading) {
    return <div className="text-center py-12 text-gray-500">Loading profile...</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-bold mb-4">Hotel Profile</h3>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Profile Form */}
        <div className="lg:col-span-2">
          <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow p-6 space-y-4">
            <FormInput
              label="Hotel Name"
              name="hotel_name"
              value={formData.hotel_name}
              onChange={handleChange}
              error={errors.hotel_name}
              required
              placeholder="Your hotel name"
            />

            <FormInput
              label="Address"
              name="address"
              value={formData.address}
              onChange={handleChange}
              error={errors.address}
              required
              placeholder="Street address"
            />

            <FormInput
              label="Phone"
              name="phone"
              type="tel"
              value={formData.phone}
              onChange={handleChange}
              error={errors.phone}
              required
              placeholder="+1 (555) 000-0000"
            />

            <div className="grid grid-cols-2 gap-4">
              <FormInput
                label="Check-in Time"
                name="check_in_time"
                type="time"
                value={formData.check_in_time}
                onChange={handleChange}
                required
              />

              <FormInput
                label="Check-out Time"
                name="check_out_time"
                type="time"
                value={formData.check_out_time}
                onChange={handleChange}
                required
              />
            </div>

            {successMessage && (
              <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded">
                ✅ {successMessage}
              </div>
            )}

            {errors.submit && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                {errors.submit}
              </div>
            )}

            <button
              type="submit"
              disabled={isSaving}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-bold py-3 px-4 rounded-lg transition duration-200"
            >
              {isSaving ? 'Saving...' : 'Save Profile'}
            </button>
          </form>
        </div>

        {/* Sidebar Cards */}
        <div className="space-y-4">
          {/* Email Card */}
          <div className="bg-white rounded-lg shadow p-6">
            <h4 className="font-bold text-gray-900 mb-2">Email</h4>
            <p className="text-gray-600 text-sm break-all">{profile?.email}</p>
            <p className="text-xs text-gray-500 mt-2">✓ Verified</p>
          </div>

          {/* Stripe Status Card */}
          <div className="bg-white rounded-lg shadow p-6 border-l-4 border-orange-500">
            <h4 className="font-bold text-gray-900 mb-3">Stripe Connect</h4>
            {profile?.stripe_status === 'connected' ? (
              <div>
                <p className="text-sm text-green-600 font-medium mb-2">✓ Connected</p>
                <p className="text-xs text-gray-500">Ready to receive payments</p>
              </div>
            ) : (
              <div>
                <p className="text-sm text-orange-600 font-medium mb-2">⚠️ Not Connected</p>
                <p className="text-xs text-gray-500 mb-3">
                  Connect Stripe to receive payouts
                </p>
                <button className="w-full bg-orange-100 hover:bg-orange-200 text-orange-700 font-medium py-2 px-3 rounded text-sm transition">
                  Connect Stripe
                </button>
              </div>
            )}
          </div>

          {/* Account Stats */}
          <div className="bg-white rounded-lg shadow p-6">
            <h4 className="font-bold text-gray-900 mb-3">Account Stats</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Member since</span>
                <span className="font-medium">March 2025</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Listings</span>
                <span className="font-medium">12</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Total Bookings</span>
                <span className="font-medium">24</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
