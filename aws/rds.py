from aws.client import AWSClients


def list_db_instances(clients: AWSClients):
    response = clients.rds.describe_db_instances()

    databases = []

    for db in response["DBInstances"]:
        databases.append(
            {
                "identifier": db["DBInstanceIdentifier"],
                "engine": db["Engine"],
                "engine_version": db["EngineVersion"],
                "status": db["DBInstanceStatus"],
                "instance_class": db["DBInstanceClass"],
                "availability_zone": db.get("AvailabilityZone"),
                "multi_az": db.get("MultiAZ"),
                "storage_type": db.get("StorageType"),
                "allocated_storage_gb": db.get("AllocatedStorage"),
                "storage_encrypted": db.get("StorageEncrypted"),
                "endpoint": (
                    db.get("Endpoint", {}).get("Address")
                ),
                "port": (
                    db.get("Endpoint", {}).get("Port")
                ),
            }
        )

    return databases
