import { useState, useEffect } from 'react';
import { useLocation, useNavigate, Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from '../components/Layout';
import { DashboardTab } from '../components/DashboardTab';
import { InventoryTab } from '../components/InventoryTab';
import { OffersTab } from '../components/OffersTab';
import { BookingsTab } from '../components/BookingsTab';
import { PricingTab } from '../components/PricingTab';
import { ProfileTab } from '../components/ProfileTab';

const tabs = [
  { id: 'dashboard', name: 'Dashboard', icon: '📊' },
  { id: 'inventory', name: 'Inventory', icon: '🏠' },
  { id: 'offers', name: 'Offers', icon: '💼' },
  { id: 'bookings', name: 'Bookings', icon: '📅' },
  { id: 'pricing', name: 'Pricing', icon: '💰' },
  { id: 'profile', name: 'Profile', icon: '👤' },
];

export const Dashboard = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const pathSegments = location.pathname.split('/');
  const currentTab = pathSegments[pathSegments.length - 1] || 'dashboard';
  const [activeTab, setActiveTab] = useState(currentTab);

  // Sync activeTab with URL when location changes
  useEffect(() => {
    const newTab = pathSegments[pathSegments.length - 1] || 'dashboard';
    setActiveTab(newTab);
  }, [location.pathname]);

  // Navigate when tab changes
  const handleTabChange = (tabId: string) => {
    navigate(`/portal/${tabId}`, { replace: false });
  };

  const getTabTitle = () => {
    const tab = tabs.find(t => t.id === activeTab);
    return tab?.name || 'Dashboard';
  };

  return (
    <Layout
      tabs={tabs}
      activeTab={activeTab}
      onTabChange={handleTabChange}
      title={getTabTitle()}
    >
      <Routes>
        <Route index element={<Navigate to="dashboard" replace />} />
        <Route path="dashboard" element={<DashboardTab onNavigate={handleTabChange} />} />
        <Route path="inventory" element={<InventoryTab />} />
        <Route path="offers" element={<OffersTab />} />
        <Route path="bookings" element={<BookingsTab />} />
        <Route path="pricing" element={<PricingTab />} />
        <Route path="profile" element={<ProfileTab />} />
      </Routes>
    </Layout>
  );
};
