"""Auto-Scaling Policies for Discrete Resource Simulation.

Implements:
1. ReactivePolicy: Threshold-based scaling reacting to current CPU/Memory saturation.
2. PredictivePolicy: Lookahead forecast-driven scaling that provisions nodes proactively
   before surge peaks arrive, neutralizing provisioning latency.
"""

from abc import ABC, abstractmethod
import math
from typing import List, Optional, Sequence
from app.simulation.instance import VirtualInstance


class BaseScalingPolicy(ABC):
    """Abstract base class for autoscaling policies."""

    def __init__(
        self,
        min_instances: int = 2,
        max_instances: int = 20,
        cooldown_ticks: int = 3,
    ):
        if min_instances < 1:
            raise ValueError("min_instances must be at least 1")
        if max_instances < min_instances:
            raise ValueError("max_instances cannot be less than min_instances")
        if cooldown_ticks < 0:
            raise ValueError("cooldown_ticks cannot be negative")

        self.min_instances: int = min_instances
        self.max_instances: int = max_instances
        self.cooldown_ticks: int = cooldown_ticks
        self.last_scaling_tick: int = -9999
        self.name: str = self.__class__.__name__

    def can_scale(self, current_tick: int) -> bool:
        """Verify whether cooldown period has expired since last scale event."""
        return (current_tick - self.last_scaling_tick) >= self.cooldown_ticks

    def clamp_instances(self, target_count: int) -> int:
        """Clamp proposed instance count within configured boundary limits."""
        return max(self.min_instances, min(self.max_instances, target_count))

    @abstractmethod
    def evaluate(
        self,
        current_tick: int,
        instances: List[VirtualInstance],
        current_cpu: float,
        current_memory: float,
        current_demand: float,
        forecast_demands: Optional[Sequence[float]] = None,
    ) -> int:
        """Evaluate telemetry and return delta instance change (+N, -N, or 0)."""
        pass


class ReactivePolicy(BaseScalingPolicy):
    """Reactive autoscaling policy reacting to instantaneous cluster utilization.

    Rules:
    - Scale UP: if CPU > 75% OR Memory > 80%, add ceil(N * 0.5) nodes.
    - Scale DOWN: if CPU < 30% AND Memory < 40%, remove 1 node.
    - Strictly obeys cooldown interval and [min_instances, max_instances].
    """

    def __init__(
        self,
        min_instances: int = 2,
        max_instances: int = 20,
        cooldown_ticks: int = 3,
        scale_up_cpu: float = 75.0,
        scale_up_memory: float = 80.0,
        scale_down_cpu: float = 30.0,
        scale_down_memory: float = 40.0,
    ):
        super().__init__(min_instances, max_instances, cooldown_ticks)
        self.scale_up_cpu = scale_up_cpu
        self.scale_up_memory = scale_up_memory
        self.scale_down_cpu = scale_down_cpu
        self.scale_down_memory = scale_down_memory

    def evaluate(
        self,
        current_tick: int,
        instances: List[VirtualInstance],
        current_cpu: float,
        current_memory: float,
        current_demand: float,
        forecast_demands: Optional[Sequence[float]] = None,
    ) -> int:
        # Total active + currently provisioning nodes
        active_alive = [i for i in instances if i.is_alive]
        current_count = len(active_alive)

        # Baseline constraint enforcement
        if current_count < self.min_instances:
            delta = self.min_instances - current_count
            self.last_scaling_tick = current_tick
            return delta

        if not self.can_scale(current_tick):
            return 0

        # Scale-up condition
        if current_cpu > self.scale_up_cpu or current_memory > self.scale_up_memory:
            scale_step = max(1, math.ceil(current_count * 0.5))
            target_count = self.clamp_instances(current_count + scale_step)
            delta = target_count - current_count
            if delta > 0:
                self.last_scaling_tick = current_tick
                return delta

        # Scale-down condition
        elif current_cpu < self.scale_down_cpu and current_memory < self.scale_down_memory:
            target_count = self.clamp_instances(current_count - 1)
            delta = target_count - current_count
            if delta < 0:
                self.last_scaling_tick = current_tick
                return delta

        return 0


class PredictivePolicy(BaseScalingPolicy):
    """Predictive autoscaling policy driven by forward horizon workload forecasts.

    Evaluates forecast demand across t+1 to t+3.
    Computes required nodes for target utilization (default 70%) and triggers
    provisioning 1 step early so instances are ACTIVE exactly when demand arrives.
    """

    def __init__(
        self,
        min_instances: int = 2,
        max_instances: int = 20,
        cooldown_ticks: int = 3,
        target_utilization: float = 0.70,
        capacity_per_instance_rps: float = 200.0,
        lookahead_steps: int = 3,
    ):
        super().__init__(min_instances, max_instances, cooldown_ticks)
        self.target_utilization = target_utilization
        self.capacity_per_instance_rps = capacity_per_instance_rps
        self.lookahead_steps = lookahead_steps

    def evaluate(
        self,
        current_tick: int,
        instances: List[VirtualInstance],
        current_cpu: float,
        current_memory: float,
        current_demand: float,
        forecast_demands: Optional[Sequence[float]] = None,
    ) -> int:
        active_alive = [i for i in instances if i.is_alive]
        current_count = len(active_alive)

        if current_count < self.min_instances:
            delta = self.min_instances - current_count
            self.last_scaling_tick = current_tick
            return delta

        if not self.can_scale(current_tick):
            return 0

        # Determine peak forward demand across lookahead window [t+1 .. t+lookahead]
        if forecast_demands and len(forecast_demands) > 0:
            window = forecast_demands[: self.lookahead_steps]
            target_demand = max(window)
        else:
            target_demand = current_demand

        # Calculate nodes needed to serve peak forecast demand at target utilization
        effective_node_capacity = self.capacity_per_instance_rps * self.target_utilization
        required_nodes = math.ceil(target_demand / effective_node_capacity)
        target_count = self.clamp_instances(required_nodes)

        # Scale up proactively if forecast demand requires more capacity
        if target_count > current_count:
            delta = target_count - current_count
            self.last_scaling_tick = current_tick
            return delta

        # Scale down gradually if forecast demand and current utilization are both comfortably low
        elif target_count < current_count:
            if current_cpu < 40.0 and current_memory < 50.0:
                step_down = max(self.min_instances, current_count - 1)
                delta = step_down - current_count
                if delta < 0:
                    self.last_scaling_tick = current_tick
                    return delta

        return 0
