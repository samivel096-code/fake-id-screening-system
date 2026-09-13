import React from 'react';
import { ShieldCheck, AlertTriangle, HelpCircle, CheckCircle2 } from 'lucide-react';

interface Props {
  status: string;
  size?: 'sm' | 'md' | 'lg';
}

export const StatusBadge: React.FC<Props> = ({ status, size = 'md' }) => {
  const normalized = status.toUpperCase();

  if (normalized.includes('VERIFIED')) {
    return (
      <span className="status-badge verified">
        <CheckCircle2 size={size === 'sm' ? 12 : 16} />
        VERIFIED
      </span>
    );
  }

  if (normalized.includes('LIKELY AUTHENTIC') || normalized.includes('LIKELY')) {
    return (
      <span className="status-badge likely-authentic">
        <ShieldCheck size={size === 'sm' ? 12 : 16} />
        LIKELY AUTHENTIC
      </span>
    );
  }

  if (normalized.includes('SUSPICIOUS') || normalized.includes('ALTERED')) {
    return (
      <span className="status-badge suspicious">
        <AlertTriangle size={size === 'sm' ? 12 : 16} />
        SUSPICIOUS / LIKELY ALTERED
      </span>
    );
  }

  return (
    <span className="status-badge unable">
      <HelpCircle size={size === 'sm' ? 12 : 16} />
      UNABLE TO VERIFY
    </span>
  );
};
