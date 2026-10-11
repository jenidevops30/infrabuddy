import boto3


class AWSClients:
    def __init__(self, region: str):
        self.region = region

        self.ec2 = boto3.client(
            "ec2",
            region_name=region,
        )

        self.elbv2 = boto3.client(
            "elbv2",
            region_name=region,
        )

        self.autoscaling = boto3.client(
            "autoscaling",
            region_name=region,
        )

        self.rds = boto3.client(
            "rds",
            region_name=region,
        )

        self.cloudwatch = boto3.client(
            "cloudwatch",
            region_name=region,
        )

