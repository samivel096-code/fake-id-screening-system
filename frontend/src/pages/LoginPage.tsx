import React, { useState } from 'react';
import { ShieldCheck, Lock, Mail, UserCheck, AlertCircle } from 'lucide-react';
import { api } from '../services/api';
import { User } from '../types';

interface Props {
  onLoginSuccess: (user: User) => void;
}

export const LoginPage: React.FC<Props> = ({ onLoginSuccess }) => {
  const [userIdOrEmail, setUserIdOrEmail] = useState('officer@screening.gov');
  const [password, setPassword] = useState('Officer@123');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await api.login(userIdOrEmail, password);
      onLoginSuccess(res.user);
    } catch (err: any) {
      setError(err.message || 'Invalid credentials');
    } finally {
      setLoading(false);
    }
  };

  const autofill = (email: string, pwd: string) => {
    setUserIdOrEmail(email);
    setPassword(pwd);
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px', background: 'radial-gradient(ellipse at top, #172554 0%, #090d16 70%)' }}>
      <div style={{ maxWidth: '440px', width: '100%', background: 'var(--bg-panel)', border: '1px solid var(--border-active)', borderRadius: 'var(--radius-lg)', padding: '36px', boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.7)' }}>
        <div style={{ textAlign: 'center', marginBottom: '28px' }}>
          <div style={{ width: '52px', height: '52px', borderRadius: 'var(--radius-md)', background: 'linear-gradient(135deg, #2563eb, #06b6d4)', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', color: '#fff', marginBottom: '14px', boxShadow: '0 0 20px rgba(37, 99, 235, 0.4)' }}>
            <ShieldCheck size={28} />
          </div>
          <h2 style={{ fontSize: '20px', fontWeight: 800, color: '#fff' }}>Official Document Screening</h2>
          <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginTop: '4px' }}>
            Authorized Identity & Reference Template Inspection System
          </p>
        </div>

        {error && (
          <div style={{ padding: '12px', background: 'rgba(239, 68, 68, 0.15)', border: '1px solid #ef4444', borderRadius: 'var(--radius-md)', color: '#f87171', fontSize: '13px', display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '20px' }}>
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleLogin}>
          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '6px' }}>
              Email / User ID
            </label>
            <div style={{ position: 'relative' }}>
              <input
                type="text"
                required
                value={userIdOrEmail}
                onChange={e => setUserIdOrEmail(e.target.value)}
                placeholder="e.g. officer@screening.gov"
                style={{ width: '100%', background: 'var(--bg-dark)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '10px 14px 10px 38px', color: '#fff', fontSize: '14px' }}
              />
              <Mail size={16} color="var(--text-dim)" style={{ position: 'absolute', left: '12px', top: '13px' }} />
            </div>
          </div>

          <div style={{ marginBottom: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
              <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                Password
              </label>
              <span
                style={{ fontSize: '12px', color: '#60a5fa', cursor: 'pointer' }}
                onClick={() => alert('Demo System: Use the 1-click role buttons below to autofill valid credentials.')}
              >
                Forgot Password?
              </span>
            </div>
            <div style={{ position: 'relative' }}>
              <input
                type="password"
                required
                value={password}
                onChange={e => setPassword(e.target.value)}
                style={{ width: '100%', background: 'var(--bg-dark)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '10px 14px 10px 38px', color: '#fff', fontSize: '14px' }}
              />
              <Lock size={16} color="var(--text-dim)" style={{ position: 'absolute', left: '12px', top: '13px' }} />
            </div>
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            style={{ width: '100%', padding: '12px', fontSize: '14px', marginBottom: '24px' }}
            disabled={loading}
          >
            {loading ? 'Authenticating...' : 'Sign In'}
          </button>
        </form>

        {/* Demo Roles Quick Fill */}
        <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '18px' }}>
          <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: '10px', textAlign: 'center' }}>
            Demo Mode: Quick Fill Credentials
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
            <button
              type="button"
              className="btn btn-secondary"
              style={{ fontSize: '11px', padding: '6px 8px' }}
              onClick={() => autofill('officer@screening.gov', 'Officer@123')}
            >
              Officer (Priya)
            </button>
            <button
              type="button"
              className="btn btn-secondary"
              style={{ fontSize: '11px', padding: '6px 8px' }}
              onClick={() => autofill('admin@screening.gov', 'Admin@123')}
            >
              Administrator
            </button>
            <button
              type="button"
              className="btn btn-secondary"
              style={{ fontSize: '11px', padding: '6px 8px' }}
              onClick={() => autofill('reviewer@screening.gov', 'Reviewer@123')}
            >
              Reviewer (Arun)
            </button>
            <button
              type="button"
              className="btn btn-secondary"
              style={{ fontSize: '11px', padding: '6px 8px' }}
              onClick={() => autofill('viewer@screening.gov', 'Viewer@123')}
            >
              Viewer (Audit)
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
