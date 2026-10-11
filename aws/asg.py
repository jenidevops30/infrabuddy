from aws.client import AWSClients


def list_auto_scaling_groups(clients: AWSClients):
    response = clients.autoscaling.describe_auto_scaling_groups()

    groups = []

    for group in response["AutoScalingGroups"]:
        groups.append(
            {
                "name": group["AutoScalingGroupName"],
                "min_size": group["MinSize"],
                "max_size": group["MaxSize"],
                "desired_capacity": group["DesiredCapacity"],
                "instances": [
                    {
                        "id": instance["InstanceId"],
                        "state": instance["LifecycleState"],
                        "health": instance["HealthStatus"],
                    }
                    for instance in group["Instances"]
                ],
            }
        )

    return groups
