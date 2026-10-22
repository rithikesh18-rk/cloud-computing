import React from 'react';
import { Server, Activity, HardDrive } from 'lucide-react';
import StatusBadge from './StatusBadge';

interface InstanceCardProps {
  id: string;
  status: 'ACTIVE' | 'PROVISIONING' | 'TERMINATING' | string;
  capacityRps: number;
  cpuUsage: number;
  memoryUsage: number;
  uptimeTicks?: number;
}

export const InstanceCard: React.FC<InstanceCardProps> = ({
  id,
  status,
  capacityRps,
  cpuUsage,
  memoryUsage,
  uptimeTicks = 0,
}) => {
  const isProvisioning = status === 'PROVISIONING';
  const isTerminating = status === 'TERMINATING';

  // Bar color based on utilization
  const getLoadColor = (usage: number) => {
    if (usage > 85) return 'bg-rose-500';
    if (usage > 70) return 'bg-amber-400';
    return 'bg-teal-400';
  };

  return (
    <div
      className={`relative overflow-hidden bg-dark-card border rounded-xl p-4 transition-all duration-200 ${
        isProvisioning
          ? 'border-amber-500/40 bg-amber-500/[0.02]'
          : isTerminating
          ? 'border-rose-500/30 opacity-60'
          : 'border-dark-border hover:border-teal-500/30'
      }`}
    >
      {/* Top Header */}
      <div className="flex items-center justify-between gap-2 mb-3">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-dark-border text-slate-300">
            <Server className="w-4 h-4" />
          </div>
          <div>
            <div className="text-xs font-mono font-semibold text-white tracking-wider">
              {id}
            </div>
            <div className="text-[10px] text-slate-400 font-mono">
              Cap: {capacityRps} RPS
            </div>
          </div>
        </div>
        <StatusBadge status={status} size="sm" />
      </div>

      {/* Load Bars */}
      <div className="space-y-2.5 pt-1">
        {/* CPU */}
        <div>
          <div className="flex justify-between items-center text-[10px] font-mono text-slate-400 mb-1">
            <span className="flex items-center gap-1">
              <Activity className="w-3 h-3 text-teal-400" /> CPU
            </span>
            <span className="font-semibold text-slate-200">{cpuUsage.toFixed(1)}%</span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-500 ${getLoadColor(cpuUsage)}`}
              style={{ width: `${Math.min(100, Math.max(0, cpuUsage))}%` }}
            />
          </div>
        </div>

        {/* Memory */}
        <div>
          <div className="flex justify-between items-center text-[10px] font-mono text-slate-400 mb-1">
            <span className="flex items-center gap-1">
              <HardDrive className="w-3 h-3 text-violet-400" /> MEM
            </span>
            <span className="font-semibold text-slate-200">{memoryUsage.toFixed(1)}%</span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-500 ${getLoadColor(memoryUsage)}`}
              style={{ width: `${Math.min(100, Math.max(0, memoryUsage))}%` }}
            />
          </div>
        </div>
      </div>

      {/* Footer */}
      {uptimeTicks > 0 && (
        <div className="mt-3 pt-2 border-t border-dark-border/60 flex justify-between items-center text-[10px] text-slate-500 font-mono">
          <span>Uptime:</span>
          <span>{uptimeTicks} ticks ({(uptimeTicks * 5)}m)</span>
        </div>
      )}
    </div>
  );
};

export default InstanceCard;
