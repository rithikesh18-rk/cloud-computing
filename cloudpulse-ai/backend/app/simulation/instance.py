"""Virtual Cloud Instance Abstraction for Discrete Simulation.

Represents a cloud compute instance (e.g., container/VM worker) with:
- Capacity in requests per second (RPS)
- Finite spin-up provisioning delay
- Resource utilization telemetry
- Lifecycle state transitions (PROVISIONING -> ACTIVE -> TERMINATING)
"""

from enum import Enum
from typing import Dict, Any
import uuid


class InstanceStatus(str, Enum):
    """Lifecycle state of a virtual compute node."""
    PROVISIONING = "PROVISIONING"
    ACTIVE = "ACTIVE"
    TERMINATING = "TERMINATING"


class VirtualInstance:
    """Discrete virtual compute worker node.

    Simulates cloud worker node behavior with finite spin-up delay and capacity limits.
    """

    def __init__(
        self,
        instance_id: str | None = None,
        capacity_rps: float = 200.0,
        status: InstanceStatus = InstanceStatus.PROVISIONING,
        provision_delay_ticks: int = 1,
        allocated_cpu: float = 0.0,
        allocated_memory: float = 0.0,
    ):
        self.id: str = instance_id or f"inst-{uuid.uuid4().hex[:8]}"
        self.capacity_rps: float = float(capacity_rps)
        self.status: InstanceStatus = status
        self.provision_delay_ticks: int = provision_delay_ticks
        self.provision_counter: int = 0 if status == InstanceStatus.PROVISIONING else provision_delay_ticks
        self.allocated_cpu: float = float(allocated_cpu)
        self.allocated_memory: float = float(allocated_memory)
        self.uptime_ticks: int = 0

    @property
    def is_active(self) -> bool:
        """Whether instance is operational and accepting live traffic."""
        return self.status == InstanceStatus.ACTIVE

    @property
    def is_alive(self) -> bool:
        """Whether instance is either actively serving or currently provisioning."""
        return self.status in (InstanceStatus.ACTIVE, InstanceStatus.PROVISIONING)

    def tick(self) -> None:
        """Advance discrete simulation tick for this instance."""
        self.uptime_ticks += 1

        if self.status == InstanceStatus.PROVISIONING:
            self.provision_counter += 1
            if self.provision_counter >= self.provision_delay_ticks:
                self.status = InstanceStatus.ACTIVE

    def terminate(self) -> None:
        """Mark instance for decommissioning."""
        self.status = InstanceStatus.TERMINATING

    def update_telemetry(self, cpu: float, memory: float) -> None:
        """Update instance utilization figures."""
        self.allocated_cpu = float(cpu)
        self.allocated_memory = float(memory)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize instance state."""
        return {
            "id": self.id,
            "status": self.status.value,
            "capacity_rps": self.capacity_rps,
            "allocated_cpu": self.allocated_cpu,
            "allocated_memory": self.allocated_memory,
            "uptime_ticks": self.uptime_ticks,
            "is_active": self.is_active,
        }

    def __repr__(self) -> str:
        return (
            f"<VirtualInstance id={self.id} status={self.status.value} "
            f"capacity={self.capacity_rps}rps uptime={self.uptime_ticks}>"
        )
