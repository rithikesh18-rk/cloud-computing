import React, { useState, useEffect } from 'react';
import {
  FileSpreadsheet,
  Download,
  Calendar,
  ShieldCheck,
  DollarSign,
  TrendingUp,
  BarChart2,
} from 'lucide-react';
import { api } from '../api/client';
import { SimulationHistoryItem } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from 'recharts';

export const ExperimentReports: React.FC = () => {
  const [history, setHistory] = useState<SimulationHistoryItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  const fetchHistory = async () => {
    try {
      setLoading(true);
      const data = await api.getSimulationHistory(20);
      setHistory(data);
    } catch (err: any) {
      console.error('Failed to load simulation history', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  // Format comparative chart data across runs
  const comparativeCostData = history.slice(0, 6).map((run) => ({
    name: `Run #${run.id} (${run.workload_profile})`,
    reactiveCost: run.reactive_cost,
    predictiveCost: run.predictive_cost,
  }));

  const comparativeSlaData = history.slice(0, 6).map((run) => ({
    name: `Run #${run.id}`,
    reactiveSla: run.reactive_sla_violations,
    predictiveSla: run.predictive_sla_violations,
  }));

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="bg-dark-card border border-dark-border rounded-xl p-5 shadow-lg flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2">
            <FileSpreadsheet className="w-5 h-5 text-teal-400" />
            <h2 className="text-sm font-semibold text-white tracking-wide">
              Historical Simulation Experiments & Audit Log
            </h2>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Compare cost efficiency, SLA compliance, and export full step-by-step CSV telemetry
          </p>
        </div>

        <button
          onClick={fetchHistory}
          className="text-xs font-mono text-teal-400 hover:text-teal-300 px-3 py-1.5 rounded-lg border border-teal-500/30 bg-teal-500/10"
        >
          Refresh Logs
        </button>
      </div>

      {/* Comparative Charts: Cost & SLA */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Cost Comparison Across Runs */}
        <div className="bg-dark-card border border-dark-border rounded-xl p-5 shadow-lg">
          <div className="flex items-center gap-2 mb-4">
            <DollarSign className="w-4 h-4 text-emerald-400" />
            <h3 className="text-sm font-semibold text-white tracking-wide">
              Total Cost Comparison ($ USD)
            </h3>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={comparativeCostData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} />
                <XAxis dataKey="name" stroke="#64748b" tick={{ fontSize: 10 }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 11 }} unit="$" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#111827',
                    borderColor: '#1f2937',
                    borderRadius: '8px',
                    fontSize: '12px',
                    fontFamily: 'JetBrains Mono, monospace',
                  }}
                />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                <Bar dataKey="reactiveCost" name="Reactive Cost ($)" fill="#f43f5e" radius={[4, 4, 0, 0]} />
                <Bar dataKey="predictiveCost" name="Predictive Cost ($)" fill="#14b8a6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* SLA Violations Across Runs */}
        <div className="bg-dark-card border border-dark-border rounded-xl p-5 shadow-lg">
          <div className="flex items-center gap-2 mb-4">
            <ShieldCheck className="w-4 h-4 text-teal-400" />
            <h3 className="text-sm font-semibold text-white tracking-wide">
              SLA Violations (Steps with Capacity Deficit)
            </h3>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={comparativeSlaData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} />
                <XAxis dataKey="name" stroke="#64748b" tick={{ fontSize: 11 }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#111827',
                    borderColor: '#1f2937',
                    borderRadius: '8px',
                    fontSize: '12px',
                    fontFamily: 'JetBrains Mono, monospace',
                  }}
                />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                <Bar dataKey="reactiveSla" name="Reactive Violations" fill="#f43f5e" radius={[4, 4, 0, 0]} />
                <Bar dataKey="predictiveSla" name="Predictive Violations" fill="#10b981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Experiments Table */}
      <div className="bg-dark-card border border-dark-border rounded-xl p-5 shadow-lg">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-semibold text-white tracking-wide">
            Historical Experiment Table
          </h3>
          <span className="text-xs font-mono text-slate-400">
            {history.length} records in SQLite
          </span>
        </div>

        <div className="overflow-x-auto max-h-96 border border-dark-border rounded-lg">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-dark-bg/80 text-slate-400 uppercase tracking-wider sticky top-0 border-b border-dark-border">
              <tr>
                <th className="py-2.5 px-4">Run ID</th>
                <th className="py-2.5 px-4">Timestamp</th>
                <th className="py-2.5 px-4">Workload Profile</th>
                <th className="py-2.5 px-4">Duration</th>
                <th className="py-2.5 px-4">Reactive Cost</th>
                <th className="py-2.5 px-4">Predictive Cost</th>
                <th className="py-2.5 px-4">Cost Savings</th>
                <th className="py-2.5 px-4 text-center">Export</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-dark-border/40 text-slate-300">
              {history.map((run) => (
                <tr key={run.id} className="hover:bg-dark-border/30 transition-colors">
                  <td className="py-2.5 px-4 text-slate-400 font-bold">#{run.id}</td>
                  <td className="py-2.5 px-4 text-slate-300">{run.timestamp.replace('T', ' ').slice(0, 19)}</td>
                  <td className="py-2.5 px-4">
                    <span className="px-2 py-0.5 rounded bg-dark-bg border border-dark-border text-white font-semibold">
                      {run.workload_profile}
                    </span>
                  </td>
                  <td className="py-2.5 px-4">{run.total_steps} ticks ({(run.total_steps * 5)}m)</td>
                  <td className="py-2.5 px-4 text-slate-400 font-semibold">${run.reactive_cost.toFixed(2)}</td>
                  <td className="py-2.5 px-4 text-teal-400 font-bold">${run.predictive_cost.toFixed(2)}</td>
                  <td className="py-2.5 px-4">
                    <span className="text-emerald-400 font-bold">
                      {run.cost_savings_pct > 0 ? `-${run.cost_savings_pct.toFixed(1)}%` : '0%'}
                    </span>
                  </td>
                  <td className="py-2.5 px-4 text-center">
                    <a
                      href={api.getSimulationExportUrl(run.id)}
                      download={`simulation_${run.id}.csv`}
                      className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-teal-500/10 hover:bg-teal-500/20 text-teal-400 border border-teal-500/30 transition-colors"
                    >
                      <Download className="w-3.5 h-3.5" />
                      <span>CSV</span>
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default ExperimentReports;
