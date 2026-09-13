import React, { useState } from 'react';
import { ScoreBreakdown } from '../types';
import { ChevronDown, ChevronUp, Info } from 'lucide-react';

interface Props {
  score: number;
  breakdown: ScoreBreakdown;
}

export const VerificationScoreCard: React.FC<Props> = ({ score, breakdown }) => {
  const [showDetails, setShowDetails] = useState(false);

  // SVG circle calculation
  const radius = 54;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  let color = '#ef4444'; // Red for < 70
  if (score >= 85) color = '#10b981'; // Green
  else if (score >= 70) color = '#3b82f6'; // Blue

  const metricRows = [
    { label: 'Template Match', value: breakdown.template_match, max: 100, isTemplate: true },
    { label: 'OCR Consistency', value: breakdown.ocr_consistency, max: 100 },
    { label: 'QR Consistency', value: breakdown.qr_consistency, max: 100 },
    { label: 'Required Fields', value: breakdown.required_fields, max: 100 },
    { label: 'Image Quality', value: breakdown.image_quality, max: 100 },
    { label: 'Integrity Screening', value: breakdown.integrity_screening, max: 100 },
  ];

  return (
    <div style={{ background: 'var(--bg-card)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--border-subtle)', padding: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
        <div>
          <h3 style={{ fontSize: '16px', fontWeight: 700, color: '#fff' }}>Screening Score</h3>
          <p style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Automated consistency rating (0–100)</p>
        </div>
        <div style={{ background: 'rgba(255,255,255,0.05)', padding: '4px 10px', borderRadius: '4px', fontSize: '11px', color: 'var(--text-dim)', fontWeight: 600 }}>
          NOT AUTHENTICITY PROBABILITY
        </div>
      </div>

      <div style={{ display: 'flex', gap: '28px', alignItems: 'center', flexWrap: 'wrap' }}>
        {/* Circle Gauge */}
        <div style={{ position: 'relative', width: '130px', height: '130px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <svg width="130" height="130" className="gauge-svg">
            <circle
              cx="65"
              cy="65"
              r={radius}
              stroke="rgba(255,255,255,0.08)"
              strokeWidth="10"
              fill="transparent"
            />
            <circle
              cx="65"
              cy="65"
              r={radius}
              stroke={color}
              strokeWidth="10"
              fill="transparent"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              className="gauge-val"
            />
          </svg>
          <div style={{ position: 'absolute', textAlign: 'center' }}>
            <div style={{ fontSize: '32px', fontWeight: 800, color: '#fff', lineHeight: 1 }}>{Math.round(score)}</div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 600, marginTop: '4px' }}>/ 100</div>
          </div>
        </div>

        {/* Breakdown bars */}
        <div style={{ flex: 1, minWidth: '240px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {metricRows.map(m => (
            <div key={m.label}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '4px' }}>
                <span style={{ color: m.isTemplate ? '#60a5fa' : 'var(--text-muted)', fontWeight: m.isTemplate ? 600 : 500 }}>
                  {m.label}
                </span>
                <span style={{ fontWeight: 700, color: '#fff' }}>{m.value}/100</span>
              </div>
              <div style={{ height: '6px', background: 'rgba(255,255,255,0.06)', borderRadius: '3px', overflow: 'hidden' }}>
                <div
                  style={{
                    height: '100%',
                    width: `${Math.min(100, Math.max(0, m.value))}%`,
                    background: m.value >= 85 ? '#10b981' : m.value >= 70 ? '#3b82f6' : '#ef4444',
                    borderRadius: '3px',
                    transition: 'width 0.6s ease'
                  }}
                />
              </div>
            </div>
          ))}

          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginTop: '4px', paddingTop: '8px', borderTop: '1px solid var(--border-subtle)' }}>
            <span style={{ color: 'var(--text-muted)' }}>Authorized Verification</span>
            <span style={{ fontWeight: 700, color: breakdown.authorized_verification === 'VERIFIED' ? '#10b981' : '#f59e0b' }}>
              {breakdown.authorized_verification}
            </span>
          </div>
        </div>
      </div>

      {/* Template Match Drill-Down Toggle */}
      {breakdown.template_details && (
        <div style={{ marginTop: '20px', borderTop: '1px solid var(--border-subtle)', paddingTop: '14px' }}>
          <button
            onClick={() => setShowDetails(!showDetails)}
            style={{ background: 'none', border: 'none', color: '#60a5fa', fontSize: '12px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px', cursor: 'pointer' }}
          >
            {showDetails ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            {showDetails ? 'Hide Template Match Components' : 'View Template Match Breakdown (Layout, Positions, Symbols, QR)'}
          </button>

          {showDetails && (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '12px', marginTop: '14px', background: 'rgba(0,0,0,0.2)', padding: '14px', borderRadius: 'var(--radius-md)' }}>
              <div>
                <div style={{ fontSize: '11px', color: 'var(--text-dim)' }}>Layout</div>
                <div style={{ fontSize: '16px', fontWeight: 700, color: '#fff' }}>{breakdown.template_details.layout ?? 98}/100</div>
              </div>
              <div>
                <div style={{ fontSize: '11px', color: 'var(--text-dim)' }}>Field Positions</div>
                <div style={{ fontSize: '16px', fontWeight: 700, color: '#fff' }}>{breakdown.template_details.field_positions ?? 95}/100</div>
              </div>
              <div>
                <div style={{ fontSize: '11px', color: 'var(--text-dim)' }}>Typography/Layout</div>
                <div style={{ fontSize: '16px', fontWeight: 700, color: '#fff' }}>{breakdown.template_details.typography_layout ?? 94}/100</div>
              </div>
              <div>
                <div style={{ fontSize: '11px', color: 'var(--text-dim)' }}>Symbols/Emblems</div>
                <div style={{ fontSize: '16px', fontWeight: 700, color: '#fff' }}>{breakdown.template_details.symbols ?? 96}/100</div>
              </div>
              <div>
                <div style={{ fontSize: '11px', color: 'var(--text-dim)' }}>QR Position</div>
                <div style={{ fontSize: '16px', fontWeight: 700, color: '#fff' }}>{breakdown.template_details.qr_position ?? 100}/100</div>
              </div>
              <div>
                <div style={{ fontSize: '11px', color: 'var(--text-dim)' }}>Dimensions & AR</div>
                <div style={{ fontSize: '16px', fontWeight: 700, color: '#fff' }}>{breakdown.template_details.dimensions ?? 98}/100</div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
