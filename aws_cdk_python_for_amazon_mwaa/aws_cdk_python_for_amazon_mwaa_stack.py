from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_iam as iam,
    aws_ec2 as ec2,
    aws_mwaa as mwaa
)
from constructs import Construct


class AwsCdkPythonForAmazonMwaaStack(Stack):

    def __init__(
            self, 
            scope: Construct, 
            construct_id: str, 
            source_bucket: s3.Bucket,
            **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        source_bucket_arn = source_bucket.bucket_arn

        mwaa_policy_document = iam.PolicyDocument(
            statements=[
                iam.PolicyStatement(
                    actions=["airflow:PublishMetrics"],
                    effect=iam.Effect.ALLOW,
                    # TODO: narrow the scope of the MWAA Environment
                    resources=[f"arn:aws:airflow:{self.region}:{self.account}:environment/*"],
                ),
                # TODO: revisit this
                iam.PolicyStatement(
                    actions=[
                        "s3:ListAllMyBuckets"
                    ],
                    effect=iam.Effect.DENY,
                    resources=[
                        f"{source_bucket_arn}/*",
                        f"{source_bucket_arn}"
                        ],
                ),
                iam.PolicyStatement(
                    actions=[
                        "s3:*"
                    ],
                    effect=iam.Effect.ALLOW,
                    resources=[
                        f"{source_bucket_arn}/*",
                        f"{source_bucket_arn}"
                        ],
                ),
                iam.PolicyStatement(
                    actions=[
                        "logs:CreateLogStream",
                        "logs:CreateLogGroup",
                        "logs:PutLogEvents",
                        "logs:GetLogEvents",
                        "logs:GetLogRecord",
                        "logs:GetLogGroupFields",
                        "logs:GetQueryResults",
                        "logs:DescribeLogGroups"
                    ],
                    effect=iam.Effect.ALLOW,
                    # TODO: try to narrow this scope down
                    resources=[f"arn:aws:logs:{self.region}:{self.account}:log-group:*"],
                ),
                iam.PolicyStatement(
                    actions=[
                        "logs:DescribeLogGroups"
                    ],
                    effect=iam.Effect.ALLOW,
                    resources=["*"],
                ),
                # TODO: revisit this
                iam.PolicyStatement(
                    actions=[
                        "sqs:ChangeMessageVisibility",
                        "sqs:DeleteMessage",
                        "sqs:GetQueueAttributes",
                        "sqs:GetQueueUrl",
                        "sqs:ReceiveMessage",
                        "sqs:SendMessage"
                    ],
                    effect=iam.Effect.ALLOW,
                    resources=[f"arn:aws:sqs:{self.region}:*:airflow-celery-*"],
                ),
                iam.PolicyStatement(
                    actions=[
                        "ecs:RunTask",
                        "ecs:DescribeTasks",
                        "ecs:RegisterTaskDefinition",
                        "ecs:DescribeTaskDefinition",
                        "ecs:ListTasks"
                    ],
                    effect=iam.Effect.ALLOW,
                    resources=[
                        "*"
                        ],
                    ),
                iam.PolicyStatement(
                    actions=[
                        "iam:PassRole"
                    ],
                    effect=iam.Effect.ALLOW,
                    resources=[ "*" ],
                    conditions= { 
                        "StringLike": { 
                            "iam:PassedToService": "ecs-tasks.amazonaws.com" 
                            } 
                        },
                    ),
                # KMS stuff might not be needed also
                iam.PolicyStatement(
                    actions=[
                        "kms:Decrypt",
                        "kms:DescribeKey",
                        "kms:GenerateDataKey*",
                        "kms:Encrypt",
                        "kms:PutKeyPolicy"
                    ],
                    effect=iam.Effect.ALLOW,
                    resources=["*"],
                    conditions={
                        "StringEquals": {
                            "kms:ViaService": [
                                # SQS may not be needed
                                f"sqs.{self.region}.amazonaws.com",
                                f"s3.{self.region}.amazonaws.com",
                            ]
                        }
                    },
                ),
            ]
        )

        mwaa_service_role = iam.Role(
            self,
            "mwaa_svc_role",
            assumed_by=iam.CompositePrincipal(
                iam.ServicePrincipal("airflow.amazonaws.com"),
                iam.ServicePrincipal("airflow-env.amazonaws.com"),
                iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            ),
            inline_policies={
                "mwaaPolicyDoc": mwaa_policy_document
            },
            path="/service-role/"
        )
        mwaa_service_role.add_to_policy(
            iam.PolicyStatement(
                resources=["*"],
                actions=["cloudwatch:PutMetricData"],
                effect=iam.Effect.ALLOW,
            )
        )
        mwaa_service_role.add_to_policy(
            iam.PolicyStatement(
                resources=["*"],
                actions=["sts:AssumeRole"],
                effect=iam.Effect.ALLOW,
            )
        )
        mwaa_service_role.add_to_policy(
            iam.PolicyStatement(
                resources=[
                    "arn:aws:secretsmanager:*:*:airflow/connections/*",
                    "arn:aws:secretsmanager:*:*:airflow/variables/*",
                ],
                actions=[
                    "secretsmanager:DescribeSecret",
                    "secretsmanager:PutSecretValue",
                    "secretsmanager:CreateSecret",
                    "secretsmanager:DeleteSecret",
                    "secretsmanager:CancelRotateSecret",
                    "secretsmanager:ListSecretVersionIds",
                    "secretsmanager:UpdateSecret",
                    "secretsmanager:GetRandomPassword",
                    "secretsmanager:GetResourcePolicy",
                    "secretsmanager:GetSecretValue",
                    "secretsmanager:StopReplicationToReplica",
                    "secretsmanager:ReplicateSecretToRegions",
                    "secretsmanager:RestoreSecret",
                    "secretsmanager:RotateSecret",
                    "secretsmanager:UpdateSecretVersionStage",
                    "secretsmanager:RemoveRegionsFromReplication",
                    "secretsmanager:ListSecrets",
                ],
                effect=iam.Effect.ALLOW,
            )
            )

        self.env_name = "mwaa_env"
        # Create MWAA user policy
        managed_policy = iam.ManagedPolicy(
            self,
            "mwaa-user-policy",
            managed_policy_name="mwaa-user-policy",
            statements=[
                iam.PolicyStatement(
                    resources=[
                        f"arn:aws:airflow:{self.region}:{self.account}:role/{self.env_name}/Op"
                    ],
                    actions=["airflow:CreateWebLoginToken"],
                    effect=iam.Effect.ALLOW,
                ),
                iam.PolicyStatement(
                    resources=[
                        f"arn:aws:airflow:{self.region}:{self.account}:environment/{self.env_name}"
                    ],
                    actions=["airflow:GetEnvironment"],
                    effect=iam.Effect.ALLOW,
                ),
                iam.PolicyStatement(
                    resources=["*"],
                    actions=["airflow:ListEnvironments"],
                    effect=iam.Effect.ALLOW,
                ),
                iam.PolicyStatement(
                    resources=[
                        f"arn:aws:s3:::{source_bucket.bucket_name}/dags/*",
                    ],
                    actions=["s3:PutObject"],
                    effect=iam.Effect.ALLOW,
                )
            ],
        )
        
        self.vpc = ec2.Vpc(
            self,
            "infra_network",
            ip_addresses=ec2.IpAddresses.cidr("10.80.0.0/20"),
            max_azs=2,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="public",
                    subnet_type=ec2.SubnetType.PUBLIC
                ),
                ec2.SubnetConfiguration(
                    name="private",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
                ),
            ],
            enable_dns_hostnames=True,
            enable_dns_support=True
        )

        mwaa_sec_group = ec2.SecurityGroup(
            self,
            "mwaa-sec-group",
            vpc=self.vpc,
            security_group_name="mwaa-sec-group"
        )
        mwaa_sec_group.connections.allow_internally(ec2.Port.all_traffic(), "MWAA")

        private_subnet_ids = [subnet.subnet_id for subnet in self.vpc.private_subnets]
        private_subnets = [subnet for subnet in self.vpc.private_subnets]

        full_access_policy = iam.PolicyStatement(
            resources=["*"],
            actions=["*"],
            effect=iam.Effect.ALLOW,
            principals=[iam.AnyPrincipal()],
        )
        s3_vpc_endpoint = self.vpc.add_gateway_endpoint(
            "s3_vpc_endpoint",
            service=ec2.GatewayVpcEndpointAwsService.S3,
            subnets=[ec2.SubnetSelection(subnets=private_subnets)],
        )
        s3_vpc_endpoint.add_to_policy(full_access_policy)

        ecr_dkr_vpc_endpoint = self.vpc.add_interface_endpoint(
            "ecr_vpc_endpoint",
            subnets=ec2.SubnetSelection(subnets=private_subnets),
            private_dns_enabled=True,
            service=ec2.InterfaceVpcEndpointAwsService.ECR_DOCKER
        )
        ecr_dkr_vpc_endpoint.add_to_policy(full_access_policy)

        ecr_api_vpc_endpoint = self.vpc.add_interface_endpoint(
            "ecr_api_vpc_endpoint",
            subnets=ec2.SubnetSelection(subnets=private_subnets),
            private_dns_enabled=True,
            service=ec2.InterfaceVpcEndpointAwsService.ECR
        )
        ecr_api_vpc_endpoint.add_to_policy(full_access_policy)

        logs_vpc_endpoint = self.vpc.add_interface_endpoint(
            "logs_vpc_endpoint",
            subnets=ec2.SubnetSelection(subnets=private_subnets),
            private_dns_enabled=True,
            service=ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH_LOGS
        )
        logs_vpc_endpoint.add_to_policy(full_access_policy)

        monitoring_vpc_endpoint = self.vpc.add_interface_endpoint(
            "monitoring_vpc_endpoint",
            subnets=ec2.SubnetSelection(subnets=private_subnets),
            private_dns_enabled=True,
            service=ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH_MONITORING
        )
        monitoring_vpc_endpoint.add_to_policy(full_access_policy)
        
        sqs_vpc_endpoint = self.vpc.add_interface_endpoint(
            "sqs_vpc_endpoint",
            subnets=ec2.SubnetSelection(subnets=private_subnets),
            private_dns_enabled=True,
            service=ec2.InterfaceVpcEndpointAwsService.SQS
        )
        sqs_vpc_endpoint.add_to_policy(full_access_policy)

        kms_vpc_endpoint = self.vpc.add_interface_endpoint(
            "kms_vpc_endpoint",
            subnets=ec2.SubnetSelection(subnets=private_subnets),
            private_dns_enabled=True,
            service=ec2.InterfaceVpcEndpointAwsService.KMS
        )
        kms_vpc_endpoint.add_to_policy(full_access_policy)

        # MWAA environment creation
        mwaa_env = mwaa.CfnEnvironment(
            self,
            self.env_name,
            name=self.env_name,
            # can revisit this 
            environment_class="mw1.medium",
            logging_configuration=mwaa.CfnEnvironment.LoggingConfigurationProperty(
                dag_processing_logs=mwaa.CfnEnvironment.ModuleLoggingConfigurationProperty(
                    enabled=True,
                    log_level="INFO"
                ),
                task_logs=mwaa.CfnEnvironment.ModuleLoggingConfigurationProperty(
                    enabled=True,
                    log_level="INFO"
                ),
                worker_logs=mwaa.CfnEnvironment.ModuleLoggingConfigurationProperty(
                    enabled=True,
                    log_level="INFO"
                ),
                scheduler_logs=mwaa.CfnEnvironment.ModuleLoggingConfigurationProperty(
                    enabled=True,
                    log_level="INFO"
                ),
                webserver_logs=mwaa.CfnEnvironment.ModuleLoggingConfigurationProperty(
                    enabled=True,
                    log_level="INFO"
                ),
            ),
            max_workers=10,
            min_workers=2,
            source_bucket_arn=source_bucket_arn,
            webserver_access_mode="PUBLIC_ONLY",
            execution_role_arn=mwaa_service_role.role_arn,
            dag_s3_path="dags",
            requirements_s3_path="requires/requirements-2024-01-12-1518.txt",
            network_configuration=mwaa.CfnEnvironment.NetworkConfigurationProperty(
                subnet_ids=private_subnet_ids,
                security_group_ids=[mwaa_sec_group.security_group_id]
            )
        )
        mwaa_env.node.add_dependency(self.vpc)
        mwaa_env.node.add_dependency(mwaa_sec_group)
        mwaa_env.node.add_dependency(managed_policy)
        mwaa_env.node.add_dependency(mwaa_service_role)
        mwaa_env.node.add_dependency(s3_vpc_endpoint)
        mwaa_env.node.add_dependency(kms_vpc_endpoint)
        mwaa_env.node.add_dependency(sqs_vpc_endpoint)
        mwaa_env.node.add_dependency(logs_vpc_endpoint)
        mwaa_env.node.add_dependency(monitoring_vpc_endpoint)
        mwaa_env.node.add_dependency(ecr_api_vpc_endpoint)
        mwaa_env.node.add_dependency(ecr_dkr_vpc_endpoint)
