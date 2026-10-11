from aws.client import AWSClients


def list_instances(clients: AWSClients):
    response = clients.ec2.describe_instances()

    instances = []

    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            instances.append(
                {
                    "id": instance["InstanceId"],
                    "type": instance["InstanceType"],
                    "state": instance["State"]["Name"],
                    "private_ip": instance.get("PrivateIpAddress"),
                    "availability_zone": (
                        instance.get("Placement", {})
                        .get("AvailabilityZone")
                    ),
                }
            )

    return instances
