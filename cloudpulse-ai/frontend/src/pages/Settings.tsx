import React, { useState, useEffect } from 'react';
import {
  Sliders,
  Save,
  RotateCcw,
  CheckCircle2,
  AlertTriangle,
  Info,
  Server,
  DollarSign,
  Cpu,
} from 'lucide-react';
import { api } from '../api/client';
import { SettingsResponse } from '../types';

export const Settings: React.FC = () => {
  const [settings, setSettings] = useState<SettingsResponse | null>(null);
  const [formData, setFormData] = useState({
    min_instances: 2,
    max_instances: 20,
    cooldown_ticks: 3,
    target_utilization: 0.70,
    capacity_per_instance_rps: 200.0,
    hourly_cost_per_node: 0.05,
  });

  const [saving, setSaving] = useState<boolean>(false);
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    api.getSettings().then((data) => {
      setSettings(data);
      setFormData({
        min_instances: data.min_instances,
        max_instances: data.max_instances,
        cooldown_ticks: data.cooldown_ticks,
        target_utilization: data.target_utilization,
        capacity_per_instance_rps: data.capacity_per_instance_rps,
        hourly_cost_per_node: data.hourly_cost_per_node,
      });
    }).catch(console.error);
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.min_instances > formData.max_instances) {
      setFeedback({
        type: 'error',
        text: 'Minimum instances cannot exceed maximum instances.',
      });
      return;
    }

    try {
      setSaving(true);
      setFeedback(null);
      const updated = await api.updateSettings(formData);
      setSettings(updated);
      setFeedback({ type: 'success', text: 'Settings successfully updated in database.' });
    } catch (err: any) {
      setFeedback({
        type: 'error',
        text: err.response?.data?.detail || 'Failed to update system settings.',
      });
    } finally {
      setSaving(false);
    }
  };

  const handleResetDefaults = () => {
    setFormData({
      min_instances: 2,
      max_instances: 20,
      cooldown_ticks: 3,
      target_utilization: 0.70,
      capacity_per_instance_rps: 200.0,
      hourly_cost_per_node: 0.05,
    });
    setFeedback({ type: 'success', text: 'Reset parameters to factory defaults (unsaved).' });
  };

  return (
    <div className="p-6 space-y-6 max-w-4xl mx-auto">
      {/* Settings Form Container */}
      <div className="bg-dark-card border border-dark-border rounded-xl p-6 shadow-lg">
        <div className="flex items-center justify-between pb-4 border-b border-dark-border mb-6">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-teal-500/10 border border-teal-500/30 text-teal-400">
              <Sliders className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-sm font-semibold text-white tracking-wide">
                Runtime Autoscaling & Billing Parameters
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Configure cluster boundary limits, scaling hysteresis, and node pricing
              </p>
            </div>
          </div>

          {settings?.updated_at && (
            <span className="text-[10px] font-mono text-slate-500">
              Last saved: {settings.updated_at.replace('T', ' ').slice(0, 19)}
            </span>
          )}
        </div>

        <form onSubmit={handleSave} className="space-y-6">
          {/* Section 1: Fleet Boundaries */}
          <div>
            <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-teal-400 mb-3">
              <Server className="w-4 h-4" /> Cluster Fleet Bounds
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">
                  Minimum Instances (Floor)
                </label>
                <input
                  type="number"
                  min="1"
                  max="50"
                  value={formData.min_instances}
                  onChange={(e) => setFormData({ ...formData, min_instances: Number(e.target.value) })}
                  className="w-full px-3 py-2 rounded-lg bg-dark-bg border border-dark-border text-white text-xs font-mono focus:border-teal-500 focus:outline-none"
                />
                <span className="text-[11px] text-slate-500 mt-1 block">
                  Autoscaler will never drop instance count below this floor.
                </span>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">
                  Maximum Instances (Ceiling)
                </label>
                <input
                  type="number"
                  min="1"
                  max="100"
                  value={formData.max_instances}
                  onChange={(e) => setFormData({ ...formData, max_instances: Number(e.target.value) })}
                  className="w-full px-3 py-2 rounded-lg bg-dark-bg border border-dark-border text-white text-xs font-mono focus:border-teal-500 focus:outline-none"
                />
                <span className="text-[11px] text-slate-500 mt-1 block">
                  Hard budget cap to prevent runaway scaling during catastrophic bursts.
                </span>
              </div>
            </div>
          </div>

          {/* Section 2: Scaling Hysteresis & Target Utilization */}
          <div className="pt-4 border-t border-dark-border/60">
            <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-cyan-400 mb-3">
              <Cpu className="w-4 h-4" /> Policy Dynamics & Target Margins
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">
                  Cooldown Interval (Ticks)
                </label>
                <input
                  type="number"
                  min="0"
                  max="20"
                  value={formData.cooldown_ticks}
                  onChange={(e) => setFormData({ ...formData, cooldown_ticks: Number(e.target.value) })}
                  className="w-full px-3 py-2 rounded-lg bg-dark-bg border border-dark-border text-white text-xs font-mono focus:border-teal-500 focus:outline-none"
                />
                <span className="text-[11px] text-slate-500 mt-1 block">
                  Minimum ticks between scaling actions to prevent flapping ({formData.cooldown_ticks * 5} min).
                </span>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">
                  Target Utilization Ratio
                </label>
                <input
                  type="number"
                  step="0.05"
                  min="0.30"
                  max="0.95"
                  value={formData.target_utilization}
                  onChange={(e) => setFormData({ ...formData, target_utilization: Number(e.target.value) })}
                  className="w-full px-3 py-2 rounded-lg bg-dark-bg border border-dark-border text-white text-xs font-mono focus:border-teal-500 focus:outline-none"
                />
                <span className="text-[11px] text-slate-500 mt-1 block">
                  Target cluster load for predictive policy sizing ({(formData.target_utilization * 100).toFixed(0)}%).
                </span>
              </div>
            </div>
          </div>

          {/* Section 3: Cost & Hardware Sizing */}
          <div className="pt-4 border-t border-dark-border/60">
            <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-emerald-400 mb-3">
              <DollarSign className="w-4 h-4" /> Capacity & Unit Billing
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">
                  Instance Capacity (RPS)
                </label>
                <input
                  type="number"
                  min="50"
                  max="5000"
                  value={formData.capacity_per_instance_rps}
                  onChange={(e) => setFormData({ ...formData, capacity_per_instance_rps: Number(e.target.value) })}
                  className="w-full px-3 py-2 rounded-lg bg-dark-bg border border-dark-border text-white text-xs font-mono focus:border-teal-500 focus:outline-none"
                />
                <span className="text-[11px] text-slate-500 mt-1 block">
                  Nominal throughput handled by one healthy worker node before queueing latency.
                </span>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">
                  Hourly Cost per Node ($ USD)
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="0.001"
                  max="10.0"
                  value={formData.hourly_cost_per_node}
                  onChange={(e) => setFormData({ ...formData, hourly_cost_per_node: Number(e.target.value) })}
                  className="w-full px-3 py-2 rounded-lg bg-dark-bg border border-dark-border text-white text-xs font-mono focus:border-teal-500 focus:outline-none"
                />
                <span className="text-[11px] text-slate-500 mt-1 block">
                  Simulated cloud billing rate per compute instance-hour.
                </span>
              </div>
            </div>
          </div>

          {feedback && (
            <div
              className={`p-3.5 rounded-lg text-xs flex items-center gap-2 border font-mono ${
                feedback.type === 'success'
                  ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                  : 'bg-rose-500/10 text-rose-400 border-rose-500/30'
              }`}
            >
              {feedback.type === 'success' ? (
                <CheckCircle2 className="w-4 h-4 shrink-0" />
              ) : (
                <AlertTriangle className="w-4 h-4 shrink-0" />
              )}
              <span>{feedback.text}</span>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex items-center justify-between pt-4 border-t border-dark-border">
            <button
              type="button"
              onClick={handleResetDefaults}
              className="flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-dark-border hover:bg-slate-700 text-slate-300 text-xs font-semibold transition-colors"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reset Defaults</span>
            </button>

            <button
              type="submit"
              disabled={saving}
              className="flex items-center gap-2 px-5 py-2 rounded-lg bg-teal-500 hover:bg-teal-400 text-dark-bg font-bold text-xs tracking-wider uppercase transition-all shadow-lg shadow-teal-500/20 disabled:opacity-50"
            >
              <Save className="w-4 h-4" />
              <span>{saving ? 'Saving...' : 'Save Configuration'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Settings;
