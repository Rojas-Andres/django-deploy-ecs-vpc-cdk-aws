#!/usr/bin/env python3
from aws_cdk import App, Environment
from cluster_stack.cluster_stack import ClusterStack
from ecr_stack.ecr_stack import EcrStack
from vpc_stack.vpc_stack import VpcInfraStack

app = App()

account_id_deploy = app.node.try_get_context("account_id_deploy")
stack_name = app.node.try_get_context("STACK_NAME_DEPLOY")
env_us_west_2 = Environment(account=account_id_deploy, region="us-west-2")

cluster_stack_name = app.node.try_get_context("cluster_stack_name") or "ClusterStack"


vpc_stack = VpcInfraStack(app, f"{stack_name}VpcInfraStack", name=stack_name, env=env_us_west_2)

ecr_repository = EcrStack(app, f"{stack_name}ECR", env=env_us_west_2)
cluster_stack = ClusterStack(app, cluster_stack_name, vpc=vpc_stack.vpc, env=env_us_west_2)

app.synth()
