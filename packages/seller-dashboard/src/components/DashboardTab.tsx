import { useApi } from '../hooks/useApi';
import { StatCard } from './StatCard';

export const DashboardTab = ({ onNavigate }: { onNavigate: (tab: string) => void }) => {
  const { loading } = useApi('/api/sellers/profile');

  if (loading) {
    return <div className="text-center py-12 text-gray-500">Loading dashboard...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="Active Listings" value="12" icon="🏠" color="blue" />
        <StatCard label="Pending Offers" value="3" icon="💼" color="orange" />
        <StatCard label="This Month Revenue" value="$4,250" icon="💰" color="green" />
        <StatCard label="Occupancy Rate" value="78%" icon="📊" color="purple" />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Quick Actions */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-bold mb-4">Quick Actions</h3>
          <div className="space-y-3">
            <button
              onClick={() => onNavigate('inventory')}
              className="w-full bg-blue-50 hover:bg-blue-100 border border-blue-200 text-blue-700 font-medium py-3 px-4 rounded-lg transition"
            >
              ➕ Add New Room
            </button>
            <button
              onClick={() => onNavigate('pricing')}
              className="w-full bg-green-50 hover:bg-green-100 border border-green-200 text-green-700 font-medium py-3 px-4 rounded-lg transition"
            >
              💰 Update Pricing
            </button>
            <button
              onClick={() => onNavigate('offers')}
              className="w-full bg-orange-50 hover:bg-orange-100 border border-orange-200 text-orange-700 font-medium py-3 px-4 rounded-lg transition"
            >
              💬 View Offers
            </button>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-bold mb-4">Recent Bookings</h3>
          <div className="space-y-3">
            <div className="border-l-4 border-blue-500 pl-4 py-2">
              <p className="font-medium text-gray-900">Deluxe Room</p>
              <p className="text-sm text-gray-500">John Smith • Mar 20-22</p>
              <p className="text-sm font-bold text-green-600 mt-1">$450</p>
            </div>
            <div className="border-l-4 border-blue-500 pl-4 py-2">
              <p className="font-medium text-gray-900">Standard Room</p>
              <p className="text-sm text-gray-500">Jane Doe • Mar 25-27</p>
              <p className="text-sm font-bold text-green-600 mt-1">$300</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
