from aws.client import AWSClients


def list_volumes(clients: AWSClients):
    response = clients.ec2.describe_volumes()

    volumes = []

    for volume in response["Volumes"]:
        attachments = []

        for attachment in volume.get("Attachments", []):
            attachments.append(
                {
                    "instance_id": attachment.get("InstanceId"),
                    "device": attachment.get("Device"),
                    "state": attachment.get("State"),
                }
            )

        volumes.append(
            {
                "id": volume["VolumeId"],
                "size_gb": volume["Size"],
                "volume_type": volume["VolumeType"],
                "state": volume["State"],
                "iops": volume.get("Iops"),
                "throughput": volume.get("Throughput"),
                "attachments": attachments,
            }
        )

    return volumes
