import React, { useEffect, useState } from 'react';
import {
  Server,
  Activity,
  ShieldCheck,
  DollarSign,
  TrendingUp,
  Cpu,
  Zap,
  ArrowRight,
  Clock,
  Layers,
} from 'lucide-react';
import { MetricCard } from '../components/MetricCard';
import { InstanceCard } from '../components/InstanceCard';
import { StatusBadge } from '../components/StatusBadge';
import { api } from '../api/client';
import {
  DatasetPreviewResponse,
  SimulationHistoryItem,
  SettingsResponse,
  ActiveTab,
} from '../types';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';

interface OverviewProps {
  onNavigate: (tab: ActiveTab) => void;
}

export const Overview: React.FC<OverviewProps> = ({ onNavigate }) => {
  const [loading, setLoading] = useState<boolean>(true);
  const [datasetPreview, setDatasetPreview] = useState<DatasetPreviewResponse | null>(null);
  const [recentSimulations, setRecentSimulations] = useState<SimulationHistoryItem[]>([]);
  const [settings, setSettings] = useState<SettingsResponse | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [previewData, historyData, settingsData] = await Promise.allSettled([
          api.getDatasetPreview(),
          api.getSimulationHistory(5),
          api.getSettings(),
        ]);

        if (previewData.status === 'fulfilled') setDatasetPreview(previewData.value);
        if (historyData.status === 'fulfilled') setRecentSimulations(historyData.value);
        if (settingsData.status === 'fulfilled') setSettings(settingsData.value);
      } catch (err) {
        console.error('Error fetching overview telemetry', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Format telemetry for mini sparkline
  const chartData = (datasetPreview?.rows || []).slice(0, 24).map((row) => ({
    time: row.timestamp.split(' ')[1]?.slice(0, 5) || row.timestamp,
    cpu: row.cpu_usage,
    memory: row.memory_usage,
    requests: row.request_count,
  }));

  // Mock cluster topology derived from active settings
  const simulatedNodes = [
    { id: 'worker-node-01', status: 'ACTIVE', cpu: 64.2, memory: 58.1, uptime: 142 },
    { id: 'worker-node-02', status: 'ACTIVE', cpu: 71.8, memory: 62.4, uptime: 142 },
    { id: 'worker-node-03', status: 'ACTIVE', cpu: 55.0, memory: 51.9, uptime: 98 },
    { id: 'worker-node-04', status: 'PROVISIONING', cpu: 12.0, memory: 28.5, uptime: 1 },
  ];

  const latestRun = recentSimulations[0];

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Informational Banner */}
      <div className="bg-gradient-to-r from-teal-500/10 via-dark-card to-cyan-500/5 border border-teal-500/20 rounded-xl p-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-lg bg-teal-500/20 border border-teal-500/40 text-teal-300">
            <Zap className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <div className="text-xs font-mono uppercase tracking-wider text-teal-400 font-bold">
              Autonomous Resource Orchestrator
            </div>
            <div className="text-xs text-slate-300 mt-0.5">
              Predictive autoscaling neutralizes spin-up latency by provisioning nodes 1 step ahead of workload surges.
            </div>
          </div>
        </div>

        <button
          onClick={() => onNavigate('simulation')}
          className="flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-teal-500 hover:bg-teal-400 text-dark-bg font-semibold text-xs tracking-wider uppercase transition-all shadow-lg shadow-teal-500/20 shrink-0"
        >
          <span>Launch Lab</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Active Cluster Capacity"
          value={simulatedNodes.filter((n) => n.status === 'ACTIVE').length * (settings?.capacity_per_instance_rps || 200) + ' RPS'}
          subtitle={`${simulatedNodes.length} nodes active / provisioning`}
          icon={Server}
          iconColor="teal"
          badge="HEALTHY"
        />
        <MetricCard
          title="SLA Compliance Rate"
          value={latestRun ? `${(100 - (latestRun.predictive_sla_violations / latestRun.total_steps) * 100).toFixed(1)}%` : '98.8%'}
          change={latestRun ? Number(latestRun.cost_savings_pct.toFixed(1)) : 14.5}
          changeLabel="cost savings"
          icon={ShieldCheck}
          iconColor="emerald"
          badge="PREDICTIVE"
        />
        <MetricCard
          title="Cluster Avg CPU"
          value={chartData.length ? `${(chartData.reduce((acc, r) => acc + r.cpu, 0) / chartData.length).toFixed(1)}%` : '58.4%'}
          subtitle={`Target: ${((settings?.target_utilization || 0.7) * 100).toFixed(0)}% optimal`}
          icon={Activity}
          iconColor="violet"
        />
        <MetricCard
          title="Infrastructure Cost"
          value={`$${(simulatedNodes.length * (settings?.hourly_cost_per_node || 0.05)).toFixed(3)}/hr`}
          subtitle={`Unit rate: $${(settings?.hourly_cost_per_node || 0.05).toFixed(2)}/node/hr`}
          icon={DollarSign}
          iconColor="cyan"
        />
      </div>

      {/* Main Grid: Telemetry Trends & Quick Simulator */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Live Telemetry Sparkline */}
        <div className="lg:col-span-2 bg-dark-card border border-dark-border rounded-xl p-5 shadow-lg flex flex-col justify-between">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-sm font-semibold text-white tracking-wide flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-teal-400" />
                Recent Workload & CPU Utilization Trend
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                5-minute interval historical telemetry from active dataset
              </p>
            </div>
            <button
              onClick={() => onNavigate('workload')}
              className="text-xs font-mono text-teal-400 hover:text-teal-300 flex items-center gap-1"
            >
              Full Analytics <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="cpuGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#14b8a6" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#14b8a6" stopOpacity={0.0} />
                  </linearGradient>
                  <linearGradient id="memGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} />
                <XAxis dataKey="time" stroke="#64748b" tick={{ fontSize: 11 }} />
                <YAxis stroke="#64748b" domain={[0, 100]} tick={{ fontSize: 11 }} unit="%" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#111827',
                    borderColor: '#1f2937',
                    borderRadius: '8px',
                    fontSize: '12px',
                    fontFamily: 'JetBrains Mono, monospace',
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="cpu"
                  name="CPU Usage"
                  stroke="#14b8a6"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#cpuGradient)"
                />
                <Area
                  type="monotone"
                  dataKey="memory"
                  name="Memory Usage"
                  stroke="#8b5cf6"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#memGradient)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          <div className="flex items-center justify-center gap-6 pt-3 border-t border-dark-border/60 text-xs text-slate-400">
            <span className="flex items-center gap-2">
              <span className="w-3 h-0.5 bg-teal-400 rounded-full" /> CPU Utilization
            </span>
            <span className="flex items-center gap-2">
              <span className="w-3 h-0.5 bg-violet-400 rounded-full" /> Memory Allocation
            </span>
          </div>
        </div>

        {/* Right 1 Col: Quick Simulation & Recent Runs */}
        <div className="bg-dark-card border border-dark-border rounded-xl p-5 shadow-lg flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-sm font-semibold text-white tracking-wide flex items-center gap-2">
                <Clock className="w-4 h-4 text-cyan-400" />
                Recent Lab Benchmarks
              </h2>
              <button
                onClick={() => onNavigate('reports')}
                className="text-xs font-mono text-cyan-400 hover:text-cyan-300"
              >
                View All
              </button>
            </div>

            {recentSimulations.length > 0 ? (
              <div className="space-y-3">
                {recentSimulations.map((run) => (
                  <div
                    key={run.id}
                    className="p-3 rounded-lg bg-dark-bg/60 border border-dark-border flex items-center justify-between text-xs"
                  >
                    <div>
                      <div className="font-semibold text-white flex items-center gap-2">
                        <span>{run.workload_profile} Profile</span>
                        <StatusBadge
                          status={run.cost_savings_pct > 0 ? `-${run.cost_savings_pct.toFixed(0)}% cost` : 'EQUAL'}
                          size="sm"
                          variant="success"
                        />
                      </div>
                      <div className="text-[10px] text-slate-400 font-mono mt-0.5">
                        Run #{run.id} • {run.total_steps} steps
                      </div>
                    </div>

                    <div className="text-right font-mono">
                      <div className="text-teal-400 font-bold">${run.predictive_cost.toFixed(2)}</div>
                      <div className="text-[10px] text-slate-500 line-through">
                        ${run.reactive_cost.toFixed(2)}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-6 text-center text-xs text-slate-400 border border-dashed border-slate-800 rounded-lg">
                No simulations executed yet. Run your first comparative benchmark in the Lab!
              </div>
            )}
          </div>

          <div className="mt-4 pt-4 border-t border-dark-border">
            <button
              onClick={() => onNavigate('simulation')}
              className="w-full py-2.5 rounded-lg bg-dark-border hover:bg-slate-700/60 border border-slate-700 text-slate-200 text-xs font-semibold tracking-wider uppercase transition-all flex items-center justify-center gap-2"
            >
              <Zap className="w-4 h-4 text-teal-400" />
              <span>Simulate Traffic Surge</span>
            </button>
          </div>
        </div>
      </div>

      {/* Cluster Node Fleet Grid */}
      <div className="bg-dark-card border border-dark-border rounded-xl p-5 shadow-lg">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-sm font-semibold text-white tracking-wide flex items-center gap-2">
              <Layers className="w-4 h-4 text-teal-400" />
              Simulated Cluster Fleet Topology
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Live worker node health, allocated resource slices, and spinning states
            </p>
          </div>
          <button
            onClick={() => onNavigate('optimization')}
            className="text-xs font-mono text-teal-400 hover:text-teal-300 flex items-center gap-1"
          >
            Manage Fleet <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {simulatedNodes.map((node) => (
            <InstanceCard
              key={node.id}
              id={node.id}
              status={node.status}
              capacityRps={settings?.capacity_per_instance_rps || 200}
              cpuUsage={node.cpu}
              memoryUsage={node.memory}
              uptimeTicks={node.uptime}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

export default Overview;
