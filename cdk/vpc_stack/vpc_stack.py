"""
    stack to create VPC
"""
import aws_cdk as core
from aws_cdk import aws_ec2 as ec2
from constructs import Construct


class VpcInfraStack(core.Stack):
    def __init__(self, scope: Construct, id: str, name: str, **kwargs) -> None:
        """
        Create VPC
        """
        super().__init__(scope, id, **kwargs)

        self.vpc = ec2.Vpc(
            self,
            "VPC",
            vpc_name=f"{name}-vpc",
            max_azs=2,
            nat_gateways=1,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="public-subnet",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24,
                ),
                ec2.SubnetConfiguration(
                    name="private-subnet",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24,
                ),
            ],
        )
