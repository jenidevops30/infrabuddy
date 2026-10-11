from aws.client import AWSClients


def list_load_balancers(clients: AWSClients):
    response = clients.elbv2.describe_load_balancers()

    load_balancers = []

    for lb in response["LoadBalancers"]:
        load_balancers.append(
            {
                "name": lb["LoadBalancerName"],
                "arn": lb["LoadBalancerArn"],
                "arn_suffix": lb["LoadBalancerArn"].split(
                    "loadbalancer/"
                )[1],
                "dns_name": lb["DNSName"],
                "state": lb["State"]["Code"],
                "type": lb["Type"],
            }
        )

    return load_balancers



def get_target_groups(clients: AWSClients, load_balancer_arn: str):
    response = clients.elbv2.describe_target_groups(
        LoadBalancerArn=load_balancer_arn
    )

    return response["TargetGroups"]


def get_target_health(
    clients: AWSClients,
    target_group_arn: str,
):
    response = clients.elbv2.describe_target_health(
        TargetGroupArn=target_group_arn
    )

    targets = []

    for target in response["TargetHealthDescriptions"]:
        targets.append(
            {
                "target_id": target["Target"]["Id"],
                "port": target["Target"].get("Port"),
                "state": target["TargetHealth"]["State"],
                "reason": target["TargetHealth"].get("Reason"),
                "description": target["TargetHealth"].get(
                    "Description"
                ),
            }
        )

    return targets
