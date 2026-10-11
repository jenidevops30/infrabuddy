from aws.health import get_health_snapshot
from aws.metrics import (
    get_ec2_evidence,
    get_rds_evidence,
)


def build_evidence(clients):
    infrastructure = get_health_snapshot(clients)

    evidence = {
        "region": infrastructure["region"],
        "infrastructure": infrastructure,
        "metrics": {},
    }

    evidence["metrics"]["ec2"] = get_ec2_evidence(
        clients,
        infrastructure["ec2"],
    )

    evidence["metrics"]["rds"] = get_rds_evidence(
        clients,
        infrastructure["rds"],
    )

    return evidence
