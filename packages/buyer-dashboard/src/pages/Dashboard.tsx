import { useState, useEffect } from 'react';
import { useLocation, useNavigate, Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from '../components/Layout';
import { SearchTab } from '../components/SearchTab';
import { MyOffersTab } from '../components/MyOffersTab';
import { NegotiationsTab } from '../components/NegotiationsTab';
import { BookingsTab } from '../components/BookingsTab';
import { ProfileTab } from '../components/ProfileTab';

const tabs = [
  { id: 'search', name: 'Search', icon: '🔍' },
  { id: 'offers', name: 'My Offers', icon: '💼' },
  { id: 'negotiations', name: 'Negotiations', icon: '🤝' },
  { id: 'bookings', name: 'Bookings', icon: '📅' },
  { id: 'profile', name: 'Profile', icon: '👤' },
];

export const Dashboard = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const pathSegments = location.pathname.split('/');
  const currentTab = pathSegments[pathSegments.length - 1] || 'search';
  const [activeTab, setActiveTab] = useState(currentTab);

  // Sync activeTab with URL when location changes
  useEffect(() => {
    const newTab = pathSegments[pathSegments.length - 1] || 'search';
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
        <Route index element={<Navigate to="search" replace />} />
        <Route path="search" element={<SearchTab />} />
        <Route path="offers" element={<MyOffersTab />} />
        <Route path="negotiations" element={<NegotiationsTab />} />
        <Route path="bookings" element={<BookingsTab />} />
        <Route path="profile" element={<ProfileTab />} />
      </Routes>
    </Layout>
  );
};
