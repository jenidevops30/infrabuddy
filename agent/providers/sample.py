"""
Sample Data Model Provider

Provides deterministic mock responses for development and testing without requiring
external API credentials or network access.
"""

import json
import logging
from typing import Optional, Any

from agent.providers.base import ModelProvider, ModelResponse, ProviderType

logger = logging.getLogger(__name__)


class SampleProvider(ModelProvider):
    """Sample data provider that returns deterministic mock responses."""
    
    def __init__(self, model: str = "sample-model", **kwargs):
        super().__init__(model, **kwargs)
        self._call_count = 0
    
    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.SAMPLE
    
    async def analyze(self, prompt: str, system_prompt: Optional[str] = None) -> ModelResponse:
        """
        Return a structured mock diagnosis based on the prompt content.
        
        This provides realistic sample output for development and testing.
        """
        self._call_count += 1
        
        # Detect what type of analysis is being requested
        prompt_lower = prompt.lower()
        
        if "ec2" in prompt_lower and "cpu" in prompt_lower:
            content = self._generate_ec2_cpu_diagnosis(prompt)
        elif "alb" in prompt_lower or "load balancer" in prompt_lower:
            content = self._generate_alb_diagnosis(prompt)
        elif "rds" in prompt_lower or "database" in prompt_lower:
            content = self._generate_rds_diagnosis(prompt)
        else:
            content = self._generate_generic_diagnosis(prompt)
        
        logger.debug(f"Sample provider generated response (call #{self._call_count})")
        
        return ModelResponse(
            content=content,
            model=self.model,
            provider=ProviderType.SAMPLE,
            usage={"prompt_tokens": len(prompt) // 4, "completion_tokens": len(content) // 4, "total_tokens": (len(prompt) + len(content)) // 4},
            metadata={"call_count": self._call_count, "sample_mode": True},
        )
    
    def _generate_ec2_cpu_diagnosis(self, prompt: str) -> str:
        """Generate a sample EC2 CPU diagnosis."""
        return json.dumps({
            "diagnosis_id": "diag-sample-ec2-cpu-001",
            "timestamp": "2026-10-10T12:00:00Z",
            "instance_id": "i-0123456789abcdef0",
            "problem_summary": "CPU sustained >90% for 25 minutes",
            "evidence": [
                {"metric": "CPUUtilization", "value": 94.2, "timestamp": "2026-10-10T11:45:00Z", "unit": "Percent"},
                {"metric": "CPUUtilization", "value": 91.8, "timestamp": "2026-10-10T11:40:00Z", "unit": "Percent"},
                {"metric": "CPUUtilization", "value": 89.5, "timestamp": "2026-10-10T11:35:00Z", "unit": "Percent"},
                {"metric": "StatusCheck", "value": "passed", "timestamp": "2026-10-10T11:45:00Z", "unit": "Count"},
            ],
            "hypotheses": [
                {"cause": "Application load spike", "confidence": 0.7, "evidence_refs": [0, 1, 2], "reasoning": "Sustained high CPU correlates with typical application load patterns"},
                {"cause": "Runaway process", "confidence": 0.2, "evidence_refs": [], "reasoning": "No evidence of single process dominance without OS-level visibility"},
                {"cause": "Noisy neighbor (shared tenancy)", "confidence": 0.1, "evidence_refs": [], "reasoning": "Possible but less likely on dedicated instance types"},
            ],
            "confidence": 0.7,
            "uncertainty": "Cannot inspect OS-level processes without SSM/agent access. Application logs needed to confirm load spike vs. runaway process.",
            "recommended_steps": [
                "Check application logs for traffic spike or error patterns",
                "Review recent deployments or configuration changes",
                "Enable detailed monitoring for 1-minute granularity",
                "Consider enabling SSM for process-level visibility",
            ],
            "safe_remediation": [
                {"action": "Scale out ASG desired capacity", "risk": "low", "requires_approval": True, "description": "Add instances to distribute load"},
                {"action": "Restart application service via deployment", "risk": "medium", "requires_approval": True, "description": "Rolling restart to clear potential stuck processes"},
            ],
            "runbook_references": [
                {"title": "High CPU Troubleshooting Runbook", "url": "runbooks/ec2-high-cpu.md", "section": "CPU Utilization > 80%"},
                {"title": "Application Performance Investigation", "url": "runbooks/app-perf.md", "section": "Load Spike Analysis"},
            ],
            "audit_event_id": "audit-sample-001",
        }, indent=2)
    
    def _generate_alb_diagnosis(self, prompt: str) -> str:
        """Generate a sample ALB diagnosis."""
        return json.dumps({
            "diagnosis_id": "diag-sample-alb-001",
            "timestamp": "2026-10-10T12:00:00Z",
            "load_balancer_arn": "arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/sample-alb/abc123",
            "problem_summary": "Target group unhealthy - 3 of 4 targets failing health checks",
            "evidence": [
                {"metric": "HealthyHostCount", "value": 1, "timestamp": "2026-10-10T11:45:00Z", "unit": "Count"},
                {"metric": "UnHealthyHostCount", "value": 3, "timestamp": "2026-10-10T11:45:00Z", "unit": "Count"},
                {"metric": "TargetResponseTime", "value": 5.2, "timestamp": "2026-10-10T11:45:00Z", "unit": "Seconds"},
                {"metric": "HTTPCode_Target_5XX_Count", "value": 142, "timestamp": "2026-10-10T11:45:00Z", "unit": "Count"},
            ],
            "hypotheses": [
                {"cause": "Application deployment failure", "confidence": 0.6, "evidence_refs": [3], "reasoning": "5XX errors suggest application-level failures"},
                {"cause": "Health check path misconfiguration", "confidence": 0.25, "evidence_refs": [0, 1], "reasoning": "All targets unhealthy simultaneously suggests config issue"},
                {"cause": "Target instance resource exhaustion", "confidence": 0.15, "evidence_refs": [2], "reasoning": "High response times could indicate resource pressure"},
            ],
            "confidence": 0.6,
            "uncertainty": "Need application logs and deployment history to distinguish between deployment failure and config issue.",
            "recommended_steps": [
                "Check recent deployment status in CI/CD pipeline",
                "Verify health check path and expected response codes",
                "Review application logs on healthy target for error patterns",
                "Check target group health check configuration",
            ],
            "safe_remediation": [
                {"action": "Rollback recent deployment", "risk": "low", "requires_approval": True, "description": "Revert to previous known-good version"},
                {"action": "Update health check configuration", "risk": "low", "requires_approval": True, "description": "Fix path/port/codes if misconfigured"},
            ],
            "runbook_references": [
                {"title": "ALB Target Health Troubleshooting", "url": "runbooks/alb-target-health.md"},
            ],
            "audit_event_id": "audit-sample-002",
        }, indent=2)
    
    def _generate_rds_diagnosis(self, prompt: str) -> str:
        """Generate a sample RDS diagnosis."""
        return json.dumps({
            "diagnosis_id": "diag-sample-rds-001",
            "timestamp": "2026-10-10T12:00:00Z",
            "db_instance_identifier": "sample-db-instance",
            "problem_summary": "High CPU utilization and elevated connection count",
            "evidence": [
                {"metric": "CPUUtilization", "value": 87.3, "timestamp": "2026-10-10T11:45:00Z", "unit": "Percent"},
                {"metric": "DatabaseConnections", "value": 950, "timestamp": "2026-10-10T11:45:00Z", "unit": "Count"},
                {"metric": "FreeableMemory", "value": 1024, "timestamp": "2026-10-10T11:45:00Z", "unit": "MB"},
                {"metric": "ReadLatency", "value": 0.045, "timestamp": "2026-10-10T11:45:00Z", "unit": "Seconds"},
            ],
            "hypotheses": [
                {"cause": "Connection pool exhaustion", "confidence": 0.65, "evidence_refs": [1], "reasoning": "High connection count near max_connections limit"},
                {"cause": "Inefficient queries causing CPU pressure", "confidence": 0.25, "evidence_refs": [0, 3], "reasoning": "High CPU with elevated read latency suggests query issues"},
                {"cause": "Insufficient instance class for workload", "confidence": 0.1, "evidence_refs": [0, 2], "reasoning": "Low freeable memory with high CPU indicates resource constraints"},
            ],
            "confidence": 0.65,
            "uncertainty": "Need query-level analysis (Performance Insights) to confirm inefficient queries vs. connection pooling issue.",
            "recommended_steps": [
                "Enable Performance Insights for query-level analysis",
                "Review application connection pool configuration",
                "Check for long-running queries in pg_stat_activity / SHOW PROCESSLIST",
                "Consider upgrading instance class if sustained high load",
            ],
            "safe_remediation": [
                {"action": "Increase max_connections parameter", "risk": "medium", "requires_approval": True, "description": "Requires parameter group change and reboot"},
                {"action": "Scale up instance class", "risk": "low", "requires_approval": True, "description": "Modify instance class during maintenance window"},
            ],
            "runbook_references": [
                {"title": "RDS High CPU Troubleshooting", "url": "runbooks/rds-high-cpu.md"},
                {"title": "Connection Pool Optimization", "url": "runbooks/rds-connections.md"},
            ],
            "audit_event_id": "audit-sample-003",
        }, indent=2)
    
    def _generate_generic_diagnosis(self, prompt: str) -> str:
        """Generate a generic sample diagnosis."""
        return json.dumps({
            "diagnosis_id": "diag-sample-generic-001",
            "timestamp": "2026-10-10T12:00:00Z",
            "problem_summary": "Sample diagnosis - no specific issue detected in evidence",
            "evidence": [
                {"metric": "SampleMetric", "value": 42.0, "timestamp": "2026-10-10T11:45:00Z", "unit": "Count"},
            ],
            "hypotheses": [
                {"cause": "Sample hypothesis for demonstration", "confidence": 0.5, "evidence_refs": [0], "reasoning": "This is sample data for development"},
            ],
            "confidence": 0.5,
            "uncertainty": "This is sample mode - no real AWS data was analyzed.",
            "recommended_steps": [
                "Configure AWS credentials for real analysis",
                "Configure NVIDIA API key for real LLM analysis",
            ],
            "safe_remediation": [],
            "runbook_references": [],
            "audit_event_id": "audit-sample-000",
        }, indent=2)
    
    async def health_check(self) -> bool:
        """Sample provider is always healthy."""
        return True
    
    def get_config_summary(self) -> dict[str, Any]:
        """Return sanitized config for logging."""
        base = super().get_config_summary()
        base.update({
            "call_count": self._call_count,
        })
        return base