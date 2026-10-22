"""Synthetic Cloud Workload Generator for CloudPulse AI.

Generates realistic, reproducible time-series cloud telemetry incorporating:
- Diurnal sine-wave daily cycles (peak hours vs trough off-peak)
- Weekly business-day vs weekend workload modulations
- Poisson-distributed burst spikes simulating sudden traffic surges
"""

from pathlib import Path
from typing import Optional
import numpy as np
import pandas as pd


def generate_synthetic_workload(
    days: int = 14,
    interval_minutes: int = 5,
    seed: int = 42,
    output_path: Optional[str | Path] = None,
) -> pd.DataFrame:
    """Generate reproducible multi-day cloud workload telemetry.

    Args:
        days: Total duration in days (default: 14).
        interval_minutes: Interval between consecutive readings (default: 5).
        seed: Random seed for exact reproducibility (default: 42).
        output_path: Optional file path to persist CSV data.

    Returns:
        pd.DataFrame with columns:
        ['timestamp', 'cpu_usage', 'memory_usage', 'request_count', 'response_time']
    """
    rng = np.random.default_rng(seed)

    # 14 days at 5-min intervals = 4,032 time steps
    steps_per_day = (24 * 60) // interval_minutes
    total_steps = days * steps_per_day

    # Base timestamp starting at beginning of month
    start_time = pd.Timestamp("2026-03-01 00:00:00")
    timestamps = pd.date_range(start=start_time, periods=total_steps, freq=f"{interval_minutes}min")

    # Time-based numerical features
    hour_fraction = timestamps.hour + (timestamps.minute / 60.0)
    day_of_week = timestamps.dayofweek  # 0=Monday, 6=Sunday

    # 1. Diurnal cycle: sine wave peaking around 14:00 (2 PM) and trough around 03:00 (3 AM)
    # Phase shift: (hour - 8) * (2*pi / 24) peaks at hour 14
    diurnal_wave = 0.5 * (1.0 + np.sin((hour_fraction - 8.0) * 2.0 * np.pi / 24.0))

    # 2. Weekly cycle: Weekdays (0-4) experience higher baseline than weekends (5-6)
    weekend_mask = day_of_week >= 5
    weekly_multiplier = np.where(weekend_mask, 0.65, 1.0)
    # Slight mid-week peak (Tuesday-Thursday)
    midweek_boost = np.where((day_of_week >= 1) & (day_of_week <= 3), 1.1, 1.0)
    weekly_factor = weekly_multiplier * midweek_boost

    # Combined base demand factor [0.2 to 1.1]
    base_demand = (0.25 + 0.65 * diurnal_wave) * weekly_factor

    # 3. Poisson spikes: rare burst events simulating microservice spikes or batch jobs
    spike_occurrences = rng.poisson(lam=0.03, size=total_steps)
    spike_magnitudes = rng.uniform(1.8, 3.2, size=total_steps) * spike_occurrences

    # Base request count: nominal 1,200 req/5-min scaled by demand and spikes
    noise_requests = rng.normal(0, 40, size=total_steps)
    request_count = (1200.0 * base_demand * (1.0 + 0.45 * spike_magnitudes)) + noise_requests
    request_count = np.maximum(50, np.round(request_count)).astype(int)

    # 4. CPU usage: Strongly correlated with request count + Gaussian jitter
    # Range 0-100%
    cpu_noise = rng.normal(0, 2.5, size=total_steps)
    cpu_usage = 12.0 + (request_count / 28.0) + (spike_magnitudes * 18.0) + cpu_noise
    cpu_usage = np.clip(cpu_usage, 5.0, 99.5)
    cpu_usage = np.round(cpu_usage, 2)

    # 5. Memory usage: Slower dynamics with baseline hysteresis and cache buildup
    # Smooth moving trend + diurnal variation
    mem_base = 35.0 + 28.0 * diurnal_wave * weekly_multiplier
    mem_noise = rng.normal(0, 1.5, size=total_steps)
    memory_usage = mem_base + (cpu_usage * 0.22) + mem_noise
    memory_usage = np.clip(memory_usage, 15.0, 98.0)
    memory_usage = np.round(memory_usage, 2)

    # 6. Response time (ms): Base latency ~25ms, increasing non-linearly when CPU exceeds 75%
    overload_penalty = np.where(cpu_usage > 75.0, np.exp((cpu_usage - 75.0) / 7.0) * 8.0, 0.0)
    latency_noise = rng.exponential(scale=3.0, size=total_steps)
    response_time = 22.0 + (request_count / 140.0) + overload_penalty + latency_noise
    response_time = np.clip(response_time, 8.0, 1200.0)
    response_time = np.round(response_time, 2)

    df = pd.DataFrame(
        {
            "timestamp": timestamps,
            "cpu_usage": cpu_usage,
            "memory_usage": memory_usage,
            "request_count": request_count,
            "response_time": response_time,
        }
    )

    if output_path is not None:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False)

    return df


if __name__ == "__main__":
    default_out = Path(__file__).resolve().parents[2] / "data" / "sample_workload.csv"
    df = generate_synthetic_workload(output_path=default_out)
    print(f"Generated {len(df)} workload records -> {default_out}")
