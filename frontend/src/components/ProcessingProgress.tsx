import React, { useEffect, useState } from 'react';
import { CheckCircle2, Loader2, Circle } from 'lucide-react';

interface Props {
  onComplete?: () => void;
}

const STEPS = [
  'Document uploaded & validated',
  'Strict image quality checked (blur, lighting, resolution)',
  'Document boundaries detected & perspective normalized',
  'OCR text & bounding boxes extracted',
  'Document type identified & consistency evaluated',
  'Reference template & layout dimensions compared',
  'QR code detected, located & decoded',
  'Data cross-checked between visible text & QR payload',
  'Document integrity & alteration screening completed',
  'Generating final transparent screening report',
];

export const ProcessingProgress: React.FC<Props> = ({ onComplete }) => {
  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentStep(prev => {
        if (prev < STEPS.length - 1) {
          return prev + 1;
        } else {
          clearInterval(interval);
          if (onComplete) onComplete();
          return prev;
        }
      });
    }, 280);

    return () => clearInterval(interval);
  }, [onComplete]);

  return (
    <div style={{ background: 'var(--bg-card)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--border-subtle)', padding: '24px', maxWidth: '650px', margin: '0 auto' }}>
      <div style={{ textAlign: 'center', marginBottom: '20px' }}>
        <h3 style={{ fontSize: '18px', fontWeight: 700, color: '#fff' }}>Automated Screening Pipeline</h3>
        <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>Executing multi-layer biometric and cryptographic verification checks...</p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {STEPS.map((step, idx) => {
          const isDone = idx < currentStep;
          const isCurrent = idx === currentStep;

          return (
            <div key={step} className="timeline-step" style={{ opacity: idx > currentStep ? 0.4 : 1 }}>
              <div className={`step-icon-circle ${isDone ? 'done' : isCurrent ? 'running' : 'pending'}`}>
                {isDone ? (
                  <CheckCircle2 size={16} />
                ) : isCurrent ? (
                  <Loader2 size={16} className="animate-spin" />
                ) : (
                  <Circle size={14} />
                )}
              </div>
              <div style={{ flex: 1, fontSize: '13px', fontWeight: isCurrent ? 600 : 400, color: isDone ? '#e2e8f0' : isCurrent ? '#60a5fa' : 'var(--text-dim)' }}>
                {step}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
