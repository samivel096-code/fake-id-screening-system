import React from 'react';
import { QrCode, CheckCircle2, AlertTriangle, AlertOctagon, HelpCircle, ShieldAlert } from 'lucide-react';
import { VerificationResult } from '../types';
import { maskIdentifier } from '../utils/masking';

interface Props {
  qrAnalysis: VerificationResult['qr_analysis'];
  extractedFields: Record<string, any>;
  hasMismatch: boolean;
}

export const QRResult: React.FC<Props> = ({ qrAnalysis, extractedFields, hasMismatch }) => {
  const isDetected = qrAnalysis.detected;
  const isReadable = qrAnalysis.readable;
  const dataAvailable = qrAnalysis.data_available ?? Boolean(qrAnalysis.parsed_data && Object.keys(qrAnalysis.parsed_data).length > 0);
  const matchStatus = qrAnalysis.visible_data_match || (hasMismatch ? 'MISMATCH' : 'MATCH');
  const authStatus = qrAnalysis.authorized_verification || 'NOT AVAILABLE (DEMO ONLY)';
  const discrepancies = qrAnalysis.discrepancies || [];

  return (
    <div style={{ background: 'var(--bg-card)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--border-subtle)', padding: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ width: '36px', height: '36px', borderRadius: 'var(--radius-md)', background: 'rgba(59, 130, 246, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#60a5fa' }}>
            <QrCode size={20} />
          </div>
          <div>
            <h3 style={{ fontSize: '15px', fontWeight: 700, color: '#fff' }}>QR Verification</h3>
            <p style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Cryptographic & cross-data comparison screening</p>
          </div>
        </div>

        <span
          style={{
            fontSize: '11px',
            fontWeight: 700,
            padding: '3px 10px',
            borderRadius: 'var(--radius-full)',
            background: hasMismatch
              ? 'rgba(239, 68, 68, 0.2)'
              : isDetected
              ? 'rgba(16, 185, 129, 0.2)'
              : 'rgba(245, 158, 11, 0.2)',
            color: hasMismatch ? '#f87171' : isDetected ? '#34d399' : '#fbbf24',
          }}
        >
          {hasMismatch ? '⚠ MISMATCH DETECTED' : isDetected ? '✓ SCANNED' : 'NOT PRESENT'}
        </span>
      </div>

      {/* Grid of Status Parameters required by Section 15 */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '12px', marginBottom: '18px' }}>
        <div style={{ background: 'rgba(0,0,0,0.25)', padding: '10px 14px', borderRadius: 'var(--radius-md)' }}>
          <div style={{ fontSize: '11px', color: 'var(--text-dim)', fontWeight: 600 }}>QR CODE</div>
          <div style={{ fontSize: '14px', fontWeight: 700, color: isDetected ? '#34d399' : '#f87171', marginTop: '2px' }}>
            {isDetected ? 'DETECTED' : 'NOT DETECTED'}
          </div>
        </div>

        <div style={{ background: 'rgba(0,0,0,0.25)', padding: '10px 14px', borderRadius: 'var(--radius-md)' }}>
          <div style={{ fontSize: '11px', color: 'var(--text-dim)', fontWeight: 600 }}>READABLE</div>
          <div style={{ fontSize: '14px', fontWeight: 700, color: isReadable ? '#34d399' : '#f87171', marginTop: '2px' }}>
            {isReadable ? 'YES' : 'NO'}
          </div>
        </div>

        <div style={{ background: 'rgba(0,0,0,0.25)', padding: '10px 14px', borderRadius: 'var(--radius-md)' }}>
          <div style={{ fontSize: '11px', color: 'var(--text-dim)', fontWeight: 600 }}>DATA</div>
          <div style={{ fontSize: '14px', fontWeight: 700, color: dataAvailable ? '#34d399' : '#f87171', marginTop: '2px' }}>
            {dataAvailable ? 'AVAILABLE' : 'NOT AVAILABLE'}
          </div>
        </div>

        <div style={{ background: 'rgba(0,0,0,0.25)', padding: '10px 14px', borderRadius: 'var(--radius-md)' }}>
          <div style={{ fontSize: '11px', color: 'var(--text-dim)', fontWeight: 600 }}>VISIBLE DATA MATCH</div>
          <div style={{ fontSize: '14px', fontWeight: 700, color: matchStatus === 'MATCH' ? '#34d399' : matchStatus === 'MISMATCH' ? '#f87171' : '#fbbf24', marginTop: '2px' }}>
            {matchStatus}
          </div>
        </div>

        <div style={{ background: 'rgba(0,0,0,0.25)', padding: '10px 14px', borderRadius: 'var(--radius-md)' }}>
          <div style={{ fontSize: '11px', color: 'var(--text-dim)', fontWeight: 600 }}>AUTHORIZED VERIFICATION</div>
          <div style={{ fontSize: '12px', fontWeight: 700, color: authStatus.includes('VERIFIED') ? '#34d399' : '#f59e0b', marginTop: '4px' }}>
            {authStatus}
          </div>
        </div>
      </div>

      {/* Mismatch Alert Box required by Section 16 */}
      {hasMismatch && (
        <div style={{ background: 'rgba(239, 68, 68, 0.12)', border: '1px solid #ef4444', borderRadius: 'var(--radius-md)', padding: '16px', marginBottom: '14px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#f87171', fontWeight: 700, fontSize: '13px', marginBottom: '8px' }}>
            <ShieldAlert size={18} />
            <span>QR INFORMATION MISMATCH</span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', background: 'rgba(0,0,0,0.3)', padding: '12px', borderRadius: 'var(--radius-sm)', marginBottom: '10px' }}>
            <div>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Visible Document Name</div>
              <div style={{ fontSize: '13px', fontWeight: 700, color: '#fff' }}>
                {extractedFields?.name || 'Not detected in OCR'}
              </div>
            </div>
            <div>
              <div style={{ fontSize: '11px', color: '#fca5a5' }}>QR Encoded Name</div>
              <div style={{ fontSize: '13px', fontWeight: 700, color: '#f87171' }}>
                {qrAnalysis.parsed_data?.name || 'Different / Tampered'}
              </div>
            </div>
          </div>

          <div style={{ fontSize: '12px', color: '#fca5a5', lineHeight: 1.5 }}>
            &ldquo;The information encoded in the QR code does not match the corresponding visible document information.&rdquo;
          </div>
        </div>
      )}

      {/* Decoded QR Raw Payload Drawer */}
      {qrAnalysis.raw_data && (
        <details style={{ marginTop: '12px' }}>
          <summary style={{ fontSize: '12px', color: '#60a5fa', cursor: 'pointer', fontWeight: 600 }}>
            View Decoded QR Payload Data ({qrAnalysis.format || 'Standard'})
          </summary>
          <pre
            style={{
              background: 'rgba(0,0,0,0.4)',
              padding: '12px',
              borderRadius: 'var(--radius-md)',
              fontSize: '11px',
              color: '#93c5fd',
              marginTop: '8px',
              overflowX: 'auto',
              fontFamily: 'var(--font-mono)'
            }}
          >
            {typeof qrAnalysis.parsed_data === 'object'
              ? JSON.stringify(qrAnalysis.parsed_data, null, 2)
              : qrAnalysis.raw_data}
          </pre>
        </details>
      )}
    </div>
  );
};
