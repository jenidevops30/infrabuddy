from statistics import mean
from aws.ec2 import list_instances
from aws.alb import (
    list_load_balancers,
    get_target_groups,
    get_target_health,
)
from aws.asg import list_auto_scaling_groups
from aws.ebs import list_volumes
from aws.rds import list_db_instances
from aws.cloudwatch import get_ec2_cpu
from aws.cloudwatch import get_alb_metric
from aws.cloudwatch import get_target_group_metric
from aws.cloudwatch import get_rds_metric



def summarize_metric(datapoints: list[dict]) -> dict:

    if not datapoints:
        return {
            "count": 0,
            "average": None,
            "minimum": None,
            "maximum": None,
            "latest": None,
        }

    values = [point["value"] for point in datapoints]

    return {
        "count": len(values),
        "average": round(mean(values), 2),
        "minimum": round(min(values), 2),
        "maximum": round(max(values), 2),
        "latest": values[-1],
    }
def get_ec2_evidence(clients, instances):
    evidence = []

    for instance in instances:
        item = {
            "instance_id": instance["id"],
            "state": instance["state"],
            "instance_type": instance["type"],
        }

        if instance["state"] == "running":
            cpu = get_ec2_cpu(
                clients,
                instance["id"],
                minutes=30,
            )

            item["cpu_30m"] = summarize_metric(cpu)

        evidence.append(item)

    return evidence

def get_ec2_evidence(clients, instances):
    evidence = []

    for instance in instances:
        item = {
            "instance_id": instance["id"],
            "state": instance["state"],
            "instance_type": instance["type"],
        }

        if instance["state"] == "running":
            cpu = get_ec2_cpu(
                clients,
                instance["id"],
                minutes=30,
            )

            item["cpu_30m"] = summarize_metric(cpu)

        evidence.append(item)

    return evidence


def get_rds_evidence(clients, databases):
    evidence = []

    for db in databases:
        identifier = db["identifier"]

        cpu = get_rds_metric(
            clients,
            identifier,
            "CPUUtilization",
        )

        connections = get_rds_metric(
            clients,
            identifier,
            "DatabaseConnections",
        )

        storage = get_rds_metric(
            clients,
            identifier,
            "FreeStorageSpace",
        )

        evidence.append(
            {
                "identifier": identifier,
                "status": db["status"],
                "engine": db["engine"],
                "instance_class": db["instance_class"],
                "multi_az": db["multi_az"],
                "cpu_30m": summarize_metric(cpu),
                "connections_30m": summarize_metric(connections),
                "free_storage_bytes_30m": summarize_metric(
                    storage
                ),
            }
        )

    return evidence