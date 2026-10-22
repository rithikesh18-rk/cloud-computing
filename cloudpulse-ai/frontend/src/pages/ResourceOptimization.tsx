import React, { useState, useEffect } from 'react';
import {
  Cpu,
  Server,
  Sliders,
  ShieldAlert,
  ArrowUp,
  ArrowDown,
  Layers,
  Activity,
  Plus,
  Minus,
} from 'lucide-react';
import { InstanceCard } from '../components/InstanceCard';
import { api } from '../api/client';
import { SettingsResponse } from '../types';

export const ResourceOptimization: React.FC = () => {
  const [settings, setSettings] = useState<SettingsResponse | null>(null);
  const [nodes, setNodes] = useState([
    { id: 'worker-node-01', status: 'ACTIVE', cpu: 64.2, memory: 58.1, uptime: 154 },
    { id: 'worker-node-02', status: 'ACTIVE', cpu: 71.8, memory: 62.4, uptime: 154 },
    { id: 'worker-node-03', status: 'ACTIVE', cpu: 55.0, memory: 51.9, uptime: 110 },
    { id: 'worker-node-04', status: 'ACTIVE', cpu: 68.4, memory: 64.0, uptime: 42 },
  ]);

  useEffect(() => {
    api.getSettings().then(setSettings).catch(console.error);
  }, []);

  const totalCapacity = nodes.filter((n) => n.status === 'ACTIVE').length * (settings?.capacity_per_instance_rps || 200);
  const currentDemand = 540.0;
  const clusterLoadPct = (currentDemand / totalCapacity) * 100;

  const handleAddNode = () => {
    if (nodes.length >= (settings?.max_instances || 20)) return;
    const newId = `worker-node-0${nodes.length + 1}`;
    setNodes([...nodes, { id: newId, status: 'PROVISIONING', cpu: 5.0, memory: 20.0, uptime: 1 }]);
    setTimeout(() => {
      setNodes((prev) =>
        prev.map((n) => (n.id === newId ? { ...n, status: 'ACTIVE', cpu: 45.0, memory: 40.0 } : n))
      );
    }, 2500);
  };

  const handleDrainNode = () => {
    if (nodes.length <= (settings?.min_instances || 2)) return;
    const lastNode = nodes[nodes.length - 1];
    setNodes((prev) =>
      prev.map((n) => (n.id === lastNode.id ? { ...n, status: 'TERMINATING' } : n))
    );
    setTimeout(() => {
      setNodes((prev) => prev.filter((n) => n.id !== lastNode.id));
    }, 1500);
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Cluster Headroom Gauge & Threshold Banner */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Gauge Card */}
        <div className="md:col-span-2 bg-dark-card border border-dark-border rounded-xl p-5 shadow-lg flex flex-col justify-between">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-sm font-semibold text-white tracking-wide flex items-center gap-2">
                <Cpu className="w-5 h-5 text-teal-400" />
                Cluster Operational Headroom & Capacity Margin
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Current cluster throughput vs aggregate incoming workload demand
              </p>
            </div>
            <span className="text-xs font-mono px-2.5 py-1 rounded-md bg-teal-500/10 text-teal-400 border border-teal-500/30 font-bold">
              {clusterLoadPct.toFixed(1)}% SATURATION
            </span>
          </div>

          {/* Visual Headroom Bar */}
          <div className="space-y-3">
            <div className="flex justify-between items-center text-xs font-mono text-slate-300">
              <span>Current Demand: <strong className="text-white">{currentDemand} RPS</strong></span>
              <span>Available Capacity: <strong className="text-teal-400">{totalCapacity} RPS</strong></span>
            </div>

            <div className="relative w-full h-4 bg-slate-800 rounded-full overflow-hidden border border-slate-700">
              <div
                className="h-full bg-gradient-to-r from-teal-500 via-cyan-400 to-amber-400 transition-all duration-500 rounded-full"
                style={{ width: `${Math.min(100, clusterLoadPct)}%` }}
              />
              {/* Threshold Gate Indicators */}
              <div
                className="absolute top-0 bottom-0 w-0.5 bg-rose-500 z-10"
                style={{ left: '75%' }}
                title="Scale-Up Gate (75%)"
              />
              <div
                className="absolute top-0 bottom-0 w-0.5 bg-cyan-400 z-10"
                style={{ left: '30%' }}
                title="Scale-Down Gate (30%)"
              />
            </div>

            <div className="flex justify-between text-[11px] font-mono text-slate-500">
              <span>0 RPS</span>
              <span className="text-cyan-400 flex items-center gap-1">
                <ArrowDown className="w-3 h-3" /> Scale-Down Threshold (30%)
              </span>
              <span className="text-rose-400 flex items-center gap-1">
                <ArrowUp className="w-3 h-3" /> Scale-Up Threshold (75%)
              </span>
              <span>{totalCapacity} RPS</span>
            </div>
          </div>
        </div>

        {/* Fleet Scaling Controls */}
        <div className="bg-dark-card border border-dark-border rounded-xl p-5 shadow-lg flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Sliders className="w-5 h-5 text-violet-400" />
              <h3 className="text-sm font-semibold text-white tracking-wide">
                Manual Fleet Overrides
              </h3>
            </div>
            <p className="text-xs text-slate-400 mb-4">
              Directly inject or drain virtual nodes in the simulated cluster
            </p>

            <div className="space-y-2 text-xs font-mono text-slate-300">
              <div className="flex justify-between py-1 border-b border-dark-border/60">
                <span className="text-slate-400">Node Limit Range:</span>
                <span className="text-white">[{settings?.min_instances || 2} min, {settings?.max_instances || 20} max]</span>
              </div>
              <div className="flex justify-between py-1 border-b border-dark-border/60">
                <span className="text-slate-400">Node Spin-Up Delay:</span>
                <span className="text-teal-400 font-bold">1 tick (5 min)</span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-slate-400">Hourly Unit Rate:</span>
                <span className="text-slate-200">${(settings?.hourly_cost_per_node || 0.05).toFixed(2)}/node/hr</span>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3 mt-4">
            <button
              onClick={handleAddNode}
              className="py-2.5 px-3 rounded-lg bg-teal-500/15 hover:bg-teal-500/25 border border-teal-500/30 text-teal-300 text-xs font-mono font-semibold flex items-center justify-center gap-1.5 transition-colors"
            >
              <Plus className="w-4 h-4" /> Add Node
            </button>
            <button
              onClick={handleDrainNode}
              className="py-2.5 px-3 rounded-lg bg-rose-500/15 hover:bg-rose-500/25 border border-rose-500/30 text-rose-300 text-xs font-mono font-semibold flex items-center justify-center gap-1.5 transition-colors"
            >
              <Minus className="w-4 h-4" /> Drain Node
            </button>
          </div>
        </div>
      </div>

      {/* Cluster Node Fleet Visualization */}
      <div className="bg-dark-card border border-dark-border rounded-xl p-5 shadow-lg">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-semibold text-white tracking-wide flex items-center gap-2">
              <Layers className="w-4 h-4 text-teal-400" />
              Live Virtual Worker Node Fleet ({nodes.length} Instances)
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Individual node utilization slices and active lifecycle status
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {nodes.map((node) => (
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

export default ResourceOptimization;
