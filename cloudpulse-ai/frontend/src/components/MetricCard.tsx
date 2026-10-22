import React from 'react';
import { LucideIcon, ArrowUpRight, ArrowDownRight } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  change?: number; // e.g., +12.4 or -5.2
  changeLabel?: string;
  icon: LucideIcon;
  iconColor?: 'teal' | 'cyan' | 'violet' | 'amber' | 'emerald' | 'rose';
  badge?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  change,
  changeLabel = 'vs baseline',
  icon: Icon,
  iconColor = 'teal',
  badge,
}) => {
  const colorMap = {
    teal: 'bg-teal-500/10 text-teal-400 border-teal-500/20',
    cyan: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20',
    violet: 'bg-violet-500/10 text-violet-400 border-violet-500/20',
    amber: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
    emerald: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    rose: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
  };

  const isPositive = change !== undefined && change >= 0;

  return (
    <div className="relative overflow-hidden bg-dark-card border border-dark-border rounded-xl p-5 shadow-lg hover:border-slate-700 transition-all duration-200 group">
      {/* Subtle background glow */}
      <div className="absolute -top-12 -right-12 w-28 h-28 bg-teal-500/5 rounded-full blur-2xl group-hover:bg-teal-500/10 transition-colors pointer-events-none" />

      <div className="flex items-start justify-between">
        <span className="text-xs font-medium uppercase tracking-wider text-slate-400">
          {title}
        </span>
        <div className={`p-2.5 rounded-lg border ${colorMap[iconColor]}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>

      <div className="mt-3 flex items-baseline gap-2">
        <span className="text-2xl font-bold font-mono tracking-tight text-white">
          {value}
        </span>
        {badge && (
          <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-dark-border text-slate-300 border border-slate-700">
            {badge}
          </span>
        )}
      </div>

      {(subtitle || change !== undefined) && (
        <div className="mt-2.5 flex items-center gap-2 text-xs">
          {change !== undefined ? (
            <span
              className={`inline-flex items-center font-mono font-medium ${
                isPositive ? 'text-emerald-400' : 'text-rose-400'
              }`}
            >
              {isPositive ? (
                <ArrowUpRight className="w-3.5 h-3.5 mr-0.5" />
              ) : (
                <ArrowDownRight className="w-3.5 h-3.5 mr-0.5" />
              )}
              {isPositive ? `+${change}%` : `${change}%`}
            </span>
          ) : null}
          <span className="text-slate-500">{subtitle || changeLabel}</span>
        </div>
      )}
    </div>
  );
};

export default MetricCard;
