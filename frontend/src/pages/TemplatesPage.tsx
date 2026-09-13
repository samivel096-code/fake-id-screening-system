import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { TemplateItem, User } from '../types';
import { FileText, Plus, CheckCircle, XCircle, Trash2, UploadCloud, RefreshCw, X, Shield, Eye } from 'lucide-react';

interface Props {
  user: User | null;
}

export const TemplatesPage: React.FC<Props> = ({ user }) => {
  const [templates, setTemplates] = useState<TemplateItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<TemplateItem | null>(null);

  // New Template Form state
  const [newDocType, setNewDocType] = useState('');
  const [newTemplateName, setNewTemplateName] = useState('');
  const [newVersion, setNewVersion] = useState('v1.0');
  const [newIssuingOrg, setNewIssuingOrg] = useState('');
  const [sampleFile, setSampleFile] = useState<File | null>(null);
  const [learning, setLearning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTemplates = async () => {
    setLoading(true);
    try {
      const data = await api.getTemplates();
      setTemplates(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTemplates();
  }, []);

  const handleLearnAndCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!sampleFile) {
      setError('Please attach an authorized reference document sample.');
      return;
    }

    setLearning(true);
    setError(null);
    try {
      const fd = new FormData();
      fd.append('file', sampleFile);
      fd.append('document_type', newDocType);
      fd.append('template_name', newTemplateName);
      fd.append('version', newVersion);
      fd.append('issuing_org', newIssuingOrg);

      await api.learnTemplateFromSample(fd);
      setModalOpen(false);
      setSampleFile(null);
      setNewDocType('');
      setNewTemplateName('');
      await fetchTemplates();
    } catch (err: any) {
      setError(err.message || 'Template learning failed.');
    } finally {
      setLearning(false);
    }
  };

  const handleToggleStatus = async (id: string, currentStatus: string) => {
    const nextStatus = currentStatus === 'ACTIVE' ? 'INACTIVE' : 'ACTIVE';
    try {
      await api.toggleTemplateStatus(id, nextStatus);
      await fetchTemplates();
    } catch (e: any) {
      alert(e.message || 'Status update failed');
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to remove this template configuration?')) return;
    try {
      await api.deleteTemplate(id);
      await fetchTemplates();
    } catch (e: any) {
      alert(e.message || 'Delete failed');
    }
  };

  return (
    <div className="page-container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px', flexWrap: 'wrap', gap: '16px' }}>
        <div className="page-header" style={{ marginBottom: 0 }}>
          <h1 className="page-title">Document Reference Templates</h1>
          <p className="page-subtitle">
            Manage authorized sample baselines and automated layout profiles for identity verification
          </p>
        </div>

        <button className="btn btn-primary" onClick={() => setModalOpen(true)}>
          <Plus size={16} /> Upload Reference Sample & Learn Template
        </button>
      </div>

      {/* Templates List */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '20px' }}>
        {templates.map(tmpl => (
          <div
            key={tmpl.id}
            style={{
              background: 'var(--bg-card)',
              borderRadius: 'var(--radius-lg)',
              border: '1px solid var(--border-subtle)',
              padding: '20px',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
            }}
          >
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '10px' }}>
                <span style={{ fontSize: '11px', fontWeight: 700, color: '#60a5fa', textTransform: 'uppercase', background: 'rgba(59, 130, 246, 0.15)', padding: '2px 8px', borderRadius: '4px' }}>
                  {tmpl.document_type}
                </span>
                <span
                  style={{
                    fontSize: '11px',
                    fontWeight: 700,
                    padding: '2px 8px',
                    borderRadius: '4px',
                    background: tmpl.status === 'ACTIVE' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)',
                    color: tmpl.status === 'ACTIVE' ? '#34d399' : '#f87171',
                  }}
                >
                  {tmpl.status}
                </span>
              </div>

              <h3 style={{ fontSize: '15px', fontWeight: 700, color: '#fff', marginBottom: '4px' }}>
                {tmpl.template_name}
              </h3>
              <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '14px' }}>
                {tmpl.issuing_org || 'Authorized Issuing Authority'} &bull; {tmpl.version}
              </p>

              {/* Sample Preview Thumbnail */}
              {tmpl.sample_image_url ? (
                <div style={{ height: '130px', background: '#0b0f17', borderRadius: 'var(--radius-md)', overflow: 'hidden', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '14px', border: '1px solid var(--border-subtle)' }}>
                  <img src={tmpl.sample_image_url} alt="Reference Sample" style={{ maxHeight: '100%', maxWidth: '100%', objectFit: 'contain' }} />
                </div>
              ) : (
                <div style={{ height: '130px', background: 'rgba(255,255,255,0.02)', borderRadius: 'var(--radius-md)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-dim)', fontSize: '12px', marginBottom: '14px' }}>
                  Profile-only template
                </div>
              )}

              {/* Expected fields preview */}
              <div style={{ fontSize: '11px', color: 'var(--text-dim)', marginBottom: '6px' }}>
                REQUIRED FIELDS ({tmpl.profile?.expected_fields?.length || 0}):
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', marginBottom: '16px' }}>
                {tmpl.profile?.expected_fields?.slice(0, 4).map((f, i) => (
                  <span key={i} style={{ background: 'rgba(255,255,255,0.05)', padding: '2px 6px', borderRadius: '4px', fontSize: '11px', color: '#cbd5e1' }}>
                    {f.label || f.name}
                  </span>
                ))}
                {(tmpl.profile?.expected_fields?.length || 0) > 4 && (
                  <span style={{ fontSize: '11px', color: 'var(--text-dim)', padding: '2px 4px' }}>
                    +{(tmpl.profile?.expected_fields?.length || 0) - 4} more
                  </span>
                )}
              </div>
            </div>

            {/* Actions */}
            <div style={{ display: 'flex', justifyContent: 'space-between', borderTop: '1px solid var(--border-subtle)', paddingTop: '12px' }}>
              <button
                className="btn btn-secondary"
                style={{ fontSize: '11px', padding: '5px 10px' }}
                onClick={() => setSelectedTemplate(tmpl)}
              >
                <Eye size={12} /> Profile Specs
              </button>

              <div style={{ display: 'flex', gap: '6px' }}>
                <button
                  className="btn btn-secondary"
                  style={{ fontSize: '11px', padding: '5px 10px' }}
                  onClick={() => handleToggleStatus(tmpl.id, tmpl.status)}
                >
                  {tmpl.status === 'ACTIVE' ? 'Disable' : 'Activate'}
                </button>
                <button
                  className="btn btn-danger"
                  style={{ fontSize: '11px', padding: '5px 10px' }}
                  onClick={() => handleDelete(tmpl.id)}
                >
                  <Trash2 size={12} />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Modal: Upload Reference Sample & Learn Template */}
      {modalOpen && (
        <div className="modal-backdrop">
          <div className="modal-dialog" style={{ maxWidth: '580px' }}>
            <div className="modal-header">
              <h3 style={{ fontSize: '16px', fontWeight: 700, color: '#fff' }}>
                Automated Template Learning & Enrollment
              </h3>
              <button onClick={() => setModalOpen(false)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
                <X size={18} />
              </button>
            </div>

            <form onSubmit={handleLearnAndCreate}>
              <div className="modal-body">
                {error && (
                  <div style={{ padding: '10px 14px', background: 'rgba(239, 68, 68, 0.15)', border: '1px solid #ef4444', borderRadius: 'var(--radius-sm)', color: '#f87171', fontSize: '13px', marginBottom: '16px' }}>
                    {error}
                  </div>
                )}

                <div style={{ marginBottom: '14px' }}>
                  <label style={{ display: 'block', fontSize: '12px', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '6px' }}>
                    Document Type *
                  </label>
                  <input
                    type="text"
                    required
                    value={newDocType}
                    onChange={e => setNewDocType(e.target.value)}
                    placeholder="e.g. Aadhaar, Passport, University Degree"
                    style={{ width: '100%', background: 'var(--bg-dark)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '9px 12px', color: '#fff', fontSize: '13px' }}
                  />
                </div>

                <div style={{ marginBottom: '14px' }}>
                  <label style={{ display: 'block', fontSize: '12px', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '6px' }}>
                    Template Friendly Name *
                  </label>
                  <input
                    type="text"
                    required
                    value={newTemplateName}
                    onChange={e => setNewTemplateName(e.target.value)}
                    placeholder="e.g. Official Government Aadhaar Reference 2026"
                    style={{ width: '100%', background: 'var(--bg-dark)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '9px 12px', color: '#fff', fontSize: '13px' }}
                  />
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '16px' }}>
                  <div>
                    <label style={{ display: 'block', fontSize: '12px', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '6px' }}>
                      Template Version
                    </label>
                    <input
                      type="text"
                      value={newVersion}
                      onChange={e => setNewVersion(e.target.value)}
                      placeholder="v1.0"
                      style={{ width: '100%', background: 'var(--bg-dark)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '9px 12px', color: '#fff', fontSize: '13px' }}
                    />
                  </div>
                  <div>
                    <label style={{ display: 'block', fontSize: '12px', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '6px' }}>
                      Issuing Organization
                    </label>
                    <input
                      type="text"
                      value={newIssuingOrg}
                      onChange={e => setNewIssuingOrg(e.target.value)}
                      placeholder="e.g. UIDAI / Ministry of Transport"
                      style={{ width: '100%', background: 'var(--bg-dark)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '9px 12px', color: '#fff', fontSize: '13px' }}
                    />
                  </div>
                </div>

                <div style={{ marginBottom: '16px' }}>
                  <label style={{ display: 'block', fontSize: '12px', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '6px' }}>
                    Upload Authorized Sample Image / PDF *
                  </label>
                  <label className="upload-panel" style={{ padding: '24px', display: 'block' }}>
                    <input
                      type="file"
                      accept=".jpg,.jpeg,.png,.pdf"
                      required
                      onChange={e => setSampleFile(e.target.files?.[0] || null)}
                      style={{ display: 'none' }}
                    />
                    <UploadCloud size={28} color="#60a5fa" style={{ margin: '0 auto 8px', display: 'block' }} />
                    <div style={{ fontSize: '13px', fontWeight: 600, color: '#fff' }}>
                      {sampleFile ? sampleFile.name : 'Select Reference Sample File'}
                    </div>
                  </label>
                </div>

                <div style={{ background: 'rgba(59, 130, 246, 0.08)', padding: '12px', borderRadius: 'var(--radius-md)', fontSize: '12px', color: '#93c5fd' }}>
                  <strong>Automated Learning Workflow:</strong> Quality check &rarr; Boundary detection &rarr; Perspective correction &rarr; OCR &rarr; Layout density &rarr; Symbol & QR detection &rarr; Field coordinate mapping.
                </div>
              </div>

              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setModalOpen(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary" disabled={learning}>
                  {learning ? 'Analyzing & Learning Template...' : 'Run Template Learning'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: View Template Profile Specifications */}
      {selectedTemplate && (
        <div className="modal-backdrop">
          <div className="modal-dialog" style={{ maxWidth: '640px' }}>
            <div className="modal-header">
              <h3 style={{ fontSize: '16px', fontWeight: 700, color: '#fff' }}>
                Template Profile: {selectedTemplate.template_name}
              </h3>
              <button onClick={() => setSelectedTemplate(null)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
                <X size={18} />
              </button>
            </div>

            <div className="modal-body">
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px', marginBottom: '16px', fontSize: '13px' }}>
                <div>
                  <span style={{ color: 'var(--text-dim)' }}>Document Type:</span>{' '}
                  <strong style={{ color: '#fff' }}>{selectedTemplate.document_type}</strong>
                </div>
                <div>
                  <span style={{ color: 'var(--text-dim)' }}>Aspect Ratio:</span>{' '}
                  <strong style={{ color: '#fff' }}>{selectedTemplate.aspect_ratio || '1.538'}</strong>
                </div>
                <div>
                  <span style={{ color: 'var(--text-dim)' }}>Dimensions:</span>{' '}
                  <strong style={{ color: '#fff' }}>{selectedTemplate.expected_width}x{selectedTemplate.expected_height} px</strong>
                </div>
                <div>
                  <span style={{ color: 'var(--text-dim)' }}>QR Code Required:</span>{' '}
                  <strong style={{ color: selectedTemplate.profile?.has_qr_code ? '#34d399' : 'var(--text-dim)' }}>
                    {selectedTemplate.profile?.has_qr_code ? 'YES' : 'NO'}
                  </strong>
                </div>
              </div>

              <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '8px' }}>
                Enrolled Mandatory Fields
              </div>
              <div style={{ background: 'var(--bg-dark)', borderRadius: 'var(--radius-md)', padding: '12px', marginBottom: '16px' }}>
                <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '12px' }}>
                  {selectedTemplate.profile?.expected_fields?.map((f, i) => (
                    <li key={i} style={{ display: 'flex', justifyContent: 'space-between', color: '#e2e8f0' }}>
                      <span>&bull; {f.label} ({f.name})</span>
                      <span style={{ color: '#60a5fa' }}>{f.required ? 'MANDATORY' : 'OPTIONAL'}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '8px' }}>
                Raw Learned Configuration
              </div>
              <pre style={{ background: '#070a10', padding: '12px', borderRadius: 'var(--radius-md)', fontSize: '11px', color: '#38bdf8', overflowX: 'auto', maxHeight: '180px' }}>
                {JSON.stringify(selectedTemplate.profile, null, 2)}
              </pre>
            </div>

            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={() => setSelectedTemplate(null)}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
