import React from 'react';
import { LayoutDashboard, FileCheck2, Layers, History, FileText, Settings, ShieldAlert, Users } from 'lucide-react';
import { User } from '../types';

interface Props {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  user: User | null;
}

export const Sidebar: React.FC<Props> = ({ activeTab, setActiveTab, user }) => {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'verify', label: 'Verify Document', icon: FileCheck2 },
    { id: 'bulk', label: 'Bulk Screening', icon: Layers },
    { id: 'history', label: 'Verification History', icon: History },
    { id: 'templates', label: 'Reference Templates', icon: FileText, adminOnly: false },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="logo-badge">
          <FileCheck2 size={22} />
        </div>
        <div className="app-title-group">
          <h1>DocScreen AI</h1>
          <p>Identity Verification</p>
        </div>
      </div>

      <ul className="nav-links">
        {menuItems.map(item => {
          const Icon = item.icon;
          return (
            <li
              key={item.id}
              className={`nav-item ${activeTab === item.id ? 'active' : ''}`}
              onClick={() => setActiveTab(item.id)}
            >
              <Icon size={18} />
              <span>{item.label}</span>
            </li>
          );
        })}
      </ul>

      <div className="sidebar-footer">
        <div className="officer-badge">
          <div className="officer-avatar">
            {user ? user.full_name.charAt(0).toUpperCase() : 'O'}
          </div>
          <div className="officer-info">
            <div className="officer-name">{user?.full_name || 'Officer'}</div>
            <div className="officer-role-tag">{user?.role || 'OFFICER'}</div>
          </div>
        </div>
      </div>
    </aside>
  );
};
