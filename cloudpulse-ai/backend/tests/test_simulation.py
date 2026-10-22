"""Unit tests for CloudPulse AI Discrete Resource Simulation Engine.

Verifies:
1. Instance counts strictly adhere to [min_instances, max_instances] bounds.
2. Cooldown interval strictly prevents flapping within cooldown ticks.
3. Predictive policy proactively provisions nodes before peak surge arrives.
"""

from typing import List
import pytest

from app.simulation.instance import VirtualInstance, InstanceStatus
from app.simulation.policies import ReactivePolicy, PredictivePolicy
from app.simulation.engine import ResourceSimulationEngine, WorkloadProfile, generate_profile_workload


def test_virtual_instance_lifecycle():
    """Verify VirtualInstance provisioning delay and activation transitions."""
    inst = VirtualInstance(capacity_rps=200.0, status=InstanceStatus.PROVISIONING, provision_delay_ticks=2)

    assert not inst.is_active
    assert inst.is_alive
    assert inst.uptime_ticks == 0

    # Tick 1: Still provisioning
    inst.tick()
    assert not inst.is_active
    assert inst.uptime_ticks == 1

    # Tick 2: Transitions to ACTIVE
    inst.tick()
    assert inst.is_active
    assert inst.uptime_ticks == 2

    # Termination
    inst.terminate()
    assert not inst.is_active
    assert not inst.is_alive
    assert inst.status == InstanceStatus.TERMINATING


def test_instance_bounds_min_max():
    """Verify instance count strictly respects min_instances and max_instances."""
    min_inst = 3
    max_inst = 7
    engine = ResourceSimulationEngine(instance_capacity_rps=200.0)

    # 1. Extreme surge workload (3000 RPS) pushing against upper bound
    extreme_surge = [3000.0] * 20
    policy_surge = ReactivePolicy(min_instances=min_inst, max_instances=max_inst, cooldown_ticks=1)
    res_surge = engine.run(policy_surge, extreme_surge, initial_instances=3)

    for step in res_surge["timeline"]:
        assert step["total_instances"] <= max_inst, (
            f"Step {step['tick']} exceeded max_instances: {step['total_instances']} > {max_inst}"
        )
        assert step["total_instances"] >= min_inst

    # 2. Complete lull workload (0 RPS) pushing against lower bound
    lull = [0.0] * 25
    policy_lull = ReactivePolicy(min_instances=min_inst, max_instances=max_inst, cooldown_ticks=1)
    res_lull = engine.run(policy_lull, lull, initial_instances=6)

    for step in res_lull["timeline"]:
        assert step["total_instances"] >= min_inst, (
            f"Step {step['tick']} dropped below min_instances: {step['total_instances']} < {min_inst}"
        )
        assert step["total_instances"] <= max_inst


def test_cooldown_strictly_enforced():
    """Verify no scaling actions occur within cooldown interval ticks."""
    cooldown = 4
    policy = ReactivePolicy(min_instances=2, max_instances=15, cooldown_ticks=cooldown)
    engine = ResourceSimulationEngine(instance_capacity_rps=200.0)

    # Continuous high demand that wants to scale up every single tick
    high_demand = [1500.0] * 20
    result = engine.run(policy, high_demand, initial_instances=2)

    timeline = result["timeline"]
    scaling_ticks: List[int] = [
        step["tick"] for step in timeline if step["action"].startswith("SCALE")
    ]

    assert len(scaling_ticks) > 1, "Expected multiple scaling actions across 20 steps"

    for i in range(1, len(scaling_ticks)):
        gap = scaling_ticks[i] - scaling_ticks[i - 1]
        assert gap >= cooldown, (
            f"Cooldown violated! Scale at tick {scaling_ticks[i]} happened only {gap} ticks "
            f"after tick {scaling_ticks[i-1]} (cooldown is {cooldown})"
        )


def test_predictive_scaling_proactive_provisioning():
    """Verify predictive scaling provisions instances before peak load arrives.

    Scenario:
    - Steps 0 to 13: Baseline demand of 350 RPS (served by 2 nodes = 400 RPS capacity).
    - Step 14: Demand surges to 1400 RPS (requires at least 7 nodes).
    - Steps 15 to 20: Sustained 1400 RPS demand.
    """
    baseline_steps = 14
    surge_steps = 7
    demand_series = [350.0] * baseline_steps + [1400.0] * surge_steps

    engine = ResourceSimulationEngine(
        instance_capacity_rps=200.0,
        provision_delay_ticks=1,
        r_base_ms=25.0,
    )

    # 1. Run Reactive Policy
    reactive_policy = ReactivePolicy(min_instances=2, max_instances=12, cooldown_ticks=2)
    reactive_res = engine.run(reactive_policy, demand_series, initial_instances=2)

    # 2. Run Predictive Policy (looks ahead 3 steps)
    predictive_policy = PredictivePolicy(
        min_instances=2,
        max_instances=12,
        cooldown_ticks=2,
        target_utilization=0.70,
        lookahead_steps=3,
    )
    predictive_res = engine.run(predictive_policy, demand_series, initial_instances=2)

    # Predictive policy should trigger scale-up BEFORE step 14
    predictive_timeline = predictive_res["timeline"]
    reactive_timeline = reactive_res["timeline"]

    predictive_scale_ticks = [
        s["tick"] for s in predictive_timeline if s["action"].startswith("SCALE_UP")
    ]
    reactive_scale_ticks = [
        s["tick"] for s in reactive_timeline if s["action"].startswith("SCALE_UP")
    ]

    # Predictive scaling scales up before the surge hits at step 14
    first_predictive_scale = predictive_scale_ticks[0]
    assert first_predictive_scale < 14, (
        f"Predictive policy failed to scale up early. Scaled at {first_predictive_scale}, expected < 14"
    )

    # At step 14 (when surge hits), Predictive policy already has higher active capacity
    pred_capacity_at_surge = predictive_timeline[14]["capacity_rps"]
    react_capacity_at_surge = reactive_timeline[14]["capacity_rps"]

    assert pred_capacity_at_surge > react_capacity_at_surge, (
        f"Predictive capacity at surge ({pred_capacity_at_surge}) should exceed "
        f"Reactive capacity ({react_capacity_at_surge})"
    )

    # Predictive policy has strictly fewer SLA violations during the surge
    assert predictive_res["sla_violations_count"] < reactive_res["sla_violations_count"], (
        f"Predictive SLA violations ({predictive_res['sla_violations_count']}) should be less "
        f"than Reactive ({reactive_res['sla_violations_count']})"
    )

    # Predictive policy achieves significantly lower P95 response time
    assert predictive_res["p95_response_time_ms"] < reactive_res["p95_response_time_ms"], (
        f"Predictive P95 latency ({predictive_res['p95_response_time_ms']}ms) should be lower "
        f"than Reactive ({reactive_res['p95_response_time_ms']}ms)"
    )


def test_workload_profiles_generation():
    """Verify standard workload profile generators produce valid non-empty arrays."""
    for profile in [WorkloadProfile.NORMAL, WorkloadProfile.SPIKE, WorkloadProfile.RAMP_UP, WorkloadProfile.DROP]:
        series = generate_profile_workload(profile, steps=30)
        assert len(series) == 30
        assert all(val >= 0.0 for val in series)
