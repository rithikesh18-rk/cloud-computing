import React from 'react';

interface StatusBadgeProps {
  status: string;
  variant?: 'success' | 'warning' | 'error' | 'info' | 'neutral' | 'active' | 'provisioning';
  size?: 'sm' | 'md';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  variant,
  size = 'md',
}) => {
  // Auto-detect variant if not provided
  let determinedVariant = variant;
  if (!determinedVariant) {
    const s = status.toUpperCase();
    if (s.includes('ACTIVE') || s.includes('COMPLIANT') || s.includes('HEALTHY') || s.includes('OK')) {
      determinedVariant = 'success';
    } else if (s.includes('PROVISIONING') || s.includes('WARN') || s.includes('SCALE_UP')) {
      determinedVariant = 'warning';
    } else if (s.includes('VIOLAT') || s.includes('ERROR') || s.includes('FAIL') || s.includes('TERMINATING')) {
      determinedVariant = 'error';
    } else if (s.includes('PREDICTIVE') || s.includes('INFO') || s.includes('RF')) {
      determinedVariant = 'info';
    } else {
      determinedVariant = 'neutral';
    }
  }

  const variantStyles = {
    success: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
    warning: 'bg-amber-500/15 text-amber-400 border-amber-500/30',
    error: 'bg-rose-500/15 text-rose-400 border-rose-500/30',
    info: 'bg-cyan-500/15 text-cyan-400 border-cyan-500/30',
    active: 'bg-teal-500/15 text-teal-300 border-teal-500/30',
    provisioning: 'bg-amber-500/20 text-amber-300 border-amber-500/40 animate-pulse',
    neutral: 'bg-slate-700/30 text-slate-400 border-slate-700/50',
  };

  const sizeStyles = {
    sm: 'text-[10px] px-2 py-0.5 font-mono tracking-wider',
    md: 'text-xs px-2.5 py-1 font-mono tracking-wide',
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-md border font-medium uppercase transition-colors ${
        variantStyles[determinedVariant]
      } ${sizeStyles[size]}`}
    >
      <span className="w-1.5 h-1.5 rounded-full bg-current opacity-80" />
      {status}
    </span>
  );
};

export default StatusBadge;
