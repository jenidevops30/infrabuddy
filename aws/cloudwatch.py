from datetime import datetime, timedelta, timezone

from aws.client import AWSClients


def get_ec2_cpu(
    clients: AWSClients,
    instance_id: str,
    minutes: int = 30,
):
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(minutes=minutes)

    response = clients.cloudwatch.get_metric_statistics(
        Namespace="AWS/EC2",
        MetricName="CPUUtilization",
        Dimensions=[
            {
                "Name": "InstanceId",
                "Value": instance_id,
            }
        ],
        StartTime=start_time,
        EndTime=end_time,
        Period=300,
        Statistics=["Average"],
    )

    datapoints = sorted(
        response["Datapoints"],
        key=lambda point: point["Timestamp"],
    )

    return [
        {
            "timestamp": point["Timestamp"],
            "average": round(point["Average"], 2),
        }
        for point in datapoints
    ]

def get_alb_metric(
    clients: AWSClients,
    load_balancer_arn_suffix: str,
    metric_name: str,
    minutes: int = 30,
):
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(minutes=minutes)

    response = clients.cloudwatch.get_metric_statistics(
        Namespace="AWS/ApplicationELB",
        MetricName=metric_name,
        Dimensions=[
            {
                "Name": "LoadBalancer",
                "Value": load_balancer_arn_suffix,
            }
        ],
        StartTime=start_time,
        EndTime=end_time,
        Period=300,
        Statistics=["Sum"],
    )

    datapoints = sorted(
        response["Datapoints"],
        key=lambda point: point["Timestamp"],
    )

    return [
        {
            "timestamp": point["Timestamp"],
            "value": point["Sum"],
        }
        for point in datapoints
    ]

def get_target_group_metric(
    clients: AWSClients,
    load_balancer_arn_suffix: str,
    target_group_arn: str,
    metric_name: str,
    minutes: int = 30,
):
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(minutes=minutes)

    # Extract target group ARN suffix (after "targetgroup/")
    target_group_arn_suffix = target_group_arn.split("targetgroup/")[-1]

    response = clients.cloudwatch.get_metric_statistics(
        Namespace="AWS/ApplicationELB",
        MetricName=metric_name,
        Dimensions=[
            {
                "Name": "LoadBalancer",
                "Value": load_balancer_arn_suffix,
            },
            {
                "Name": "TargetGroup",
                "Value": target_group_arn_suffix,
            },
        ],
        StartTime=start_time,
        EndTime=end_time,
        Period=300,
        Statistics=["Average"],
    )

    datapoints = sorted(
        response["Datapoints"],
        key=lambda point: point["Timestamp"],
    )

    return [
        {
            "timestamp": point["Timestamp"],
            "value": point["Average"],
        }
        for point in datapoints
    ]

def get_rds_metric(
    clients: AWSClients,
    db_instance_identifier: str,
    metric_name: str,
    minutes: int = 30,
):
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(minutes=minutes)

    response = clients.cloudwatch.get_metric_statistics(
        Namespace="AWS/RDS",
        MetricName=metric_name,
        Dimensions=[
            {
                "Name": "DBInstanceIdentifier",
                "Value": db_instance_identifier,
            }
        ],
        StartTime=start_time,
        EndTime=end_time,
        Period=300,
        Statistics=["Average"],
    )

    datapoints = sorted(
        response["Datapoints"],
        key=lambda point: point["Timestamp"],
    )

    return [
        {
            "timestamp": point["Timestamp"],
            "value": point["Average"],
        }
        for point in datapoints
    ]


def get_ebs_metric(
    clients: AWSClients,
    volume_id: str,
    metric_name: str,
    minutes: int = 30,
):
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(minutes=minutes)

    response = clients.cloudwatch.get_metric_statistics(
        Namespace="AWS/EBS",
        MetricName=metric_name,
        Dimensions=[
            {
                "Name": "VolumeId",
                "Value": volume_id,
            }
        ],
        StartTime=start_time,
        EndTime=end_time,
        Period=300,
        Statistics=["Average"],
    )

    datapoints = sorted(
        response["Datapoints"],
        key=lambda point: point["Timestamp"],
    )

    return [
        {
            "timestamp": point["Timestamp"],
            "value": point["Average"],
        }
        for point in datapoints
    ]

def bytes_to_gb(value: float) -> float:
    return round(value / (1024 ** 3), 2)

def get_ebs_metric(
    clients: AWSClients,
    volume_id: str,
    metric_name: str,
    minutes: int = 30,
):
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(minutes=minutes)

    response = clients.cloudwatch.get_metric_statistics(
        Namespace="AWS/EBS",
        MetricName=metric_name,
        Dimensions=[
            {
                "Name": "VolumeId",
                "Value": volume_id,
            }
        ],
        StartTime=start_time,
        EndTime=end_time,
        Period=300,
        Statistics=["Average"],
    )

    datapoints = sorted(
        response["Datapoints"],
        key=lambda point: point["Timestamp"],
    )

    return [
        {
            "timestamp": point["Timestamp"],
            "value": round(point["Average"], 2),
        }
        for point in datapoints
    ]


