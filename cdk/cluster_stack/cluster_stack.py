"""
Create ECS cluster
"""
import aws_cdk as core
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_elasticloadbalancingv2 as elbv2
from aws_cdk import aws_iam as iam
from aws_cdk import aws_logs as logs
from constructs import Construct


class ClusterStack(core.Stack):
    def __init__(self, scope: Construct, id: str, vpc: ec2.IVpc, **kwargs) -> None:
        """
        Create ECS cluster
        """
        super().__init__(scope, id, **kwargs)
        stack_name = self.node.try_get_context("STACK_NAME_DEPLOY")
        cluster_name = f"{stack_name}EcsCluster"
        task_family_name = f"{stack_name}TaskFamily"
        execution_role_name = f"EcsExecutionRole{cluster_name}"
        log_group_name = f"/ecs/{cluster_name}"

        ecr_repository = self.node.try_get_context("REPOSITORY_ECR") or "default_task_family"

        log_group = logs.LogGroup(
            self,
            "LogGroup",
            log_group_name=log_group_name,
            removal_policy=core.RemovalPolicy.DESTROY,
        )

        cluster = ecs.Cluster(self, "EcsCluster", vpc=vpc, cluster_name=cluster_name)
        execution_role = iam.Role(
            self,
            execution_role_name,
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
        )
        execution_role.add_managed_policy(
            iam.ManagedPolicy.from_managed_policy_arn(
                self,
                "AmazonECSTaskExecutionRolePolicy",
                "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy",
            )
        )

        execution_role.add_managed_policy(
            iam.ManagedPolicy.from_managed_policy_arn(
                self,
                "AmazonS3FullAccess",
                "arn:aws:iam::aws:policy/AmazonS3FullAccess",
            )
        )
        execution_role.add_managed_policy(
            iam.ManagedPolicy.from_managed_policy_arn(
                self,
                "EC2InstanceProfileForImageBuilderECRContainerBuilds",
                "arn:aws:iam::aws:policy/EC2InstanceProfileForImageBuilderECRContainerBuilds",
            )
        )
        task_definition = ecs.FargateTaskDefinition(
            self,
            "TaskDef",
            family=task_family_name,
            cpu=1024,
            memory_limit_mib=3072,
            execution_role=execution_role,
            runtime_platform=ecs.RuntimePlatform(
                cpu_architecture=ecs.CpuArchitecture.X86_64,
                operating_system_family=ecs.OperatingSystemFamily.LINUX,
            ),
        )

        container = task_definition.add_container(
            "api_sandbox",
            image=ecs.ContainerImage.from_registry(ecr_repository),
            cpu=0,
            logging=ecs.LogDrivers.aws_logs(stream_prefix="ecs", log_group=log_group),
            health_check=ecs.HealthCheck(
                command=["CMD-SHELL", "curl -f http://localhost:8000 || exit 1"],
                interval=core.Duration.seconds(60),
                timeout=core.Duration.seconds(30),
                retries=3,
                start_period=core.Duration.seconds(30),
            ),
        )

        container.add_port_mappings(ecs.PortMapping(container_port=8000, protocol=ecs.Protocol.TCP))

        security_group = ec2.SecurityGroup(
            self,
            "ServiceAndLBSecurityGroup",
            vpc=vpc,
            description="Allow inbound traffic on port 8000",
            allow_all_outbound=True,
        )
        security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(8000),
            "Allow inbound traffic on port 8000",
        )

        lb = elbv2.ApplicationLoadBalancer(
            self,
            "LB",
            vpc=vpc,
            internet_facing=True,
            security_group=security_group,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
        )

        listener = lb.add_listener("Listener", port=8000, protocol=elbv2.ApplicationProtocol.HTTP, open=True)

        fargate_service = ecs.FargateService(
            self,
            "FargateService",
            cluster=cluster,
            task_definition=task_definition,
            desired_count=1,
            security_groups=[security_group],
            assign_public_ip=True,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
        )

        listener.add_targets(
            "ECS",
            port=8000,
            protocol=elbv2.ApplicationProtocol.HTTP,
            targets=[fargate_service],
        )
