/**
 * Strict TypeScript Interfaces for CloudPulse AI.
 * Mirrors all backend Pydantic v2 schemas and models.
 */

export interface HealthResponse {
  status: string;
  timestamp: string;
  service: string;
}

export interface DatasetRow {
  timestamp: string;
  cpu_usage: number;
  memory_usage: number;
  request_count: number;
  response_time: number;
}

export interface DatasetPreviewResponse {
  total_rows: number;
  time_bounds: {
    start: string;
    end: string;
  };
  null_counts: Record<string, number>;
  rows: DatasetRow[];
}

export interface DatasetUploadResponse {
  message: string;
  total_rows: number;
  valid_rows: number;
  time_bounds: {
    start: string;
    end: string;
  };
}

export interface TrainModelRequest {
  n_estimators?: number;
  random_state?: number;
}

export interface EvaluationMetrics {
  mae: number;
  rmse: number;
}

export interface ResourceMetrics {
  random_forest: EvaluationMetrics;
  baseline: EvaluationMetrics;
}

export interface TrainModelResponse {
  message: string;
  trained_at: string;
  train_samples: number;
  test_samples: number;
  metrics: {
    cpu: ResourceMetrics;
    memory: ResourceMetrics;
  };
}

export interface PredictRequest {
  horizon_steps: number;
}

export interface ForecastItem {
  step: number;
  timestamp: string;
  cpu_usage: number;
  memory_usage: number;
}

export interface PredictResponse {
  horizon_steps: number;
  historical_context_steps: number;
  forecasts: ForecastItem[];
}

export interface SimulationRunRequest {
  profile: string;
  steps?: number;
  initial_instances?: number;
  custom_demand?: number[];
}

export interface PolicySimulationSummary {
  policy_name: string;
  total_ticks: number;
  sla_violations_count: number;
  sla_violation_rate_pct: number;
  avg_response_time_ms: number;
  p95_response_time_ms: number;
  avg_cpu_utilization_pct: number;
  over_provisioned_node_hours: number;
  under_provisioned_node_hours: number;
  scale_up_actions: number;
  scale_down_actions: number;
  total_scaling_actions: number;
  total_cost_usd: number;
}

export interface TimelineStep {
  tick: number;
  demand_rps: number;
  reactive_instances: number;
  predictive_instances: number;
  reactive_capacity: number;
  predictive_capacity: number;
  reactive_latency: number;
  predictive_latency: number;
  reactive_sla: boolean;
  predictive_sla: boolean;
  reactive_action: string;
  predictive_action: string;
}

export interface SimulationComparisonResponse {
  id: number;
  timestamp: string;
  workload_profile: string;
  total_steps: number;
  reactive: PolicySimulationSummary;
  predictive: PolicySimulationSummary;
  cost_savings_pct: number;
  sla_reduction_pct: number;
  timeline: TimelineStep[];
  disclaimer: string;
}

export interface SimulationHistoryItem {
  id: number;
  timestamp: string;
  workload_profile: string;
  total_steps: number;
  reactive_cost: number;
  predictive_cost: number;
  cost_savings_pct: number;
  reactive_sla_violations: number;
  predictive_sla_violations: number;
}

export interface SettingsUpdate {
  min_instances?: number;
  max_instances?: number;
  cooldown_ticks?: number;
  target_utilization?: number;
  capacity_per_instance_rps?: number;
  hourly_cost_per_node?: number;
}

export interface SettingsResponse {
  min_instances: number;
  max_instances: number;
  cooldown_ticks: number;
  target_utilization: number;
  capacity_per_instance_rps: number;
  hourly_cost_per_node: number;
  updated_at: string;
}

export type ActiveTab =
  | 'overview'
  | 'workload'
  | 'predictions'
  | 'optimization'
  | 'simulation'
  | 'reports'
  | 'settings';
