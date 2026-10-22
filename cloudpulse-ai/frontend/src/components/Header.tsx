import React from 'react';
import { RefreshCw, Shield, Bell, CheckCircle2, AlertCircle } from 'lucide-react';
import { ActiveTab } from '../types';

interface HeaderProps {
  activeTab: ActiveTab;
  onRefresh?: () => void;
  isRefreshing?: boolean;
  isBackendHealthy?: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  activeTab,
  onRefresh,
  isRefreshing = false,
  isBackendHealthy = true,
}) => {
  const titles: Record<ActiveTab, { title: string; subtitle: string }> = {
    overview: {
      title: 'Cluster Overview & Live Pulse',
      subtitle: 'Real-time telemetry, capacity margins, and predictive health',
    },
    workload: {
      title: 'Workload Ingestion & Analytics',
      subtitle: '14-day diurnal telemetry patterns and dataset schema validation',
    },
    predictions: {
      title: 'ML Forecasting Engine',
      subtitle: 'Random Forest vs Persistence Baseline multi-step lookahead',
    },
    optimization: {
      title: 'Resource Allocation & Scaling Topology',
      subtitle: 'Instance fleet management, utilization gates, and capacity thresholds',
    },
    simulation: {
      title: 'Discrete Simulation Lab',
      subtitle: 'Head-to-head benchmarking: Reactive vs Predictive scaling policies',
    },
    reports: {
      title: 'Experiment Logs & Cost Analysis',
      subtitle: 'Historical SLA violation audits and one-click CSV report exports',
    },
    settings: {
      title: 'System & Policy Configuration',
      subtitle: 'Instance boundaries, scaling cooldown intervals, and unit billing rates',
    },
  };

  const { title, subtitle } = titles[activeTab] || titles.overview;

  return (
    <header className="h-16 px-6 bg-dark-card/80 backdrop-blur-md border-b border-dark-border flex items-center justify-between z-10 sticky top-0">
      {/* Left: View Title & Breadcrumb */}
      <div>
        <div className="flex items-center gap-2">
          <span className="text-xs font-mono uppercase tracking-wider text-teal-400">
            CloudPulse AI
          </span>
          <span className="text-slate-600">/</span>
          <h1 className="text-sm font-semibold text-white tracking-wide">
            {title}
          </h1>
        </div>
        <p className="text-[11px] text-slate-400 hidden sm:block">
          {subtitle}
        </p>
      </div>

      {/* Right: Environment Chip, Refresh, and System Indicator */}
      <div className="flex items-center gap-3">
        {/* Environment Badge */}
        <div className="hidden md:flex items-center gap-2 px-2.5 py-1 rounded-md bg-teal-500/10 border border-teal-500/30 text-teal-300 font-mono text-[11px] tracking-wider uppercase">
          <Shield className="w-3.5 h-3.5 text-teal-400" />
          <span>[SIMULATED CLUSTER]</span>
        </div>

        {/* Backend Connectivity Status */}
        <div
          className={`flex items-center gap-1.5 px-2 py-1 rounded text-[11px] font-mono border ${
            isBackendHealthy
              ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
              : 'bg-rose-500/10 text-rose-400 border-rose-500/30'
          }`}
          title={isBackendHealthy ? 'FastAPI Backend Connected' : 'FastAPI Backend Offline'}
        >
          {isBackendHealthy ? (
            <>
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span className="hidden lg:inline">API 8000 OK</span>
            </>
          ) : (
            <>
              <AlertCircle className="w-3.5 h-3.5" />
              <span className="hidden lg:inline">API Offline</span>
            </>
          )}
        </div>

        {/* Refresh Action Button */}
        {onRefresh && (
          <button
            onClick={onRefresh}
            disabled={isRefreshing}
            className="p-2 rounded-lg bg-dark-border/80 border border-slate-700 hover:border-teal-500/40 text-slate-300 hover:text-white transition-colors disabled:opacity-50"
            title="Refresh current data"
          >
            <RefreshCw
              className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin text-teal-400' : ''}`}
            />
          </button>
        )}
      </div>
    </header>
  );
};

export default Header;
