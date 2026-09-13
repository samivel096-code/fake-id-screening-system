import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { VerificationResult, ImageQuality, DemoDocItem } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { VerificationScoreCard } from '../components/VerificationScoreCard';
import { DataComparisonTable } from '../components/DataComparisonTable';
import { VisualReviewViewer } from '../components/VisualReviewViewer';
import { ProcessingProgress } from '../components/ProcessingProgress';
import { CameraCaptureModal } from '../components/CameraCaptureModal';
import { OfficerReviewModal } from '../components/OfficerReviewModal';
import { ImageQualityCard } from '../components/ImageQualityCard';
import { QRResult } from '../components/QRResult';
import {
  UploadCloud,
  Camera,
  FileText,
  AlertTriangle,
  CheckCircle2,
  RefreshCw,
  QrCode,
  ShieldCheck,
  Edit3,
  Printer,
  Sparkles,
  Info,
  ShieldAlert
} from 'lucide-react';

const DOCUMENT_TYPES = [
  'Aadhaar',
  'PAN Card',
  'Driving Licence',
  'Passport',
  'Voter ID',
  'Birth Certificate',
  'Death Certificate',
  'Caste Certificate',
  'Income Certificate',
  'Community Certificate',
  'Educational Certificate',
  'Vehicle Registration Certificate',
  'Government Certificate',
  'Business Certificate',
  'Invoice',
  'Other / Custom Document'
];

interface Props {
  initialVerificationId?: string | null;
  onClearInitialId?: () => void;
}

