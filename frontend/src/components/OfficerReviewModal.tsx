import React, { useState } from 'react';
import { X, ShieldCheck, AlertTriangle, Edit3 } from 'lucide-react';
import { api } from '../services/api';

interface Props {
  verificationId: string;
  currentStatus: string;
  onClose: () => void;
  onSuccess: (result: any) => void;
}

export const OfficerReviewModal: React.FC<Props> = ({ verificationId, currentStatus, onClose, onSuccess }) => {
  const [decision, setDecision] = useState<'APPROVED' | 'FLAGGED' | 'OVERRIDDEN'>('APPROVED');
  const [notes, setNotes] = useState('');
  const [overrideStatus, setOverrideStatus] = useState(currentStatus);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!notes.trim()) {
      setError('Officer notes are required for audit trail.');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const res = await api.submitOfficerReview(
        verificationId,
        decision,
        notes,
        decision === 'OVERRIDDEN' ? overrideStatus : undefined
      );
      onSuccess(res);
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to submit review');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-backdrop">
      <div className="modal-dialog">
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Edit3 size={18} color="#60a5fa" />
            <h3 style={{ fontSize: '16px', fontWeight: 700, color: '#fff' }}>Officer Manual Review Decision</h3>
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
            <X size={18} />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            {error && (
              <div style={{ padding: '10px 14px', background: 'rgba(239,68,68,0.15)', border: '1px solid #ef4444', borderRadius: 'var(--radius-sm)', color: '#f87171', fontSize: '13px', marginBottom: '16px' }}>
                {error}
              </div>
            )}

            <div style={{ marginBottom: '16px' }}>
              <label style={{ display: 'block', fontSize: '12px', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '8px' }}>
                Review Decision
              </label>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '10px' }}>
                <button
                  type="button"
                  className={`btn ${decision === 'APPROVED' ? 'btn-primary' : 'btn-secondary'}`}
                  style={{ fontSize: '12px', padding: '8px' }}
                  onClick={() => setDecision('APPROVED')}
                >
                  <ShieldCheck size={14} /> Approve
                </button>
                <button
                  type="button"
                  className={`btn ${decision === 'FLAGGED' ? 'btn-danger' : 'btn-secondary'}`}
                  style={{ fontSize: '12px', padding: '8px' }}
                  onClick={() => setDecision('FLAGGED')}
                >
                  <AlertTriangle size={14} /> Flag Altered
                </button>
                <button
                  type="button"
                  className={`btn ${decision === 'OVERRIDDEN' ? 'btn-primary' : 'btn-secondary'}`}
                  style={{ fontSize: '12px', padding: '8px' }}
                  onClick={() => setDecision('OVERRIDDEN')}
                >
                  Override Status
                </button>
              </div>
            </div>

            {decision === 'OVERRIDDEN' && (
              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', fontSize: '12px', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '6px' }}>
                  Target Status
                </label>
                <select
                  value={overrideStatus}
                  onChange={e => setOverrideStatus(e.target.value)}
                  style={{ width: '100%', background: 'var(--bg-dark)', border: '1px solid var(--border-subtle)', color: '#fff', padding: '8px 12px', borderRadius: 'var(--radius-md)' }}
                >
                  <option value="VERIFIED">VERIFIED</option>
                  <option value="LIKELY AUTHENTIC">LIKELY AUTHENTIC</option>
                  <option value="SUSPICIOUS / LIKELY ALTERED">SUSPICIOUS / LIKELY ALTERED</option>
                  <option value="UNABLE TO VERIFY">UNABLE TO VERIFY</option>
                </select>
              </div>
            )}

            <div style={{ marginBottom: '16px' }}>
              <label style={{ display: 'block', fontSize: '12px', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '6px' }}>
                Official Officer Justification & Notes *
              </label>
              <textarea
                rows={4}
                value={notes}
                onChange={e => setNotes(e.target.value)}
                placeholder="State your findings regarding design match, physical inspection, or authorized cross-checks..."
                style={{ width: '100%', background: 'var(--bg-dark)', border: '1px solid var(--border-subtle)', color: '#fff', padding: '10px 14px', borderRadius: 'var(--radius-md)', fontSize: '13px', resize: 'vertical' }}
              />
            </div>

            <div style={{ fontSize: '11px', color: 'var(--text-dim)' }}>
              Note: This action will be permanently recorded in the immutable audit log under your Officer ID and timestamp.
            </div>
          </div>

          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Recording Decision...' : 'Submit Official Review'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
