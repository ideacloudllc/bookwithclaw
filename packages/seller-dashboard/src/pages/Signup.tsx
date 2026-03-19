import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { validateEmail, validatePassword } from '../utils/auth';
import { FormInput } from '../components/FormInput';

export const Signup = () => {
  const { signup, loading, error: authError } = useAuth();
  const [formData, setFormData] = useState({
    hotel_name: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.hotel_name.trim()) {
      newErrors.hotel_name = 'Hotel name is required';
    }

    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!validateEmail(formData.email)) {
      newErrors.email = 'Invalid email format';
    }

    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (!validatePassword(formData.password)) {
      newErrors.password = 'Password must be at least 8 characters';
    }

    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    try {
      await signup(formData.email, formData.password, formData.hotel_name);
    } catch (err) {
      // Error is handled by useAuth hook
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Hero Section */}
      <div className="grid md:grid-cols-2 h-screen">
        <div className="hidden md:flex flex-col justify-center px-8 py-12 bg-gradient-to-br from-blue-600 to-indigo-700 text-white">
          <div className="max-w-md">
            <h1 className="text-4xl font-bold mb-6">Grow Your Hotel Business</h1>
            <p className="text-lg mb-8 text-blue-100">
              Join hundreds of hoteliers earning more with BookWithClaw
            </p>

            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <span className="text-2xl">💰</span>
                <div>
                  <h3 className="font-bold text-lg">Save on Commissions</h3>
                  <p className="text-blue-100">Only 1.8% vs 12% on OTAs</p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <span className="text-2xl">📊</span>
                <div>
                  <h3 className="font-bold text-lg">Full Control</h3>
                  <p className="text-blue-100">Manage inventory and pricing</p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <span className="text-2xl">🚀</span>
                <div>
                  <h3 className="font-bold text-lg">Instant Bookings</h3>
                  <p className="text-blue-100">Direct buyer connections</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Form Section */}
        <div className="flex flex-col justify-center px-6 md:px-8 py-12">
          <div className="max-w-sm mx-auto w-full">
            <h2 className="text-3xl font-bold mb-2 text-gray-900">Create Account</h2>
            <p className="text-gray-600 mb-8">Join BookWithClaw and start earning more</p>

            <form onSubmit={handleSubmit} className="space-y-4">
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
                label="Email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                error={errors.email}
                required
                placeholder="you@example.com"
              />

              <FormInput
                label="Password"
                name="password"
                type="password"
                value={formData.password}
                onChange={handleChange}
                error={errors.password}
                required
                placeholder="••••••••"
              />

              <FormInput
                label="Confirm Password"
                name="confirmPassword"
                type="password"
                value={formData.confirmPassword}
                onChange={handleChange}
                error={errors.confirmPassword}
                required
                placeholder="••••••••"
              />

              {authError && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                  {authError}
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-bold py-2 px-4 rounded-lg transition duration-200"
              >
                {loading ? 'Creating Account...' : 'Sign Up'}
              </button>
            </form>

            <p className="text-center text-gray-600 mt-6">
              Already have an account?{' '}
              <Link to="/sellers/login" className="text-blue-600 hover:text-blue-700 font-medium">
                Login here
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
