from pathlib import Path

from aws_cdk import (
    # Duration,
    Stack, Duration, RemovalPolicy,
    # aws_sqs as sqs,
)
from aws_cdk.aws_dynamodb import Table, Attribute, AttributeType, BillingMode
from aws_cdk.aws_ec2 import Vpc, SecurityGroup, Peer, Port, SubnetSelection, SubnetType
from aws_cdk.aws_events import Rule, Schedule
from aws_cdk.aws_events_targets import LambdaFunction
from aws_cdk.aws_iam import PolicyStatement
from aws_cdk.aws_lambda import Function, Runtime, Code
from aws_cdk.aws_logs import RetentionDays
from aws_cdk.aws_s3 import Bucket, BucketEncryption
from constructs import Construct


class CdkEventBridgeLambdaStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc_name = ""
        s3_bucket_name = "test-bucket-123421234"
        dynamo_table_name = "test-table-123421234"

        # Import VPC
        vpc = Vpc.from_lookup(self, "LambdaVpc", is_default=True, vpc_name=vpc_name)

        default_security_group = SecurityGroup.from_lookup_by_name(self, "DefaultSecurityGroupFromName",
                                                                   security_group_name="default",
                                                                   vpc=vpc
                                                                   )

        default_sg = SecurityGroup.from_security_group_id(self, "DefaultSecurityGroup",
                                                          security_group_id=default_security_group.security_group_id,
                                                          allow_all_outbound=False,
                                                          mutable=True
                                                          )

        # Create DynamoDB table
        table = Table(self, "MyDynamoDBTable",
                      table_name=dynamo_table_name,
                      partition_key=Attribute(
                          name="id",
                          type=AttributeType.STRING
                      ),
                      billing_mode=BillingMode.PAY_PER_REQUEST,
                      removal_policy=RemovalPolicy.DESTROY
                      )

        # Create S3 bucket
        bucket = Bucket(self, "MyS3Bucket",
                        bucket_name=s3_bucket_name,
                        removal_policy=RemovalPolicy.DESTROY,
                        encryption=BucketEncryption.KMS_MANAGED,
                        enforce_ssl=True,
                        versioned=True,
                        bucket_key_enabled=True,
                        auto_delete_objects=True,
                        )

        lambda_sg = SecurityGroup(self, "ScheduledLambdaSg",
                                  allow_all_outbound=False,
                                  security_group_name="scheduled-lambda-sg",
                                  vpc=vpc
                                  )

        lambda_sg.add_egress_rule(
            peer=Peer.any_ipv4(), #Peer.ipv4(cidr_ip=vpc.vpc_cidr_block),
            connection=Port.tcp(443)
        )

        lambda_path = str(Path(__name__).parent.parent / "cdk_event_bridge_lambda" / "lambda_" / "event_bridge_lambda")

        lambda_function = Function(self, "ScheduledLambdaFunction",
                                   function_name="scheduled-lambda-handler",
                                   runtime=Runtime.PYTHON_3_10,
                                   handler="index.handler",
                                   code=Code.from_asset(lambda_path),
                                   log_retention=RetentionDays.ONE_MONTH,
                                   vpc=vpc,
                                   vpc_subnets=SubnetSelection(subnet_type=SubnetType.PRIVATE_WITH_EGRESS),
                                   memory_size=512,
                                   environment={
                                       "S3_BUCKET_NAME": s3_bucket_name,
                                       "DYNAMO_TABLE_NAME": dynamo_table_name,
                                   },
                                   timeout=Duration.seconds(300),
                                   security_groups=[lambda_sg]
                                   )

        dynamodb_policy_statement = PolicyStatement(
            actions=[
                "dynamodb:GetItem",
                "dynamodb:Scan",
                "dynamodb:Query"
            ],
            resources=[f"arn:aws:dynamodb:{self.region}:{self.account}:table/{dynamo_table_name}"]
        )

        # Create a policy statement for S3 bucket access
        s3_policy_statement = PolicyStatement(
            actions=[
                "s3:GetObject",
                "s3:PutObject",
                "s3:ListBucket"
            ],
            resources=[
                f"arn:aws:s3:::{s3_bucket_name}",
                f"arn:aws:s3:::{s3_bucket_name}/*"
            ]
        )

        logging_policy_statement = PolicyStatement(
            actions=["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"],
            resources=[f"arn:aws:logs:{self.region}:{self.account}:*"])

        lambda_function.add_to_role_policy(
            statement=logging_policy_statement
        )

        lambda_function.add_to_role_policy(
            statement=s3_policy_statement
        )

        lambda_function.add_to_role_policy(
            statement=dynamodb_policy_statement
        )

        # Create an EventBridge rule to trigger the Lambda every hour at 2am UTC
        rule = Rule(
            self, "Rule",
            # schedule=Schedule.cron(hour="2", minute="0"),
            schedule=Schedule.cron(),
        )
        rule.add_target(LambdaFunction(lambda_function))
