import React, { useState } from 'react';
import {
  Zap,
  Play,
  RefreshCw,
  ShieldCheck,
  DollarSign,
  Clock,
  Activity,
  Layers,
  ArrowRight,
  TrendingDown,
  Info,
} from 'lucide-react';
import { api } from '../api/client';
import { SimulationComparisonResponse } from '../types';
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from 'recharts';

export const SimulationLab: React.FC = () => {
  const [profile, setProfile] = useState<string>('Spike');
  const [steps, setSteps] = useState<number>(50);
  const [initialInstances, setInitialInstances] = useState<number>(2);
  const [simResult, setSimResult] = useState<SimulationComparisonResponse | null>(null);
  const [running, setRunning] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const scenarioProfiles = [
    { id: 'Spike', name: 'Traffic Spike', desc: 'Acute traffic burst (1600 RPS) between ticks 20 and 26' },
    { id: 'Normal', name: 'Normal / Diurnal', desc: 'Steady cyclic 24-hour sinusoidal wave (~500 RPS)' },
    { id: 'Ramp-up', name: 'Gradual Climb', desc: 'Monotonic linear demand increase from 200 to 1800 RPS' },
    { id: 'Drop', name: 'Sudden Drop', desc: 'High load (1600 RPS) plunging abruptly to 250 RPS' },
  ];

  const handleRunSimulation = async () => {
    try {
      setRunning(true);
      setErrorMsg(null);
      const res = await api.runSimulation({
        profile,
        steps,
        initial_instances: initialInstances,
      });
      setSimResult(res);
    } catch (err: any) {
      console.error('Simulation execution failed', err);
      setErrorMsg(err.response?.data?.detail || 'Simulation execution failed.');
    } finally {
      setRunning(false);
    }
  };

  // Recharts chart data from simulation comparison timeline
  const chartData = (simResult?.timeline || []).map((step) => ({
    tick: `t+${step.tick}`,
    demand: step.demand_rps,
    reactiveCap: step.reactive_capacity,
    predictiveCap: step.predictive_capacity,
    reactiveLatency: step.reactive_latency,
    predictiveLatency: step.predictive_latency,
  }));

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Simulation Scenario Configuration Card */}
      <div className="bg-dark-card border border-dark-border rounded-xl p-5 shadow-lg">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-5">
          <div>
            <h2 className="text-sm font-semibold text-white tracking-wide flex items-center gap-2">
              <Zap className="w-5 h-5 text-teal-400" />
              Autoscaling Discrete Simulation Lab
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Benchmark Reactive threshold policies against Lookahead Predictive policies under adverse traffic patterns
            </p>
          </div>

          <button
            onClick={handleRunSimulation}
            disabled={running}
            className="flex items-center gap-2 px-5 py-2.5 rounded-lg bg-teal-500 hover:bg-teal-400 text-dark-bg font-bold text-xs tracking-wider uppercase transition-all shadow-lg shadow-teal-500/20 disabled:opacity-50"
          >
            {running ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Simulating Ticks...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-current" />
                <span>Execute Simulation</span>
              </>
            )}
          </button>
        </div>

        {/* Profile Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 mb-4">
          {scenarioProfiles.map((p) => (
            <div
              key={p.id}
              onClick={() => setProfile(p.id)}
              className={`p-3.5 rounded-xl border cursor-pointer transition-all ${
                profile === p.id
                  ? 'border-teal-500 bg-teal-500/10 shadow-sm'
                  : 'border-dark-border bg-dark-bg/60 hover:border-slate-700'
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="font-semibold text-xs text-white">{p.name}</span>
                <span
                  className={`w-2 h-2 rounded-full ${
                    profile === p.id ? 'bg-teal-400 ring-4 ring-teal-400/20' : 'bg-slate-700'
                  }`}
                />
              </div>
              <p className="text-[11px] text-slate-400">{p.desc}</p>
            </div>
          ))}
        </div>

        {/* Step Parameters */}
        <div className="flex flex-wrap items-center gap-6 pt-3 border-t border-dark-border/60 text-xs font-mono">
          <div className="flex items-center gap-2">
            <span className="text-slate-400">Total Steps:</span>
            <input
              type="number"
              value={steps}
              onChange={(e) => setSteps(Math.max(10, Math.min(200, Number(e.target.value))))}
              className="w-16 px-2 py-1 rounded bg-dark-bg border border-dark-border text-teal-400 font-bold"
            />
            <span className="text-slate-500">ticks ({(steps * 5)} mins)</span>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-slate-400">Initial Nodes:</span>
            <input
              type="number"
              value={initialInstances}
              onChange={(e) => setInitialInstances(Math.max(1, Math.min(10, Number(e.target.value))))}
              className="w-16 px-2 py-1 rounded bg-dark-bg border border-dark-border text-teal-400 font-bold"
            />
            <span className="text-slate-500">instances</span>
          </div>
        </div>

        {errorMsg && (
          <div className="mt-3 p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs font-mono">
            {errorMsg}
          </div>
        )}
      </div>

      {/* Side-by-Side Comparison Cards */}
      {simResult && (
        <div className="space-y-6">
          {/* Headline Results */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Cost Comparison */}
            <div className="bg-dark-card border border-dark-border rounded-xl p-5 shadow-lg flex flex-col justify-between">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">
                  Infrastructure Cost
                </span>
                <DollarSign className="w-5 h-5 text-emerald-400" />
              </div>

              <div className="flex items-baseline justify-between mb-2">
                <div>
                  <div className="text-2xl font-bold font-mono text-teal-400">
                    ${simResult.predictive.total_cost_usd.toFixed(2)}
                  </div>
                  <div className="text-[10px] text-slate-400 font-mono">Predictive Policy</div>
                </div>

                <div className="text-right">
                  <div className="text-lg font-bold font-mono text-slate-400 line-through">
                    ${simResult.reactive.total_cost_usd.toFixed(2)}
                  </div>
                  <div className="text-[10px] text-slate-500 font-mono">Reactive Policy</div>
                </div>
              </div>

              <div className="p-2 rounded bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-mono flex items-center gap-1.5 font-bold">
                <TrendingDown className="w-4 h-4" />
                <span>{simResult.cost_savings_pct}% Cost Reduction</span>
              </div>
            </div>

            {/* SLA Violations Comparison */}
            <div className="bg-dark-card border border-dark-border rounded-xl p-5 shadow-lg flex flex-col justify-between">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">
                  SLA Outage Violations
                </span>
                <ShieldCheck className="w-5 h-5 text-teal-400" />
              </div>

              <div className="flex items-baseline justify-between mb-2">
                <div>
                  <div className="text-2xl font-bold font-mono text-emerald-400">
                    {simResult.predictive.sla_violations_count}
                  </div>
                  <div className="text-[10px] text-slate-400 font-mono">
                    Predictive ({simResult.predictive.sla_violation_rate_pct}%)
                  </div>
                </div>

                <div className="text-right">
                  <div className="text-lg font-bold font-mono text-rose-400">
                    {simResult.reactive.sla_violations_count}
                  </div>
                  <div className="text-[10px] text-slate-500 font-mono">
                    Reactive ({simResult.reactive.sla_violation_rate_pct}%)
                  </div>
                </div>
              </div>

              <div className="p-2 rounded bg-teal-500/10 border border-teal-500/20 text-teal-300 text-xs font-mono">
                Proactive spin-up neutralized spin-up lag during burst
              </div>
            </div>

            {/* Latency P95 */}
            <div className="bg-dark-card border border-dark-border rounded-xl p-5 shadow-lg flex flex-col justify-between">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">
                  P95 Simulated Latency
                </span>
                <Clock className="w-5 h-5 text-cyan-400" />
              </div>

              <div className="flex items-baseline justify-between mb-2">
                <div>
                  <div className="text-2xl font-bold font-mono text-cyan-400">
                    {simResult.predictive.p95_response_time_ms.toFixed(1)}ms
                  </div>
                  <div className="text-[10px] text-slate-400 font-mono">Predictive P95</div>
                </div>

                <div className="text-right">
                  <div className="text-lg font-bold font-mono text-slate-400">
                    {simResult.reactive.p95_response_time_ms.toFixed(1)}ms
                  </div>
                  <div className="text-[10px] text-slate-500 font-mono">Reactive P95</div>
                </div>
              </div>

              <div className="p-2 rounded bg-dark-bg border border-dark-border text-slate-400 text-xs font-mono">
                Over-provisioned: {simResult.predictive.over_provisioned_node_hours} node-hrs
              </div>
            </div>
          </div>

          {/* Timeline Chart */}
          <div className="bg-dark-card border border-dark-border rounded-xl p-5 shadow-lg">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-sm font-semibold text-white tracking-wide">
                  Comparative Throughput Capacity vs Incoming Demand
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Visualizing proactive scaling response vs reactive lag along the simulation timeline
                </p>
              </div>
            </div>

            <div className="h-80 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={chartData} margin={{ top: 15, right: 15, left: -10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} />
                  <XAxis dataKey="tick" stroke="#64748b" tick={{ fontSize: 11 }} />
                  <YAxis stroke="#64748b" tick={{ fontSize: 11 }} unit=" RPS" />
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
                  <Area
                    type="stepAfter"
                    dataKey="demand"
                    name="Workload Demand (RPS)"
                    fill="#3b82f6"
                    fillOpacity={0.15}
                    stroke="#3b82f6"
                    strokeWidth={1.5}
                  />
                  <Line
                    type="stepAfter"
                    dataKey="reactiveCap"
                    name="Reactive Capacity"
                    stroke="#f43f5e"
                    strokeWidth={2}
                    strokeDasharray="4 4"
                    dot={false}
                  />
                  <Line
                    type="stepAfter"
                    dataKey="predictiveCap"
                    name="Predictive Capacity"
                    stroke="#14b8a6"
                    strokeWidth={2.5}
                    dot={false}
                  />
                </ComposedChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}

      {/* Transparency Note */}
      <div className="p-4 rounded-xl bg-dark-card/60 border border-slate-800 flex items-start gap-3 text-xs text-slate-400">
        <Info className="w-5 h-5 text-teal-400 shrink-0 mt-0.5" />
        <div>
          <div className="font-semibold text-slate-300">Simulation Engine Notice</div>
          <div>
            All response times, cluster states, and instance metrics are generated by CloudPulse AI’s discrete event queueing model for capacity planning and policy tuning.
          </div>
        </div>
      </div>
    </div>
  );
};

export default SimulationLab;
