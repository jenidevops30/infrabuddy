from aws.client import AWSClients
from aws.ec2 import list_instances
from aws.alb import list_load_balancers, get_target_groups, get_target_health
from aws.asg import list_auto_scaling_groups
from aws.ebs import list_volumes
from aws.rds import list_db_instances


def get_health_snapshot(clients: AWSClients):
    snapshot = {
        "region": clients.region,
        "ec2": [],
        "alb": [],
        "asg": [],
        "ebs": [],
        "rds": [],
    }

    # EC2
    snapshot["ec2"] = list_instances(clients)

    # ALB
    for lb in list_load_balancers(clients):
        lb_data = {
            "name": lb["name"],
            "state": lb["state"],
            "type": lb["type"],
            "target_groups": [],
        }

        target_groups = get_target_groups(
            clients,
            lb["arn"],
        )

        for tg in target_groups:
            targets = get_target_health(
                clients,
                tg["TargetGroupArn"],
            )

            lb_data["target_groups"].append(
                {
                    "name": tg["TargetGroupName"],
                    "targets": targets,
                }
            )

        snapshot["alb"].append(lb_data)

    # ASG
    snapshot["asg"] = list_auto_scaling_groups(clients)

    # EBS
    snapshot["ebs"] = list_volumes(clients)

    # RDS
    snapshot["rds"] = list_db_instances(clients)

    return snapshot
