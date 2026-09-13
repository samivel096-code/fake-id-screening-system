import React, { useState, useEffect } from 'react';
import { api } from './services/api';
import { User } from './types';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { VerifyDocumentPage } from './pages/VerifyDocumentPage';
import { BulkScreeningPage } from './pages/BulkScreeningPage';
import { HistoryPage } from './pages/HistoryPage';
import { TemplatesPage } from './pages/TemplatesPage';

export default function App() {
  const [user, setUser] = useState<User | null>(api.getStoredUser());
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [inspectVerificationId, setInspectVerificationId] = useState<string | null>(null);

  useEffect(() => {
    // If no user is stored, check backend session or default to demo officer
    if (!user) {
      api.quickSwitchRole('OFFICER')
        .then(res => setUser(res.user))
        .catch(console.error);
    }
  }, []);

  const handleRoleSwitch = async (role: string) => {
    try {
      const res = await api.quickSwitchRole(role);
      setUser(res.user);
    } catch (e: any) {
      alert(e.message || 'Failed to switch role');
    }
  };

  const handleLogout = () => {
    api.logout();
    setUser(null);
  };

  const handleViewRecord = (id: string) => {
    setInspectVerificationId(id);
    setActiveTab('verify');
  };

  if (!user) {
    return <LoginPage onLoginSuccess={setUser} />;
  }

  return (
    <div className="app-layout">
      {/* Sidebar Navigation */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        user={user}
      />

      {/* Main Workspace */}
      <div className="main-wrapper">
        <Navbar
          user={user}
          onRoleSwitch={handleRoleSwitch}
          onLogout={handleLogout}
        />

        <main style={{ flex: 1 }}>
          {activeTab === 'dashboard' && (
            <DashboardPage
              onNavigateToVerify={() => setActiveTab('verify')}
              onViewRecord={handleViewRecord}
            />
          )}

          {activeTab === 'verify' && (
            <VerifyDocumentPage
              initialVerificationId={inspectVerificationId}
              onClearInitialId={() => setInspectVerificationId(null)}
            />
          )}

          {activeTab === 'bulk' && (
            <BulkScreeningPage onViewRecord={handleViewRecord} />
          )}

          {activeTab === 'history' && (
            <HistoryPage onViewRecord={handleViewRecord} />
          )}

          {activeTab === 'templates' && (
            <TemplatesPage user={user} />
          )}
        </main>
      </div>
    </div>
  );
}
