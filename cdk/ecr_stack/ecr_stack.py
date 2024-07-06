"""
This is the main stack file where we define the ECR stack.
"""
import aws_cdk as core
from aws_cdk import aws_ecr as ecr
from constructs import Construct


class EcrStack(core.Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        """
        Create ECR repository
        """
        super().__init__(scope, id, **kwargs)
        repository_name = self.node.try_get_context("repository_name")
        self.repository = ecr.Repository(
            self,
            "EcrStack",
            repository_name=repository_name,
            removal_policy=core.RemovalPolicy.DESTROY,
            lifecycle_rules=[ecr.LifecycleRule(tag_prefix_list=["prod"], max_image_count=10)],
        )
