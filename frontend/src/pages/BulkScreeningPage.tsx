import React, { useState } from 'react';
import { api } from '../services/api';
import { StatusBadge } from '../components/StatusBadge';
import { Layers, UploadCloud, CheckCircle2, AlertTriangle, Filter, ArrowRight, RefreshCw } from 'lucide-react';

interface BatchItem {
  id: string;
  filename: string;
  documentType: string;
  status: string;
  qualityScore: number;
  acceptable: boolean;
  reasons: string[];
}

interface Props {
  onViewRecord: (id: string) => void;
}

export const BulkScreeningPage: React.FC<Props> = ({ onViewRecord }) => {
  const [documentType, setDocumentType] = useState('Aadhaar');
  const [files, setFiles] = useState<File[]>([]);
  const [processing, setProcessing] = useState(false);
  const [processedCount, setProcessedCount] = useState(0);
  const [results, setResults] = useState<BatchItem[]>([]);
  const [filterNeedsReview, setFilterNeedsReview] = useState(false);

  const handleFiles = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFiles(Array.from(e.target.files));
    }
  };

  const startBatchProcessing = async () => {
    if (files.length === 0) return;
    setProcessing(true);
    setProcessedCount(0);
    const batchResults: BatchItem[] = [];

    for (let i = 0; i < files.length; i++) {
      const f = files[i];
      try {
        const uploadRes = await api.uploadDocument(f, documentType);
        if (!uploadRes.quality.acceptable) {
          batchResults.push({
            id: uploadRes.document_id,
            filename: f.name,
            documentType,
            status: 'UNABLE TO VERIFY',
            qualityScore: uploadRes.quality.overall_score || 35,
            acceptable: false,
            reasons: uploadRes.quality.reasons || ['Unreadable image'],
          });
        } else {
          const vRes = await api.runVerification(uploadRes.document_id, documentType);
          batchResults.push({
            id: vRes.id,
            filename: f.name,
            documentType,
            status: vRes.status,
            qualityScore: uploadRes.quality.overall_score || 92,
            acceptable: true,
            reasons: [],
          });
        }
      } catch (err) {
        batchResults.push({
          id: `err-${i}`,
          filename: f.name,
          documentType,
          status: 'UNABLE TO VERIFY',
          qualityScore: 0,
          acceptable: false,
          reasons: ['Processing failure'],
        });
      }
      setProcessedCount(i + 1);
    }

    setResults(batchResults);
    setProcessing(false);
  };

  // Aggregates
  const counts = {
    verified: results.filter(r => r.status === 'VERIFIED').length,
    likely: results.filter(r => r.status === 'LIKELY AUTHENTIC').length,
    suspicious: results.filter(r => r.status.includes('SUSPICIOUS')).length,
    unable: results.filter(r => r.status.includes('UNABLE')).length,
  };
  const needsReviewCount = counts.suspicious + counts.unable;

  const displayedResults = filterNeedsReview
    ? results.filter(r => r.status.includes('SUSPICIOUS') || r.status.includes('UNABLE'))
    : results;

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">Bulk Document Screening</h1>
        <p className="page-subtitle">Batch process batches of identity documents and isolate cases needing review</p>
      </div>

      {/* Upload & Run Card */}
      <div style={{ background: 'var(--bg-card)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--border-subtle)', padding: '24px', marginBottom: '24px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr auto', gap: '16px', alignItems: 'flex-end' }}>
          <div>
            <label style={{ display: 'block', fontSize: '12px', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '6px' }}>
              Batch Document Type
            </label>
            <select
              value={documentType}
              onChange={e => setDocumentType(e.target.value)}
              style={{ width: '100%', background: 'var(--bg-dark)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '10px 12px', color: '#fff' }}
            >
              <option value="Aadhaar">Aadhaar</option>
              <option value="PAN Card">PAN Card</option>
              <option value="Driving Licence">Driving Licence</option>
              <option value="Passport">Passport</option>
              <option value="Birth Certificate">Birth Certificate</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '12px', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '6px' }}>
              Select Multiple Documents
            </label>
            <input
              type="file"
              multiple
              accept=".jpg,.jpeg,.png,.pdf"
              onChange={handleFiles}
              style={{ width: '100%', background: 'var(--bg-dark)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '8px 12px', color: '#fff' }}
            />
          </div>

          <button
            className="btn btn-primary"
            disabled={files.length === 0 || processing}
            onClick={startBatchProcessing}
            style={{ minWidth: '160px', height: '42px' }}
          >
            {processing ? <RefreshCw className="animate-spin" size={16} /> : <Layers size={16} />}
            {processing ? `Processing ${processedCount}/${files.length}` : `Screen ${files.length} Files`}
          </button>
        </div>
      </div>

      {/* Summary Counters if results exist */}
      {results.length > 0 && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '16px', marginBottom: '24px' }}>
          <div className="metric-card verified">
            <div className="metric-title">Verified</div>
            <div className="metric-value">{counts.verified}</div>
          </div>
          <div className="metric-card likely">
            <div className="metric-title">Likely Authentic</div>
            <div className="metric-value">{counts.likely}</div>
          </div>
          <div className="metric-card suspicious">
            <div className="metric-title">Suspicious</div>
            <div className="metric-value">{counts.suspicious}</div>
          </div>
          <div className="metric-card unable">
            <div className="metric-title">Unable to Verify</div>
            <div className="metric-value">{counts.unable}</div>
          </div>
          <div className="metric-card review">
            <div className="metric-title">Needs Review</div>
            <div className="metric-value">{needsReviewCount}</div>
          </div>
        </div>
      )}

      {/* Results Table */}
      {results.length > 0 && (
        <div style={{ background: 'var(--bg-card)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--border-subtle)', overflow: 'hidden' }}>
          <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3 style={{ fontSize: '15px', fontWeight: 700, color: '#fff' }}>
              Batch Screening Results ({displayedResults.length})
            </h3>

            <button
              className={`btn ${filterNeedsReview ? 'btn-primary' : 'btn-secondary'}`}
              style={{ fontSize: '12px', padding: '6px 12px' }}
              onClick={() => setFilterNeedsReview(!filterNeedsReview)}
            >
              <Filter size={14} /> Only Show Documents Needing Review ({needsReviewCount})
            </button>
          </div>

          <div style={{ overflowX: 'auto' }}>
            <table className="custom-table">
              <thead>
                <tr>
                  <th>Filename</th>
                  <th>Type</th>
                  <th>Status</th>
                  <th>Quality Score</th>
                  <th>Defects / Flags</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {displayedResults.map((item, idx) => (
                  <tr key={idx}>
                    <td style={{ fontWeight: 600, color: '#fff' }}>{item.filename}</td>
                    <td>{item.documentType}</td>
                    <td><StatusBadge status={item.status} size="sm" /></td>
                    <td>{Math.round(item.qualityScore)}/100</td>
                    <td style={{ color: item.reasons.length > 0 ? '#f87171' : 'var(--text-dim)', fontSize: '12px' }}>
                      {item.reasons.length > 0 ? item.reasons.join(', ') : 'None'}
                    </td>
                    <td>
                      <button
                        className="btn btn-secondary"
                        style={{ padding: '4px 8px', fontSize: '11px' }}
                        onClick={() => onViewRecord(item.id)}
                      >
                        Inspect <ArrowRight size={12} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
