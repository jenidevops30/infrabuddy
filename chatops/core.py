"""
chatops/core.py

Shared analysis runner used by both the Slack and Teams adapters.
Wraps the existing evidence → prompt → LLM pipeline with async support
and structured output suitable for chat formatting.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

from agent.config import get_settings
from agent.evidence import build_evidence
from agent.llm import LLM
from agent.prompts import build_health_prompt
from aws.client import AWSClients

logger = logging.getLogger(__name__)

# Services we can target individually
SUPPORTED_SERVICES = {"ec2", "alb", "asg", "rds", "cloudwatch", "all"}


@dataclass
class AnalysisResult:
    """Structured result returned by run_analysis."""

    success: bool
    region: str
    service_filter: str
    analysis: str
    provider: str = "unknown"
    model: str = "unknown"
    error: Optional[str] = None
    warnings: list[str] = field(default_factory=list)


async def run_analysis(service: str = "all") -> AnalysisResult:
    """
    Collect AWS evidence and run LLM analysis.

    Args:
        service: Which AWS service to focus on.
                 One of: ec2 | alb | asg | rds | cloudwatch | all

    Returns:
        AnalysisResult with analysis text and metadata.
    """
    service = service.lower().strip()
    if service not in SUPPORTED_SERVICES:
        service = "all"

    settings = get_settings()
    region = settings.aws_region
    llm = LLM()

    logger.info("ChatOps analysis requested: service=%s region=%s", service, region)

    try:
        aws = AWSClients(region)
        evidence = build_evidence(aws)
    except Exception as exc:
        logger.warning("AWS evidence collection failed: %s", exc)
        if settings.enable_sample_mode:
            evidence = {"sample_mode": True, "region": region, "error": str(exc)}
            result_warnings = [f"Could not reach AWS ({exc}). Showing sample analysis."]
        else:
            return AnalysisResult(
                success=False,
                region=region,
                service_filter=service,
                analysis="",
                error=f"AWS evidence collection failed: {exc}",
            )
    else:
        result_warnings = []

    # Optionally narrow the evidence to a single service
    if service != "all":
        evidence = _filter_evidence(evidence, service)

    prompt = build_health_prompt(evidence)

    try:
        response = await llm.analyze_async(prompt)
        analysis_text = response.content
        provider_info = llm.provider_info
    except Exception as exc:
        logger.error("LLM analysis failed: %s", exc)
        return AnalysisResult(
            success=False,
            region=region,
            service_filter=service,
            analysis="",
            error=f"LLM analysis failed: {exc}",
        )
    finally:
        await llm.close()

    return AnalysisResult(
        success=True,
        region=region,
        service_filter=service,
        analysis=analysis_text,
        provider=provider_info.get("provider", "unknown"),
        model=provider_info.get("model", "unknown"),
        warnings=result_warnings,
    )


async def run_status() -> dict:
    """
    Return raw infrastructure state without calling the LLM.
    Fast — suitable for a quick /infrabuddy status command.
    """
    settings = get_settings()
    region = settings.aws_region

    try:
        from aws.health import get_health_snapshot

        aws = AWSClients(region)
        snapshot = get_health_snapshot(aws)
        return {"success": True, "region": region, "snapshot": snapshot}
    except Exception as exc:
        logger.warning("Status check failed: %s", exc)
        return {"success": False, "region": region, "error": str(exc)}


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _filter_evidence(evidence: dict, service: str) -> dict:
    """
    Narrow the full evidence dict to a single service so the prompt
    stays focused and tokens are not wasted.
    """
    infra = evidence.get("infrastructure", {})
    metrics = evidence.get("metrics", {})

    service_map = {
        "ec2": {"ec2": infra.get("ec2", [])},
        "alb": {"alb": infra.get("alb", [])},
        "asg": {"asg": infra.get("asg", [])},
        "rds": {"rds": infra.get("rds", [])},
        "cloudwatch": {},  # CloudWatch data lives inside metrics
    }

    filtered_infra = service_map.get(service, infra)
    filtered_metrics = {service: metrics.get(service, {})} if service in metrics else {}

    return {
        "region": evidence.get("region"),
        "service_filter": service,
        "infrastructure": filtered_infra,
        "metrics": filtered_metrics,
    }
