# -*- coding: utf-8 -*-
"""
Cloud Cost Optimization & Resource Governor Engine
Core analytics, rightsizing recommendations, idle-instance detection, and anomaly detection.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
import math
from typing import Dict, List, Optional, Tuple


@dataclass
class CloudInstance:
    instance_id: str
    name: str
    provider: str  # AWS, GCP, Azure
    region: str
    instance_type: str
    vcpu: int
    ram_gb: float
    current_monthly_cost: float
    avg_cpu_percent: float
    max_cpu_percent: float
    avg_memory_percent: float
    avg_disk_iops: float
    network_in_gb: float
    network_out_gb: float
    state: str  # RUNNING, STOPPED, IDLE
    tags: Dict[str, str] = field(default_factory=dict)
    days_idle: int = 0
    recommended_type: Optional[str] = None
    recommended_monthly_cost: Optional[float] = None
    monthly_savings: float = 0.0
    recommendation_reason: str = ""
    governance_action: str = "NONE"


@dataclass
class BillingMetric:
    date: str
    provider: str
    service: str
    cost_usd: float
    is_anomaly: bool = False
    expected_cost: float = 0.0
    anomaly_score: float = 0.0
    root_cause: str = ""


class ResourceGovernor:
    """Intelligent Cloud Resource Governor and Cost Optimization Engine."""

    # Instance catalog with approximate monthly pricing
    CATALOG = {
        "AWS": {
            "t3.micro": {"vcpu": 2, "ram": 1.0, "cost": 7.50},
            "t3.small": {"vcpu": 2, "ram": 2.0, "cost": 15.00},
            "t3.medium": {"vcpu": 2, "ram": 4.0, "cost": 30.00},
            "t3.large": {"vcpu": 2, "ram": 8.0, "cost": 60.00},
            "m5.large": {"vcpu": 2, "ram": 8.0, "cost": 70.00},
            "m5.xlarge": {"vcpu": 4, "ram": 16.0, "cost": 140.00},
            "m5.2xlarge": {"vcpu": 8, "ram": 32.0, "cost": 280.00},
            "m5.4xlarge": {"vcpu": 16, "ram": 64.0, "cost": 560.00},
            "c5.2xlarge": {"vcpu": 8, "ram": 16.0, "cost": 250.00},
            "r5.2xlarge": {"vcpu": 8, "ram": 64.0, "cost": 365.00},
            "g4dn.xlarge": {"vcpu": 4, "ram": 16.0, "cost": 384.00},
        },
        "GCP": {
            "e2-micro": {"vcpu": 2, "ram": 1.0, "cost": 6.80},
            "e2-small": {"vcpu": 2, "ram": 2.0, "cost": 13.50},
            "e2-medium": {"vcpu": 2, "ram": 4.0, "cost": 25.00},
            "e2-standard-4": {"vcpu": 4, "ram": 16.0, "cost": 100.00},
            "n2-standard-8": {"vcpu": 8, "ram": 32.0, "cost": 290.00},
            "n2-standard-16": {"vcpu": 16, "ram": 64.0, "cost": 580.00},
        },
        "Azure": {
            "Standard_B1s": {"vcpu": 1, "ram": 1.0, "cost": 7.30},
            "Standard_B2s": {"vcpu": 2, "ram": 4.0, "cost": 29.20},
            "Standard_D4s_v5": {"vcpu": 4, "ram": 16.0, "cost": 140.00},
            "Standard_D8s_v5": {"vcpu": 8, "ram": 32.0, "cost": 280.00},
            "Standard_D16s_v5": {"vcpu": 16, "ram": 64.0, "cost": 560.00},
        },
    }

    def __init__(self):
        self.instances: List[CloudInstance] = []
        self.billing_history: List[BillingMetric] = []
        self._load_seed_data()
        self.evaluate_governance_rules()

    def _load_seed_data(self):
        """Seed realistic enterprise multi-cloud infrastructure and telemetry."""
        raw_instances = [
            # AWS Fleet
            ("i-01a2b3c4d5e", "prod-api-gateway-01", "AWS", "us-east-1", "m5.2xlarge", 8, 32.0, 280.00, 48.5, 78.0, 62.0, 1850.0, 450.0, 680.0, "RUNNING", {"Env": "Production", "Owner": "CoreEng"}, 0),
            ("i-07f8e9d0c1b", "prod-api-gateway-02", "AWS", "us-east-1", "m5.2xlarge", 8, 32.0, 280.00, 42.0, 71.0, 58.0, 1720.0, 410.0, 620.0, "RUNNING", {"Env": "Production", "Owner": "CoreEng"}, 0),
            ("i-09f1a2b3c4d", "dev-batch-indexer-zombie", "AWS", "us-west-2", "m5.4xlarge", 16, 64.0, 560.00, 2.1, 4.5, 8.2, 12.0, 0.5, 0.8, "IDLE", {"Env": "Development", "Owner": "DataTeam"}, 18),
            ("i-03d4e5f6a7b", "staging-redis-cache", "AWS", "us-east-1", "r5.2xlarge", 8, 64.0, 365.00, 7.8, 14.2, 18.5, 220.0, 15.0, 22.0, "RUNNING", {"Env": "Staging", "Owner": "Infra"}, 0),
            ("i-05b6c7d8e9f", "qa-regression-runner", "AWS", "us-east-2", "c5.2xlarge", 8, 16.0, 250.00, 1.4, 3.2, 9.0, 5.0, 0.1, 0.1, "IDLE", {"Env": "QA", "Owner": "QAEngineers"}, 24),
            ("i-08a9b0c1d2e", "ml-feature-extractor-gpu", "AWS", "us-west-2", "g4dn.xlarge", 4, 16.0, 384.00, 3.8, 8.0, 12.0, 45.0, 2.0, 3.5, "IDLE", {"Env": "Research", "Owner": "MLExploration"}, 9),
            ("i-02c3d4e5f6a", "analytics-kinesis-consumer", "AWS", "us-east-1", "m5.xlarge", 4, 16.0, 140.00, 68.0, 89.0, 74.0, 3200.0, 890.0, 1200.0, "RUNNING", {"Env": "Production", "Owner": "DataPlatform"}, 0),

            # GCP Fleet
            ("gcp-vm-102938", "gcp-prod-k8s-worker-1", "GCP", "us-central1", "n2-standard-8", 8, 32.0, 290.00, 55.4, 82.0, 68.0, 2100.0, 320.0, 540.0, "RUNNING", {"Env": "Production", "Owner": "SRE"}, 0),
            ("gcp-vm-102939", "gcp-prod-k8s-worker-2", "GCP", "us-central1", "n2-standard-8", 8, 32.0, 290.00, 52.1, 79.0, 65.0, 1980.0, 310.0, 520.0, "RUNNING", {"Env": "Production", "Owner": "SRE"}, 0),
            ("gcp-vm-554433", "gcp-dev-analytics-sandbox", "GCP", "us-central1", "n2-standard-16", 16, 64.0, 580.00, 4.2, 9.8, 14.0, 40.0, 1.2, 2.0, "RUNNING", {"Env": "Dev", "Owner": "Analytics"}, 0),
            ("gcp-vm-778899", "gcp-backup-mirror-sync", "GCP", "europe-west1", "e2-standard-4", 4, 16.0, 100.00, 11.2, 19.5, 21.0, 110.0, 5.0, 12.0, "RUNNING", {"Env": "Staging", "Owner": "Infra"}, 0),
            ("gcp-vm-990011", "gcp-idle-scraping-worker", "GCP", "us-east4", "e2-standard-4", 4, 16.0, 100.00, 0.8, 2.1, 6.5, 8.0, 0.05, 0.1, "IDLE", {"Env": "Staging", "Owner": "WebScraping"}, 31),

            # Azure Fleet
            ("az-vm-881290", "az-prod-order-service-01", "Azure", "eastus", "Standard_D8s_v5", 8, 32.0, 280.00, 61.2, 85.0, 71.0, 2400.0, 620.0, 890.0, "RUNNING", {"Env": "Production", "Owner": "Ecommerce"}, 0),
            ("az-vm-881291", "az-prod-order-service-02", "Azure", "eastus", "Standard_D8s_v5", 8, 32.0, 280.00, 59.8, 83.0, 69.0, 2350.0, 600.0, 870.0, "RUNNING", {"Env": "Production", "Owner": "Ecommerce"}, 0),
            ("az-vm-443322", "az-dev-sql-replica", "Azure", "eastus2", "Standard_D16s_v5", 16, 64.0, 560.00, 6.5, 12.0, 15.0, 95.0, 3.4, 4.0, "RUNNING", {"Env": "Dev", "Owner": "DBAdmin"}, 0),
            ("az-vm-112233", "az-idle-test-load-injector", "Azure", "centralus", "Standard_D4s_v5", 4, 16.0, 140.00, 0.5, 1.2, 5.0, 2.0, 0.01, 0.02, "IDLE", {"Env": "QA", "Owner": "PerfTest"}, 14),
        ]

        for item in raw_instances:
            self.instances.append(
                CloudInstance(
                    instance_id=item[0],
                    name=item[1],
                    provider=item[2],
                    region=item[3],
                    instance_type=item[4],
                    vcpu=item[5],
                    ram_gb=item[6],
                    current_monthly_cost=item[7],
                    avg_cpu_percent=item[8],
                    max_cpu_percent=item[9],
                    avg_memory_percent=item[10],
                    avg_disk_iops=item[11],
                    network_in_gb=item[12],
                    network_out_gb=item[13],
                    state=item[14],
                    tags=item[15],
                    days_idle=item[16],
                )
            )

        # 30-day historical billing records with intentional anomaly spikes
        base_date = datetime.now() - timedelta(days=30)
        daily_baseline = {
            "AWS": {"EC2": 135.0, "RDS": 45.0, "S3": 25.0, "EKS": 35.0},
            "GCP": {"Compute": 55.0, "CloudSQL": 28.0, "GCS": 15.0, "GKE": 22.0},
            "Azure": {"VirtualMachines": 62.0, "AzureSQL": 30.0, "Blob": 18.0, "AKS": 20.0},
        }

        for day in range(30):
            cur_date = (base_date + timedelta(days=day)).strftime("%Y-%m-%d")
            # Sine wave variation + weekend drop
            day_of_week = (base_date + timedelta(days=day)).weekday()
            weekend_factor = 0.75 if day_of_week in (5, 6) else 1.0

            for provider, services in daily_baseline.items():
                for service, base_cost in services.items():
                    cost = base_cost * weekend_factor * (1.0 + 0.05 * math.sin(day * 0.4))

                    # Inject Anomalies
                    is_anomaly = False
                    anomaly_score = 0.0
                    root_cause = ""
                    expected_cost = cost

                    # Anomaly 1: Day 12 AWS S3 spike (accidental uncompressed backup export)
                    if day == 12 and provider == "AWS" and service == "S3":
                        cost = base_cost * 4.8
                        is_anomaly = True
                        anomaly_score = 4.2
                        root_cause = "Uncompressed cross-region database dump dumped to Standard Tier"

                    # Anomaly 2: Day 21 GCP Compute spike (runaway un-throttled batch job)
                    if day == 21 and provider == "GCP" and service == "Compute":
                        cost = base_cost * 3.6
                        is_anomaly = True
                        anomaly_score = 3.8
                        root_cause = "Runaway preemptible cluster failing to terminate after training run"

                    # Anomaly 3: Day 27 Azure VirtualMachines spike (accidental high-tier GPU spin-up)
                    if day == 27 and provider == "Azure" and service == "VirtualMachines":
                        cost = base_cost * 3.1
                        is_anomaly = True
                        anomaly_score = 3.3
                        root_cause = "Dev team provisioned high-memory GPU node in East US without TTL tag"

                    self.billing_history.append(
                        BillingMetric(
                            date=cur_date,
                            provider=provider,
                            service=service,
                            cost_usd=round(cost, 2),
                            is_anomaly=is_anomaly,
                            expected_cost=round(expected_cost, 2),
                            anomaly_score=anomaly_score,
                            root_cause=root_cause,
                        )
                    )

    def evaluate_governance_rules(self):
        """Analyze resource utilization and calculate rightsizing & shutdown policies."""
        for inst in self.instances:
            # Rule 1: Idle instance detection (avg CPU < 5% or marked IDLE)
            if inst.days_idle >= 7 or (inst.avg_cpu_percent < 5.0 and inst.max_cpu_percent < 10.0):
                inst.state = "IDLE"
                inst.recommended_type = "TERMINATE / STOP"
                inst.recommended_monthly_cost = 0.0
                inst.monthly_savings = inst.current_monthly_cost
                inst.recommendation_reason = (
                    f"Idle for {inst.days_idle or 7} days (Avg CPU: {inst.avg_cpu_percent}%, "
                    f"Max CPU: {inst.max_cpu_percent}%). Immediate shutdown recommended."
                )
                inst.governance_action = "TAG_AND_SHUTDOWN"
                continue

            # Rule 2: Over-provisioned Compute & Memory (Avg CPU < 18%, Max CPU < 35%, RAM < 30%)
            if inst.avg_cpu_percent < 18.0 and inst.max_cpu_percent < 35.0 and inst.avg_memory_percent < 30.0:
                # Suggest downsizing by half (e.g., 8 vCPU -> 4 vCPU, or 16 -> 8)
                target_vcpu = max(2, inst.vcpu // 2)
                target_type = None
                target_cost = inst.current_monthly_cost

                provider_catalog = self.CATALOG.get(inst.provider, {})
                for itype, specs in provider_catalog.items():
                    if specs["vcpu"] == target_vcpu and specs["cost"] < inst.current_monthly_cost:
                        target_type = itype
                        target_cost = specs["cost"]
                        break

                if target_type:
                    inst.recommended_type = target_type
                    inst.recommended_monthly_cost = target_cost
                    inst.monthly_savings = inst.current_monthly_cost - target_cost
                    inst.recommendation_reason = (
                        f"Severely over-provisioned (Avg CPU: {inst.avg_cpu_percent}%, "
                        f"RAM: {inst.avg_memory_percent}%). Rightsizing from {inst.instance_type} -> {target_type} retains 100% SLA capacity."
                    )
                    inst.governance_action = "RIGHTSIZE_DOWNGRADE"
                else:
                    inst.recommended_type = inst.instance_type
                    inst.recommended_monthly_cost = inst.current_monthly_cost
                    inst.monthly_savings = 0.0
                    inst.recommendation_reason = "Adequately sized for baseline workload."
                    inst.governance_action = "MAINTAIN"
            else:
                inst.recommended_type = inst.instance_type
                inst.recommended_monthly_cost = inst.current_monthly_cost
                inst.monthly_savings = 0.0
                inst.recommendation_reason = f"Optimal utilization (Avg CPU: {inst.avg_cpu_percent}%, RAM: {inst.avg_memory_percent}%)."
                inst.governance_action = "MAINTAIN"

    def get_summary_kpis(self) -> Dict[str, float]:
        """Compute high-level executive financial and operational KPIs."""
        total_monthly_spend = sum(i.current_monthly_cost for i in self.instances)
        total_monthly_savings = sum(i.monthly_savings for i in self.instances)
        idle_count = sum(1 for i in self.instances if i.state == "IDLE")
        overprovisioned_count = sum(1 for i in self.instances if i.governance_action == "RIGHTSIZE_DOWNGRADE")
        total_instances = len(self.instances)
        annualized_savings = total_monthly_savings * 12.0
        waste_percentage = (total_monthly_savings / total_monthly_spend * 100.0) if total_monthly_spend else 0.0

        return {
            "total_monthly_spend": round(total_monthly_spend, 2),
            "total_monthly_savings": round(total_monthly_savings, 2),
            "annualized_savings": round(annualized_savings, 2),
            "waste_percentage": round(waste_percentage, 1),
            "idle_instances": idle_count,
            "overprovisioned_instances": overprovisioned_count,
            "total_instances": total_instances,
            "optimized_monthly_spend": round(total_monthly_spend - total_monthly_savings, 2),
        }

    def detect_billing_anomalies(self) -> List[BillingMetric]:
        """Return all detected billing anomalies."""
        return [b for b in self.billing_history if b.is_anomaly]
