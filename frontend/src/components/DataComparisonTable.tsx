import React from 'react';
import { DataComparisonRow } from '../types';
import { Check, AlertTriangle, HelpCircle, XCircle } from 'lucide-react';

interface Props {
  rows: DataComparisonRow[];
}

export const DataComparisonTable: React.FC<Props> = ({ rows }) => {
  if (!rows || rows.length === 0) {
    return (
      <div style={{ padding: '20px', textAlign: 'center', color: 'var(--text-muted)' }}>
        No field comparison data extracted for this document.
      </div>
    );
  }

  const getResultBadge = (res: string) => {
    switch (res) {
      case 'MATCH':
        return (
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', background: 'rgba(16, 185, 129, 0.15)', color: '#34d399', padding: '2px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 700 }}>
            <Check size={12} /> MATCH
          </span>
        );
      case 'PARTIAL MATCH':
        return (
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', background: 'rgba(59, 130, 246, 0.15)', color: '#60a5fa', padding: '2px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 700 }}>
            PARTIAL
          </span>
        );
      case 'MISMATCH':
        return (
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', background: 'rgba(239, 68, 68, 0.2)', color: '#f87171', padding: '2px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 700 }}>
            <XCircle size={12} /> MISMATCH
          </span>
        );
      case 'NOT FOUND':
        return (
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', background: 'rgba(245, 158, 11, 0.15)', color: '#fbbf24', padding: '2px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 700 }}>
            <AlertTriangle size={12} /> NOT FOUND
          </span>
        );
      default:
        return (
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', background: 'rgba(255, 255, 255, 0.05)', color: 'var(--text-dim)', padding: '2px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 600 }}>
            N/A
          </span>
        );
    }
  };

  return (
    <div style={{ background: 'var(--bg-card)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--border-subtle)', overflow: 'hidden' }}>
      <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-subtle)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h3 style={{ fontSize: '15px', fontWeight: 700, color: '#fff' }}>Document Data Comparison</h3>
          <p style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Cross-check between visible OCR text and decoded QR payload</p>
        </div>
        <span style={{ fontSize: '11px', color: '#64748b', fontWeight: 600 }}>SENSITIVE IDS MASKED</span>
      </div>

      <div style={{ overflowX: 'auto' }}>
        <table className="custom-table">
          <thead>
            <tr>
              <th style={{ width: '22%' }}>Field</th>
              <th style={{ width: '30%' }}>Extracted Visible Value</th>
              <th style={{ width: '30%' }}>Reference / QR Value</th>
              <th style={{ width: '18%' }}>Cross-Check Result</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row, idx) => (
              <tr key={idx} style={{ background: row.result === 'MISMATCH' ? 'rgba(239, 68, 68, 0.05)' : 'transparent' }}>
                <td style={{ fontWeight: 600, color: '#e2e8f0' }}>{row.field}</td>
                <td className="font-mono" style={{ color: row.result === 'MISMATCH' ? '#fca5a5' : '#cbd5e1' }}>
                  {row.extracted_value}
                </td>
                <td className="font-mono" style={{ color: row.result === 'MISMATCH' ? '#fca5a5' : '#cbd5e1' }}>
                  {row.reference_or_qr_value}
                </td>
                <td>{getResultBadge(row.result)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