export const VerifyDocumentPage: React.FC<Props> = ({ initialVerificationId, onClearInitialId }) => {
  const [documentType, setDocumentType] = useState('Aadhaar');
  const [file, setFile] = useState<File | null>(null);
  const [cameraOpen, setCameraOpen] = useState(false);
  const [reviewModalOpen, setReviewModalOpen] = useState(false);
  
  // Pipeline states
  const [isProcessing, setIsProcessing] = useState(false);
  const [qualityFailed, setQualityFailed] = useState<ImageQuality | null>(null);
  const [result, setResult] = useState<VerificationResult | null>(null);
  const [demoDocs, setDemoDocs] = useState<DemoDocItem[]>([]);
  const [loadingDemo, setLoadingDemo] = useState(false);

  useEffect(() => {
    api.getDemoDocuments().then(setDemoDocs).catch(console.error);
    if (initialVerificationId) {
      api.getVerification(initialVerificationId)
        .then(setResult)
        .catch(console.error)
        .finally(() => {
          if (onClearInitialId) onClearInitialId();
        });
    }
  }, [initialVerificationId]);

  // Handle file selection
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setQualityFailed(null);
      setResult(null);
    }
  };

  // Upload and execute screening
  const startScreening = async (fileToUpload?: File) => {
    const targetFile = fileToUpload || file;
    if (!targetFile) return;

    setIsProcessing(true);
    setQualityFailed(null);
    setResult(null);

    try {
      // Step 1: Upload and run strict Image Quality Check
      const uploadRes = await api.uploadDocument(targetFile, documentType);
      
      if (!uploadRes.quality.acceptable) {
        setIsProcessing(false);
        setQualityFailed(uploadRes.quality);
        return;
      }

      // Step 2: Run complete screening pipeline
      const verificationRes = await api.runVerification(
        uploadRes.document_id,
        documentType
      );
      setResult(verificationRes);
    } catch (err: any) {
      alert(`Screening error: ${err.message || 'Verification failed'}`);
    } finally {
      setIsProcessing(false);
    }
  };

  // 1-Click Demo Document loader
  const handleLoadDemo = async (demoId: string) => {
    setLoadingDemo(true);
    setQualityFailed(null);
    setResult(null);
    try {
      const demoItem = demoDocs.find(d => d.id === demoId);
      if (demoItem) {
        setDocumentType(demoItem.document_type);
      }
      const loaded = await api.loadDemoDocument(demoId);
      
      setIsProcessing(true);
      // Run screening on loaded demo document
      const verificationRes = await api.runVerification(
        loaded.document_id,
        loaded.document_type
      );
      
      if (verificationRes.status === 'UNABLE TO VERIFY' && verificationRes.image_quality && !verificationRes.image_quality.acceptable) {
        setQualityFailed(verificationRes.image_quality);
      } else {
        setResult(verificationRes);
      }
    } catch (e: any) {
      alert(`Failed to load demo document: ${e.message}`);
    } finally {
      setLoadingDemo(false);
      setIsProcessing(false);
    }
  };

  return (
    <div className="page-container">
      {/* Header */}
      <div className="page-header">
        <h1 className="page-title">Screen & Verify Document</h1>
        <p className="page-subtitle">
          Execute automated multi-check screening against configured reference templates
        </p>
      </div>

      {/* 1. Document Configuration & Upload Bar (hidden if showing result) */}
      {!result && !isProcessing && !qualityFailed && (
        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px', marginBottom: '28px' }}>
          {/* Main Upload Box */}
          <div style={{ background: 'var(--bg-card)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--border-subtle)', padding: '28px' }}>
            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', fontSize: '12px', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '8px' }}>
                Select Document Type
              </label>
              <select
                value={documentType}
                onChange={e => setDocumentType(e.target.value)}
                style={{
                  width: '100%',
                  background: 'var(--bg-dark)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-md)',
                  padding: '12px 14px',
                  color: '#fff',
                  fontSize: '14px',
                  fontWeight: 600
                }}
              >
                {DOCUMENT_TYPES.map(t => (
                  <option key={t} value={t}>{t}</option>
                ))}
              </select>
            </div>

            {/* Drop Zone */}
            <label className="upload-panel" style={{ display: 'block' }}>
              <input
                type="file"
                accept=".jpg,.jpeg,.png,.pdf"
                onChange={handleFileChange}
                style={{ display: 'none' }}
              />
              <div className="upload-icon-circle">
                <UploadCloud size={32} />
              </div>
              <h3 style={{ fontSize: '16px', fontWeight: 700, color: '#fff' }}>
                {file ? file.name : 'Upload Document for Screening'}
              </h3>
              <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginTop: '4px' }}>
                Drag and drop JPG, PNG, or PDF file, or click to browse
              </p>
              {file && (
                <span style={{ display: 'inline-block', marginTop: '12px', padding: '4px 10px', background: 'rgba(59, 130, 246, 0.2)', color: '#60a5fa', borderRadius: 'var(--radius-full)', fontSize: '12px', fontWeight: 600 }}>
                  Ready to Screen ({(file.size / 1024).toFixed(1)} KB)
                </span>
              )}
            </label>

            {/* Action Buttons */}
            <div style={{ display: 'flex', gap: '12px', marginTop: '20px' }}>
              <button
                className="btn btn-secondary"
                style={{ flex: 1 }}
                onClick={() => setCameraOpen(true)}
              >
                <Camera size={16} /> Take Photo (Webcam)
              </button>
              <button
                className="btn btn-primary"
                style={{ flex: 2 }}
                disabled={!file}
                onClick={() => startScreening()}
              >
                <Sparkles size={16} /> Start Automated Screening
              </button>
            </div>
          </div>

          {/* 1-Click Demo Testing Box */}
          <div style={{ background: 'var(--bg-card)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--border-subtle)', padding: '24px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px' }}>
              <Sparkles size={18} color="#fbbf24" />
              <h3 style={{ fontSize: '15px', fontWeight: 700, color: '#fff' }}>1-Click Demo Testing</h3>
            </div>
            <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '16px' }}>
              Test specific screening scenarios instantly using fictional test documents:
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {demoDocs.map(doc => (
                <button
                  key={doc.id}
                  className="btn btn-secondary"
                  disabled={loadingDemo}
                  onClick={() => handleLoadDemo(doc.id)}
                  style={{ textAlign: 'left', display: 'flex', flexDirection: 'column', alignItems: 'flex-start', padding: '10px 14px' }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%', alignItems: 'center' }}>
                    <strong style={{ fontSize: '13px', color: '#fff' }}>{doc.title}</strong>
                    <span style={{ fontSize: '10px', color: doc.expected_outcome.includes('AUTHENTIC') ? '#34d399' : doc.expected_outcome.includes('ALTERED') ? '#f87171' : '#fbbf24', fontWeight: 700 }}>
                      {doc.expected_outcome}
                    </span>
                  </div>
                  <span style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>
                    {doc.description}
                  </span>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* 2. Processing Timeline Animation */}
      {isProcessing && (
        <div style={{ padding: '40px 0' }}>
          <ProcessingProgress />
        </div>
      )}

      {/* 3. Strict Image Quality Failure View (Section 8) */}
      {qualityFailed && (
        <div style={{ background: 'rgba(239, 68, 68, 0.08)', border: '1px solid #ef4444', borderRadius: 'var(--radius-lg)', padding: '32px', maxWidth: '700px', margin: '0 auto', textAlign: 'center' }}>
          <div style={{ width: '56px', height: '56px', borderRadius: '50%', background: 'rgba(239, 68, 68, 0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px', color: '#f87171' }}>
            <AlertTriangle size={32} />
          </div>
          <h2 style={{ fontSize: '20px', fontWeight: 800, color: '#fff', marginBottom: '8px' }}>DOCUMENT NOT CLEAR</h2>
          <p style={{ fontSize: '14px', color: '#fca5a5', marginBottom: '20px' }}>
            The uploaded document is not sufficiently visible for reliable analysis.
          </p>

          <div style={{ background: 'rgba(0, 0, 0, 0.3)', borderRadius: 'var(--radius-md)', padding: '16px', textAlign: 'left', marginBottom: '24px' }}>
            <div style={{ fontSize: '12px', fontWeight: 700, color: '#f87171', textTransform: 'uppercase', marginBottom: '8px' }}>
              Detected Image Quality Defects:
            </div>
            <ul style={{ listStyle: 'disc', paddingLeft: '20px', color: '#e2e8f0', fontSize: '13px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
              {qualityFailed.reasons.map((r, i) => (
                <li key={i}>{r}</li>
              ))}
            </ul>
          </div>

          <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '20px' }}>
            Please upload a clear, complete, and un-cropped image of the document in adequate lighting.
          </p>

          <button className="btn btn-primary" onClick={() => { setQualityFailed(null); setFile(null); }}>
            Upload Clear Image
          </button>
        </div>
      )}

      {/* 4. Complete Screening Result Report */}
      {result && (
        <div>
          {/* Top Classification Banner */}
          <div style={{ background: 'var(--bg-card)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--border-subtle)', padding: '24px', marginBottom: '24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
            <div>
              <div style={{ fontSize: '12px', color: 'var(--text-dim)', fontWeight: 700, textTransform: 'uppercase', marginBottom: '6px' }}>
                Screening Classification Outcome
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                <StatusBadge status={result.status} size="lg" />
                <span style={{ fontSize: '14px', color: 'var(--text-muted)' }}>
                  Document: <strong style={{ color: '#fff' }}>{result.document_type}</strong>
                </span>
                <span style={{ fontSize: '14px', color: 'var(--text-muted)' }}>
                  Template: <strong style={{ color: '#93c5fd' }}>{result.template_name || 'Standard v1'}</strong>
                </span>
              </div>
            </div>

            <div style={{ display: 'flex', gap: '10px' }}>
              <button className="btn btn-secondary" onClick={() => window.print()}>
                <Printer size={14} /> Print Report
              </button>
              <button className="btn btn-primary" onClick={() => setReviewModalOpen(true)}>
                <Edit3 size={14} /> Record Officer Review
              </button>
              <button
                className="btn btn-secondary"
                onClick={() => { setResult(null); setFile(null); }}
              >
                Screen Another Document
              </button>
            </div>
          </div>

          {/* Mandatory Section 22 Legal Disclaimer Banner */}
          <div className="legal-notice-box">
            <Info size={20} color="#fbbf24" style={{ flexShrink: 0, marginTop: '2px' }} />
            <div>
              <strong>CRITICAL VERIFICATION PRINCIPLE</strong>
              <p>{result.legal_disclaimer}</p>
            </div>
          </div>

          {/* Section 12 Document Type Mismatch Alert Banner if detected */}
          {result.flagged_issues.some(f => f.title.toLowerCase().includes('type mismatch') || f.description.toLowerCase().includes('type is')) && (
            <div style={{ background: 'rgba(239, 68, 68, 0.15)', border: '1px solid #ef4444', borderRadius: 'var(--radius-lg)', padding: '16px 20px', marginBottom: '24px', display: 'flex', alignItems: 'center', gap: '14px' }}>
              <ShieldAlert size={26} color="#f87171" style={{ flexShrink: 0 }} />
              <div>
                <strong style={{ fontSize: '14px', color: '#f87171', textTransform: 'uppercase' }}>Document Type Mismatch Detected</strong>
                <p style={{ fontSize: '13px', color: '#fca5a5', marginTop: '2px' }}>
                  Selected document type is <strong>{result.document_type}</strong>, but the uploaded document appears inconsistent with the selected template. Officer review is required.
                </p>
              </div>
            </div>
          )}

          {/* Grid: Score Card + Validation Notes */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '24px' }}>
            {/* Score Card */}
            <VerificationScoreCard
              score={result.screening_score}
              breakdown={result.breakdown}
            />

            {/* Validation Notes & Recommendation */}
            <div style={{ background: 'var(--bg-card)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--border-subtle)', padding: '24px', display: 'flex', flexDirection: 'column' }}>
              <h3 style={{ fontSize: '16px', fontWeight: 700, color: '#fff', marginBottom: '14px' }}>
                Validation Notes & Findings
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', flex: 1 }}>
                {result.validation_notes.map((note, idx) => (
                  <div
                    key={idx}
                    style={{
                      fontSize: '13px',
                      color: note.startsWith('❌') ? '#f87171' : note.startsWith('⚠') ? '#fbbf24' : '#e2e8f0',
                      lineHeight: 1.5,
                    }}
                  >
                    {note}
                  </div>
                ))}
              </div>

              {/* Recommendation Box */}
              <div style={{ marginTop: '20px', padding: '14px', background: 'rgba(0,0,0,0.25)', borderRadius: 'var(--radius-md)', borderLeft: '4px solid #3b82f6' }}>
                <div style={{ fontSize: '11px', fontWeight: 700, color: '#93c5fd', textTransform: 'uppercase' }}>
                  System Recommendation
                </div>
                <div style={{ fontSize: '13px', color: '#fff', fontWeight: 600, marginTop: '2px' }}>
                  {result.recommendation}
                </div>
              </div>
            </div>
          </div>

          {/* Section 15 & 16: QR Verification Analysis */}
          <div style={{ marginBottom: '24px' }}>
            <QRResult
              qrAnalysis={result.qr_analysis}
              extractedFields={result.extracted_fields}
              hasMismatch={result.flagged_issues.some(f => f.type === 'QR_MISMATCH')}
            />
          </div>

          {/* Data Cross-Check Table */}
          <div style={{ marginBottom: '24px' }}>
            <DataComparisonTable rows={result.data_comparison} />
          </div>

          {/* Section 9: Image Quality Verification Confirmation */}
          {result.image_quality && (
            <div style={{ marginBottom: '24px' }}>
              <ImageQualityCard quality={result.image_quality} />
            </div>
          )}

          {/* Visual Review & Overlay Inspection */}
          <div style={{ marginBottom: '24px' }}>
            <VisualReviewViewer
              uploadedImageUrl={result.normalized_image_url}
              overlayImageUrl={result.overlay_image_url}
              sampleImageUrl={result.sample_image_url}
              flaggedIssues={result.flagged_issues}
              textBoxes={result.text_boxes}
              qrBox={result.qr_box}
              templateMatchScore={result.breakdown.template_match}
            />
          </div>

          {/* Officer Review Result Badge if already reviewed */}
          {result.officer_review_decision && (
            <div style={{ background: 'rgba(16, 185, 129, 0.1)', border: '1px solid #10b981', borderRadius: 'var(--radius-lg)', padding: '18px 24px', marginBottom: '24px' }}>
              <div style={{ fontSize: '12px', fontWeight: 700, color: '#34d399', textTransform: 'uppercase' }}>
                Official Review Recorded
              </div>
              <div style={{ fontSize: '14px', color: '#fff', marginTop: '4px' }}>
                Decision: <strong>{result.officer_review_decision}</strong> by {result.reviewed_by} on {result.reviewed_at}
              </div>
              {result.officer_notes && (
                <div style={{ fontSize: '13px', color: 'var(--text-muted)', marginTop: '4px' }}>
                  Officer Notes: &ldquo;{result.officer_notes}&rdquo;
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Camera Capture Modal */}
      {cameraOpen && (
        <CameraCaptureModal
          onCapture={capturedFile => {
            setFile(capturedFile);
            startScreening(capturedFile);
          }}
          onClose={() => setCameraOpen(false)}
        />
      )}

      {/* Officer Manual Review Modal */}
      {reviewModalOpen && result && (
        <OfficerReviewModal
          verificationId={result.id}
          currentStatus={result.status}
          onClose={() => setReviewModalOpen(false)}
          onSuccess={updated => {
            setResult({
              ...result,
              status: updated.status,
              officer_review_decision: updated.officer_review_decision,
              reviewed_by: updated.reviewed_by,
              reviewed_at: updated.reviewed_at,
            });
          }}
        />
      )}
    </div>
  );
};
