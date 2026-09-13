import React from 'react';
import { Shield, LogOut, UserCheck, AlertOctagon } from 'lucide-react';
import { User, UserRole } from '../types';

interface Props {
  user: User | null;
  onRoleSwitch: (role: string) => void;
  onLogout: () => void;
}

export const Navbar: React.FC<Props> = ({ user, onRoleSwitch, onLogout }) => {
  const roles: UserRole[] = ['ADMIN', 'OFFICER', 'REVIEWER', 'VIEWER'];

  return (
    <header className="top-navbar">
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <div className="demo-banner">
          <AlertOctagon size={14} />
          <span>DEMO MODE &bull; AUTHORIZED SCREENING SYSTEM</span>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
        {/* Quick Role Switcher for seamless demonstration */}
        <div className="role-switcher-group">
          <span style={{ fontSize: '11px', color: 'var(--text-dim)', fontWeight: 600 }}>SWITCH ROLE:</span>
          {roles.map(r => (
            <button
              key={r}
              className={`role-btn ${user?.role === r ? 'active' : ''}`}
              onClick={() => onRoleSwitch(r)}
              title={`Switch session to ${r}`}
            >
              {r}
            </button>
          ))}
        </div>

        {user && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', borderLeft: '1px solid var(--border-subtle)', paddingLeft: '16px' }}>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '13px', fontWeight: 600, color: '#f1f5f9' }}>{user.full_name}</div>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>ID: {user.user_id}</div>
            </div>
            <button
              onClick={onLogout}
              className="btn btn-secondary"
              style={{ padding: '6px 10px', fontSize: '12px' }}
              title="Sign Out"
            >
              <LogOut size={14} />
            </button>
          </div>
        )}
      </div>
    </header>
  );
};
