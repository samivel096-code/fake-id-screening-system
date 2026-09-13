import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { StatusBadge } from '../components/StatusBadge';
import { Search, Filter, ArrowRight, RefreshCw, Printer } from 'lucide-react';

interface HistoryRecord {
  id: string;
  document_id: string;
  document_type: string;
  status: string;
  screening_score: number;
  template_match_score: number;
  qr_consistency_score: number;
  officer_name: string;
  manual_review_needed: boolean;
  officer_review_decision?: string;
  created_at: string;
}

interface Props {
  onViewRecord: (id: string) => void;
}

export const HistoryPage: React.FC<Props> = ({ onViewRecord }) => {
  const [history, setHistory] = useState<HistoryRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const data = await api.getVerificationHistory(search, statusFilter, typeFilter);
      setHistory(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [statusFilter, typeFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchHistory();
  };

  return (
    <div className="page-container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px', flexWrap: 'wrap', gap: '16px' }}>
        <div className="page-header" style={{ marginBottom: 0 }}>
          <h1 className="page-title">Verification History & Audit Log</h1>
          <p className="page-subtitle">Search, filter, and inspect past automated screenings and officer reviews</p>
        </div>

        <button className="btn btn-secondary" onClick={() => window.print()}>
          <Printer size={14} /> Export Audit Records
        </button>
      </div>

      {/* Filter & Search Toolbar */}
      <div style={{ background: 'var(--bg-card)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--border-subtle)', padding: '16px 20px', marginBottom: '24px', display: 'flex', gap: '14px', flexWrap: 'wrap', alignItems: 'center' }}>
        <form onSubmit={handleSearchSubmit} style={{ flex: 1, minWidth: '220px', display: 'flex', position: 'relative' }}>
          <input
            type="text"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search by Document ID, Officer, or Type..."
            style={{ width: '100%', background: 'var(--bg-dark)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '9px 12px 9px 36px', color: '#fff', fontSize: '13px' }}
          />
          <Search size={16} color="var(--text-dim)" style={{ position: 'absolute', left: '12px', top: '11px' }} />
        </form>

        <select
          value={statusFilter}
          onChange={e => setStatusFilter(e.target.value)}
          style={{ background: 'var(--bg-dark)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '9px 12px', color: '#fff', fontSize: '13px' }}
        >
          <option value="">All Statuses</option>
          <option value="VERIFIED">VERIFIED</option>
          <option value="LIKELY AUTHENTIC">LIKELY AUTHENTIC</option>
          <option value="SUSPICIOUS / LIKELY ALTERED">SUSPICIOUS / ALTERED</option>
          <option value="UNABLE TO VERIFY">UNABLE TO VERIFY</option>
        </select>

        <select
          value={typeFilter}
          onChange={e => setTypeFilter(e.target.value)}
          style={{ background: 'var(--bg-dark)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '9px 12px', color: '#fff', fontSize: '13px' }}
        >
          <option value="">All Document Types</option>
          <option value="Aadhaar">Aadhaar</option>
          <option value="PAN Card">PAN Card</option>
          <option value="Driving Licence">Driving Licence</option>
          <option value="Passport">Passport</option>
          <option value="Birth Certificate">Birth Certificate</option>
        </select>

        <button className="btn btn-secondary" onClick={fetchHistory}>
          <RefreshCw size={14} /> Refresh
        </button>
      </div>

      {/* History Table */}
      <div style={{ background: 'var(--bg-card)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--border-subtle)', overflow: 'hidden' }}>
        <div style={{ overflowX: 'auto' }}>
          <table className="custom-table">
            <thead>
              <tr>
                <th>Verification ID</th>
                <th>Date & Time</th>
                <th>Officer</th>
                <th>Document Type</th>
                <th>Screening Outcome</th>
                <th>Screening Score</th>
                <th>Template Match</th>
                <th>QR Match</th>
                <th>Review Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {history.length === 0 ? (
                <tr>
                  <td colSpan={10} style={{ textAlign: 'center', padding: '36px', color: 'var(--text-muted)' }}>
                    No screening records match the query.
                  </td>
                </tr>
              ) : (
                history.map(r => (
                  <tr key={r.id}>
                    <td className="font-mono" style={{ color: '#93c5fd' }}>{r.id.slice(0, 10)}...</td>
                    <td style={{ color: 'var(--text-dim)', fontSize: '12px' }}>
                      {new Date(r.created_at).toLocaleString()}
                    </td>
                    <td style={{ fontWeight: 600, color: '#e2e8f0' }}>{r.officer_name}</td>
                    <td style={{ color: '#fff' }}>{r.document_type}</td>
                    <td><StatusBadge status={r.status} size="sm" /></td>
                    <td style={{ fontWeight: 700, color: '#fff' }}>{Math.round(r.screening_score)}/100</td>
                    <td style={{ color: '#60a5fa', fontWeight: 600 }}>{Math.round(r.template_match_score)}%</td>
                    <td style={{ color: r.qr_consistency_score >= 80 ? '#34d399' : '#f87171', fontWeight: 600 }}>
                      {Math.round(r.qr_consistency_score)}%
                    </td>
                    <td>
                      {r.officer_review_decision ? (
                        <span style={{ fontSize: '11px', color: '#34d399', fontWeight: 600 }}>
                          Reviewed ({r.officer_review_decision})
                        </span>
                      ) : r.manual_review_needed ? (
                        <span style={{ fontSize: '11px', color: '#f59e0b', fontWeight: 600 }}>
                          Pending Review
                        </span>
                      ) : (
                        <span style={{ fontSize: '11px', color: 'var(--text-dim)' }}>
                          Automated
                        </span>
                      )}
                    </td>
                    <td>
                      <button
                        className="btn btn-secondary"
                        style={{ padding: '4px 8px', fontSize: '11px' }}
                        onClick={() => onViewRecord(r.id)}
                      >
                        Inspect <ArrowRight size={12} />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
