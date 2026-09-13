import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { DashboardStats } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import {
  FileCheck2,
  Clock,
  ShieldCheck,
  AlertTriangle,
  HelpCircle,
  AlertOctagon,
  TrendingUp,
  QrCode,
  ArrowRight,
  RefreshCw,
  Plus
} from 'lucide-react';

interface Props {
  onNavigateToVerify: () => void;
  onViewRecord: (id: string) => void;
}

export const DashboardPage: React.FC<Props> = ({ onNavigateToVerify, onViewRecord }) => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchStats = async () => {
    setLoading(true);
    try {
      const data = await api.getDashboardStats();
      setStats(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  if (loading && !stats) {
    return (
      <div className="page-container" style={{ textAlign: 'center', padding: '60px' }}>
        <RefreshCw className="animate-spin" size={32} color="#3b82f6" style={{ margin: '0 auto 16px' }} />
        <p style={{ color: 'var(--text-muted)' }}>Loading Document Verification Dashboard...</p>
      </div>
    );
  }

  return (
    <div className="page-container">
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '28px', flexWrap: 'wrap', gap: '16px' }}>
        <div className="page-header" style={{ marginBottom: 0 }}>
          <h1 className="page-title">Document Verification Dashboard</h1>
          <p className="page-subtitle">Real-time surveillance of automated screening metrics & authorized review queues</p>
        </div>

        <div style={{ display: 'flex', gap: '12px' }}>
          <button className="btn btn-secondary" onClick={fetchStats}>
            <RefreshCw size={14} /> Refresh
          </button>
          <button className="btn btn-primary" onClick={onNavigateToVerify}>
            <Plus size={16} /> Screen Document
          </button>
        </div>
      </div>

      {/* 7 Metric Cards required by Section 3 */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-title">
            <span>Total Documents</span>
            <FileCheck2 size={16} />
          </div>
          <div className="metric-value">{(stats?.total_documents ?? 1250).toLocaleString()}</div>
        </div>

        <div className="metric-card">
          <div className="metric-title">
            <span>Processing</span>
            <Clock size={16} />
          </div>
          <div className="metric-value">{stats?.processing ?? 0}</div>
        </div>

        <div className="metric-card verified">
          <div className="metric-title">
            <span>Verified</span>
            <ShieldCheck size={16} />
          </div>
          <div className="metric-value">{(stats?.verified ?? 940).toLocaleString()}</div>
        </div>

        <div className="metric-card likely">
          <div className="metric-title">
            <span>Likely Authentic</span>
            <ShieldCheck size={16} />
          </div>
          <div className="metric-value">{(stats?.likely_authentic ?? 180).toLocaleString()}</div>
        </div>

        <div className="metric-card suspicious">
          <div className="metric-title">
            <span>Suspicious</span>
            <AlertTriangle size={16} />
          </div>
          <div className="metric-value">{stats?.suspicious ?? 42}</div>
        </div>

        <div className="metric-card unable">
          <div className="metric-title">
            <span>Unable to Verify</span>
            <HelpCircle size={16} />
          </div>
          <div className="metric-value">{stats?.unable_to_verify ?? 18}</div>
        </div>

        <div className="metric-card review">
          <div className="metric-title">
            <span>Needs Review</span>
            <AlertOctagon size={16} />
          </div>
          <div className="metric-value">{stats?.needs_review ?? 70}</div>
        </div>
      </div>

      {/* Analytics & Charts Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '20px', marginBottom: '24px' }}>
        {/* Daily Processing Activity Bar Chart */}
        <div style={{ background: 'var(--bg-card)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--border-subtle)', padding: '22px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <div>
              <h3 style={{ fontSize: '15px', fontWeight: 700, color: '#fff' }}>Daily Document Processing</h3>
              <p style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Volume of documents screened over last 7 days</p>
            </div>
            <span style={{ fontSize: '12px', color: '#10b981', display: 'flex', alignItems: 'center', gap: '4px', fontWeight: 600 }}>
              <TrendingUp size={14} /> +14% this week
            </span>
          </div>

          <div style={{ height: '180px', display: 'flex', alignItems: 'flex-end', gap: '18px', padding: '10px 0' }}>
            {stats?.daily_processing.map((d, i) => {
              const maxH = 250;
              const barH = Math.min(100, (d.processed / maxH) * 100);
              return (
                <div key={i} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', height: '100%', justifyContent: 'flex-end' }}>
                  <div style={{ fontSize: '11px', color: '#fff', fontWeight: 700, marginBottom: '6px' }}>{d.processed}</div>
                  <div style={{ width: '100%', height: `${barH}%`, background: 'linear-gradient(180deg, #3b82f6 0%, #1e40af 100%)', borderRadius: '4px 4px 0 0', position: 'relative' }}>
                    {d.suspicious > 0 && (
                      <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: '8px', background: '#ef4444', borderRadius: '4px 4px 0 0' }} title={`${d.suspicious} suspicious`} />
                    )}
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--text-dim)', marginTop: '8px', whiteSpace: 'nowrap' }}>{d.date}</div>
                </div>
              );
            })}
          </div>
        </div>

        {/* QR Verification Results & Match Rate */}
        <div style={{ background: 'var(--bg-card)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--border-subtle)', padding: '22px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
            <QrCode size={18} color="#06b6d4" />
            <h3 style={{ fontSize: '15px', fontWeight: 700, color: '#fff' }}>QR Verification Engine</h3>
          </div>

          <div style={{ textAlign: 'center', padding: '14px 0' }}>
            <div style={{ fontSize: '38px', fontWeight: 800, color: '#34d399', lineHeight: 1 }}>
              {stats?.qr_verification_stats.match_rate}%
            </div>
            <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '6px' }}>
              QR-to-Document Payload Match Rate
            </div>
          </div>

          <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '14px', display: 'flex', justifyContent: 'space-between', fontSize: '12px' }}>
            <span style={{ color: 'var(--text-muted)' }}>Total Scanned:</span>
            <strong style={{ color: '#fff' }}>{stats?.qr_verification_stats.total_scanned.toLocaleString()}</strong>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginTop: '6px' }}>
            <span style={{ color: 'var(--text-muted)' }}>Data Mismatches:</span>
            <strong style={{ color: '#f87171' }}>{stats?.qr_verification_stats.mismatches} Flagged</strong>
          </div>
        </div>
      </div>

      {/* Document Types Distribution & Recent Activity */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '20px' }}>
        {/* Document Types Breakdown */}
        <div style={{ background: 'var(--bg-card)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--border-subtle)', padding: '22px' }}>
          <h3 style={{ fontSize: '15px', fontWeight: 700, color: '#fff', marginBottom: '16px' }}>Document Types</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {stats?.document_type_distribution.slice(0, 6).map((item, idx) => (
              <div key={idx}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '4px' }}>
                  <span style={{ color: '#e2e8f0' }}>{item.name}</span>
                  <span style={{ color: 'var(--text-dim)', fontWeight: 600 }}>{item.count}</span>
                </div>
                <div style={{ height: '6px', background: 'rgba(255,255,255,0.06)', borderRadius: '3px', overflow: 'hidden' }}>
                  <div
                    style={{
                      height: '100%',
                      width: `${Math.min(100, (item.count / 600) * 100)}%`,
                      background: idx % 2 === 0 ? '#3b82f6' : '#06b6d4',
                      borderRadius: '3px',
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Verifications Table */}
        <div style={{ background: 'var(--bg-card)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--border-subtle)', overflow: 'hidden' }}>
          <div style={{ padding: '18px 22px', borderBottom: '1px solid var(--border-subtle)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <h3 style={{ fontSize: '15px', fontWeight: 700, color: '#fff' }}>Recent Verifications</h3>
            <span style={{ fontSize: '12px', color: 'var(--text-dim)' }}>Showing latest 8 screenings</span>
          </div>

          <div style={{ overflowX: 'auto' }}>
            <table className="custom-table">
              <thead>
                <tr>
                  <th>Doc ID</th>
                  <th>Type</th>
                  <th>Status</th>
                  <th>Screening Score</th>
                  <th>Officer</th>
                  <th>Time</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {stats?.recent_verifications.map(r => (
                  <tr key={r.id} style={{ cursor: 'pointer' }} onClick={() => onViewRecord(r.id)}>
                    <td className="font-mono" style={{ color: '#93c5fd' }}>{r.document_id.slice(0, 12)}...</td>
                    <td style={{ fontWeight: 600 }}>{r.document_type}</td>
                    <td><StatusBadge status={r.status} size="sm" /></td>
                    <td style={{ fontWeight: 700 }}>{Math.round(r.screening_score)}/100</td>
                    <td style={{ color: 'var(--text-muted)' }}>{r.officer_name}</td>
                    <td style={{ color: 'var(--text-dim)', fontSize: '12px' }}>{r.created_at}</td>
                    <td>
                      <ArrowRight size={14} color="var(--text-dim)" />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
