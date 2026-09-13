import React, { useState } from 'react';
import { FlaggedIssue } from '../types';
import { Eye, Layers, Scan, AlertTriangle, CheckSquare, Square, ZoomIn, ZoomOut, RotateCcw } from 'lucide-react';

interface Props {
  uploadedImageUrl?: string;
  overlayImageUrl?: string;
  sampleImageUrl?: string;
  flaggedIssues: FlaggedIssue[];
  textBoxes?: Array<{ text: string; box: { x: number; y: number; width: number; height: number } }>;
  qrBox?: { x: number; y: number; width: number; height: number };
  templateMatchScore?: number;
}

export const VisualReviewViewer: React.FC<Props> = ({
  uploadedImageUrl,
  overlayImageUrl,
  sampleImageUrl,
  flaggedIssues,
  textBoxes = [],
  qrBox,
  templateMatchScore = 95,
}) => {
  const [viewMode, setViewMode] = useState<'side-by-side' | 'overlay'>('side-by-side');
  const [showOcrBoxes, setShowOcrBoxes] = useState(false);
  const [showQrBox, setShowQrBox] = useState(true);
  const [showAnomalies, setShowAnomalies] = useState(true);
  const [selectedIssueId, setSelectedIssueId] = useState<string | null>(null);

  const selectedIssue = flaggedIssues.find(f => f.id === selectedIssueId);

  return (
    <div style={{ background: 'var(--bg-card)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--border-subtle)', padding: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h3 style={{ fontSize: '16px', fontWeight: 700, color: '#fff' }}>Visual Review & Template Alignment</h3>
          <p style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
            Compare uploaded document against authorized reference template with interactive inspection overlays
          </p>
        </div>

        {/* View Mode Switcher */}
        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            className={`btn ${viewMode === 'side-by-side' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ padding: '6px 12px', fontSize: '12px' }}
            onClick={() => setViewMode('side-by-side')}
          >
            Side-by-Side Comparison
          </button>
          {overlayImageUrl && (
            <button
              className={`btn ${viewMode === 'overlay' ? 'btn-primary' : 'btn-secondary'}`}
              style={{ padding: '6px 12px', fontSize: '12px' }}
              onClick={() => setViewMode('overlay')}
            >
              Alignment Heatmap Overlay
            </button>
          )}
        </div>
      </div>

      {/* Layer Toggles */}
      <div style={{ display: 'flex', gap: '16px', background: 'rgba(0,0,0,0.25)', padding: '10px 16px', borderRadius: 'var(--radius-md)', marginBottom: '16px', flexWrap: 'wrap', alignItems: 'center' }}>
        <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-dim)' }}>ACTIVE LAYERS:</span>

        <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', color: '#e2e8f0', cursor: 'pointer' }}>
          <input
            type="checkbox"
            checked={showAnomalies}
            onChange={e => setShowAnomalies(e.target.checked)}
          />
          <span style={{ color: '#f87171', fontWeight: 600 }}>Flagged Anomalies ({flaggedIssues.length})</span>
        </label>

        <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', color: '#e2e8f0', cursor: 'pointer' }}>
          <input
            type="checkbox"
            checked={showQrBox}
            onChange={e => setShowQrBox(e.target.checked)}
          />
          <span style={{ color: '#34d399', fontWeight: 600 }}>QR Region</span>
        </label>

        <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', color: '#e2e8f0', cursor: 'pointer' }}>
          <input
            type="checkbox"
            checked={showOcrBoxes}
            onChange={e => setShowOcrBoxes(e.target.checked)}
          />
          <span style={{ color: '#60a5fa', fontWeight: 600 }}>OCR Bounding Boxes ({textBoxes.length})</span>
        </label>

        <span style={{ marginLeft: 'auto', fontSize: '12px', color: '#93c5fd', fontWeight: 600 }}>
          Template Match: {templateMatchScore}%
        </span>
      </div>

      {/* Main Dual Canvas or Overlay */}
      {viewMode === 'side-by-side' ? (
        <div className="dual-canvas-grid">
          {/* LEFT: Reference Template */}
          <div>
            <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '6px', textTransform: 'uppercase' }}>
              Reference Template (Authorized Sample)
            </div>
            <div className="document-viewer-frame">
              {sampleImageUrl ? (
                <img src={sampleImageUrl} alt="Reference Template Sample" className="document-viewer-img" />
              ) : (
                <div style={{ color: 'var(--text-dim)', textAlign: 'center', padding: '40px' }}>
                  No reference sample image uploaded for this template.
                </div>
              )}
            </div>
          </div>

          {/* RIGHT: Uploaded Document with Overlay Highlights */}
          <div>
            <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '6px', textTransform: 'uppercase' }}>
              Uploaded Document (Normalized)
            </div>
            <div className="document-viewer-frame" style={{ position: 'relative' }}>
              {uploadedImageUrl ? (
                <img src={uploadedImageUrl} alt="Uploaded Document" className="document-viewer-img" />
              ) : (
                <div style={{ color: 'var(--text-dim)', textAlign: 'center', padding: '40px' }}>
                  No uploaded document available.
                </div>
              )}

              {/* OCR Bounding Boxes */}
              {showOcrBoxes &&
                textBoxes.map((tb, idx) => (
                  <div
                    key={idx}
                    className="overlay-bounding-box ocr"
                    style={{
                      left: `${(tb.box.x / 1000) * 100}%`,
                      top: `${(tb.box.y / 650) * 100}%`,
                      width: `${(tb.box.width / 1000) * 100}%`,
                      height: `${(tb.box.height / 650) * 100}%`,
                      position: 'absolute',
                      border: '1px solid rgba(96, 165, 250, 0.7)',
                      background: 'rgba(96, 165, 250, 0.1)',
                      pointerEvents: 'none'
                    }}
                    title={`OCR: "${tb.text}"`}
                  />
                ))}

              {/* QR Box Overlay */}
              {showQrBox && qrBox && (
                <div
                  className="overlay-bounding-box qr"
                  style={{
                    left: `${(qrBox.x / 1000) * 100}%`,
                    top: `${(qrBox.y / 650) * 100}%`,
                    width: `${(qrBox.width / 1000) * 100}%`,
                    height: `${(qrBox.height / 650) * 100}%`,
                    position: 'absolute',
                    border: selectedIssue?.type === 'QR_MISMATCH' ? '3px solid #ef4444' : '2px solid #34d399',
                    boxShadow: selectedIssue?.type === 'QR_MISMATCH' ? '0 0 20px rgba(239, 68, 68, 0.8)' : 'none',
                    background: selectedIssue?.type === 'QR_MISMATCH' ? 'rgba(239, 68, 68, 0.25)' : 'rgba(52, 211, 153, 0.15)',
                    zIndex: selectedIssue?.type === 'QR_MISMATCH' ? 25 : 10,
                    transition: 'all 0.2s ease',
                  }}
                  title="Decoded QR Code Region"
                />
              )}

              {/* Flagged Regions Overlay */}
              {showAnomalies &&
                flaggedIssues.map((issue, idx) => {
                  if (!issue.region) return null;
                  const isSelected = selectedIssueId === issue.id;
                  const r = issue.region;
                  const left = r.x_ratio !== undefined ? `${r.x_ratio * 100}%` : `${(r.x / 1000) * 100}%`;
                  const top = r.y_ratio !== undefined ? `${r.y_ratio * 100}%` : `${(r.y / 650) * 100}%`;
                  const width = r.w_ratio !== undefined ? `${r.w_ratio * 100}%` : `${(r.width / 1000) * 100}%`;
                  const height = r.h_ratio !== undefined ? `${r.h_ratio * 100}%` : `${(r.height / 650) * 100}%`;

                  return (
                    <div
                      key={issue.id || idx}
                      className="overlay-bounding-box anomaly"
                      style={{
                        position: 'absolute',
                        left,
                        top,
                        width,
                        height,
                        border: isSelected ? '3px solid #fbbf24' : '2px solid #ef4444',
                        boxShadow: isSelected ? '0 0 22px rgba(251, 191, 36, 0.9)' : '0 0 10px rgba(239, 68, 68, 0.5)',
                        background: isSelected ? 'rgba(251, 191, 36, 0.25)' : 'rgba(239, 68, 68, 0.2)',
                        zIndex: isSelected ? 30 : 15,
                        cursor: 'pointer',
                        transition: 'all 0.2s ease',
                      }}
                      onClick={() => setSelectedIssueId(isSelected ? null : issue.id)}
                      title={`${issue.title}: ${issue.description}`}
                    />
                  );
                })}
            </div>
          </div>
        </div>
      ) : (
        /* Overlay Difference View */
        <div>
          <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '6px', textTransform: 'uppercase' }}>
            Alignment Difference Heatmap (Overlay of Uploaded Image vs Reference Sample)
          </div>
          <div className="document-viewer-frame">
            {overlayImageUrl ? (
              <img src={overlayImageUrl} alt="Alignment Heatmap" className="document-viewer-img" />
            ) : (
              <div style={{ color: 'var(--text-dim)', textAlign: 'center', padding: '40px' }}>
                Overlay heatmap not generated.
              </div>
            )}
          </div>
        </div>
      )}

      {/* Flagged Issues List (Clicking highlights on canvas) */}
      <div style={{ marginTop: '20px' }}>
        <h4 style={{ fontSize: '13px', fontWeight: 700, color: '#fff', marginBottom: '10px', textTransform: 'uppercase' }}>
          Flagged Review Items ({flaggedIssues.length})
        </h4>

        {flaggedIssues.length === 0 ? (
          <div style={{ padding: '12px 16px', background: 'rgba(16, 185, 129, 0.08)', borderRadius: 'var(--radius-md)', color: '#34d399', fontSize: '13px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            ✓ No structural or cryptographic anomalies flagged.
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {flaggedIssues.map(issue => {
              const isSelected = selectedIssueId === issue.id;
              return (
                <div
                  key={issue.id}
                  onClick={() => setSelectedIssueId(isSelected ? null : issue.id)}
                  style={{
                    padding: '12px 16px',
                    borderRadius: 'var(--radius-md)',
                    background: isSelected ? 'rgba(239, 68, 68, 0.2)' : 'rgba(255, 255, 255, 0.03)',
                    border: isSelected ? '1px solid #ef4444' : '1px solid var(--border-subtle)',
                    cursor: 'pointer',
                    transition: 'all 0.15s ease',
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: '12px',
                  }}
                >
                  <AlertTriangle
                    size={18}
                    color={issue.severity === 'HIGH' ? '#f87171' : '#fbbf24'}
                    style={{ flexShrink: 0, marginTop: '2px' }}
                  />
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <strong style={{ fontSize: '13px', color: '#fff' }}>{issue.title}</strong>
                      <span
                        style={{
                          fontSize: '10px',
                          fontWeight: 700,
                          padding: '1px 6px',
                          borderRadius: '4px',
                          background: issue.severity === 'HIGH' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(245, 158, 11, 0.2)',
                          color: issue.severity === 'HIGH' ? '#f87171' : '#fbbf24',
                        }}
                      >
                        {issue.severity} RISK
                      </span>
                    </div>
                    <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '2px' }}>{issue.description}</p>
                    {issue.region && (
                      <span style={{ fontSize: '11px', color: '#60a5fa', marginTop: '4px', display: 'inline-block' }}>
                        &bull; Click to highlight location on document canvas
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
