import React from 'react';
import {
  LayoutDashboard,
  BarChart3,
  TrendingUp,
  Cpu,
  Zap,
  FileSpreadsheet,
  Sliders,
  Activity,
  Terminal,
} from 'lucide-react';
import { ActiveTab } from '../types';

interface SidebarProps {
  activeTab: ActiveTab;
  onTabChange: (tab: ActiveTab) => void;
}

interface NavItem {
  id: ActiveTab;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  tag?: string;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, onTabChange }) => {
  const navItems: NavItem[] = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'workload', label: 'Workload Analytics', icon: BarChart3 },
    { id: 'predictions', label: 'ML Predictions', icon: TrendingUp, tag: 'AI' },
    { id: 'optimization', label: 'Cluster Optimization', icon: Cpu },
    { id: 'simulation', label: 'Simulation Lab', icon: Zap, tag: 'SIM' },
    { id: 'reports', label: 'Experiment Reports', icon: FileSpreadsheet },
    { id: 'settings', label: 'System Settings', icon: Sliders },
  ];

  return (
    <aside className="w-64 bg-dark-card border-r border-dark-border flex flex-col h-screen select-none shrink-0 z-20">
      {/* Brand Header */}
      <div className="h-16 px-6 flex items-center gap-3 border-b border-dark-border">
        <div className="p-2 rounded-xl bg-teal-500/10 border border-teal-500/30 text-teal-400 flex items-center justify-center shadow-lg shadow-teal-500/10">
          <Activity className="w-5 h-5 animate-pulse" />
        </div>
        <div>
          <div className="text-base font-bold tracking-tight text-white flex items-center gap-1.5">
            CloudPulse <span className="text-teal-400 text-xs px-1.5 py-0.2 rounded bg-teal-500/20 border border-teal-500/30">AI</span>
          </div>
          <div className="text-[10px] text-slate-400 font-mono tracking-wider uppercase">
            Workload & Scaling
          </div>
        </div>
      </div>

      {/* Navigation Items */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        <div className="px-3 pb-2 text-[10px] font-mono font-semibold uppercase tracking-wider text-slate-400">
          Platform Views
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;

          return (
            <button
              key={item.id}
              onClick={() => onTabChange(item.id)}
              className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-lg text-xs font-medium transition-all group relative ${
                isActive
                  ? 'bg-gradient-to-r from-teal-500/15 to-transparent text-teal-300 border-l-2 border-teal-400 font-semibold'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
              }`}
            >
              <div className="flex items-center gap-3">
                <Icon
                  className={`w-4 h-4 transition-colors ${
                    isActive ? 'text-teal-400' : 'text-slate-400 group-hover:text-slate-200'
                  }`}
                />
                <span>{item.label}</span>
              </div>
              {item.tag && (
                <span
                  className={`text-[9px] font-mono px-1.5 py-0.5 rounded uppercase font-bold tracking-wider ${
                    isActive
                      ? 'bg-teal-500/30 text-teal-300'
                      : 'bg-dark-border text-slate-400 group-hover:text-slate-300'
                  }`}
                >
                  {item.tag}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Cluster Status Footer */}
      <div className="p-4 border-t border-dark-border bg-dark-bg/40">
        <div className="flex items-center justify-between mb-2">
          <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
            Cluster Engine
          </span>
          <span className="text-[10px] font-mono text-emerald-400 font-bold">ONLINE</span>
        </div>
        <div className="p-2 rounded bg-dark-border/60 border border-slate-800 text-[10px] font-mono text-slate-400 flex items-center gap-2">
          <Terminal className="w-3.5 h-3.5 text-teal-400 shrink-0" />
          <span className="truncate">Simulated Cluster Node</span>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
