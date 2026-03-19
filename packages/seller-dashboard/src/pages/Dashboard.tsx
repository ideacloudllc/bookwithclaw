import { useState } from 'react';
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
  const [activeTab, setActiveTab] = useState('dashboard');

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <DashboardTab onNavigate={setActiveTab} />;
      case 'inventory':
        return <InventoryTab />;
      case 'offers':
        return <OffersTab />;
      case 'bookings':
        return <BookingsTab />;
      case 'pricing':
        return <PricingTab />;
      case 'profile':
        return <ProfileTab />;
      default:
        return <DashboardTab onNavigate={setActiveTab} />;
    }
  };

  const getTabTitle = () => {
    const tab = tabs.find(t => t.id === activeTab);
    return tab?.name || 'Dashboard';
  };

  return (
    <Layout
      tabs={tabs}
      activeTab={activeTab}
      onTabChange={setActiveTab}
      title={getTabTitle()}
    >
      {renderContent()}
    </Layout>
  );
};
