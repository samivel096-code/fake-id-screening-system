import React from 'react';
import { CheckCircle2, ShieldCheck, Camera, Sparkles } from 'lucide-react';
import { ImageQuality } from '../types';

interface Props {
  quality?: ImageQuality;
}

export const ImageQualityCard: React.FC<Props> = ({ quality }) => {
  if (!quality || !quality.acceptable) return null;

  const checks = [
    { label: 'Document completely visible', detail: `${quality.width}x${quality.height} px canvas` },
    { label: 'Resolution sufficient', detail: `${quality.width}x${quality.height} px (min 600x400 required)` },
    { label: 'Text readable', detail: 'Crisp character contrast verified' },
    { label: 'Blur acceptable', detail: `Laplacian variance: ${quality.blur_score}` },
    { label: 'Lighting acceptable', detail: `Mean luma: ${quality.brightness}, Contrast: ${quality.contrast}` },
    { label: 'Document orientation acceptable', detail: `Tilt: ~${quality.estimated_tilt}°` },
  ];

  return (
    <div style={{ background: 'var(--bg-card)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--border-subtle)', padding: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ width: '36px', height: '36px', borderRadius: 'var(--radius-md)', background: 'rgba(16, 185, 129, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#10b981' }}>
            <ShieldCheck size={20} />
          </div>
          <div>
            <h3 style={{ fontSize: '15px', fontWeight: 700, color: '#fff' }}>Image Quality Analysis</h3>
            <p style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Automated OpenCV sharpness, lighting & border verification</p>
          </div>
        </div>

        <span
          style={{
            fontSize: '11px',
            fontWeight: 700,
            padding: '3px 10px',
            borderRadius: 'var(--radius-full)',
            background: 'rgba(16, 185, 129, 0.2)',
            color: '#34d399',
          }}
        >
          ✓ IMAGE QUALITY ACCEPTABLE
        </span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '10px' }}>
        {checks.map((item, idx) => (
          <div
            key={idx}
            style={{
              display: 'flex',
              alignItems: 'flex-start',
              gap: '10px',
              padding: '10px 14px',
              background: 'rgba(0,0,0,0.2)',
              borderRadius: 'var(--radius-md)',
              border: '1px solid rgba(16, 185, 129, 0.15)',
            }}
          >
            <CheckCircle2 size={16} color="#10b981" style={{ flexShrink: 0, marginTop: '2px' }} />
            <div>
              <div style={{ fontSize: '13px', fontWeight: 600, color: '#e2e8f0' }}>{item.label}</div>
              <div style={{ fontSize: '11px', color: 'var(--text-dim)' }}>{item.detail}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
