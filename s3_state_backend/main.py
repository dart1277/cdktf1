#!/usr/bin/env python
import os

from cdktf import App, TerraformStack, TerraformResourceLifecycle
from cdktf_cdktf_provider_aws.dynamodb_table import (
    DynamodbTable, DynamodbTableServerSideEncryption)
from cdktf_cdktf_provider_aws.provider import AwsProvider
from cdktf_cdktf_provider_aws.s3_bucket import S3Bucket
from cdktf_cdktf_provider_aws.s3_bucket_policy import S3BucketPolicy
from cdktf_cdktf_provider_aws.s3_bucket_server_side_encryption_configuration import (
    S3BucketServerSideEncryptionConfigurationA,
    S3BucketServerSideEncryptionConfigurationRuleA,
    S3BucketServerSideEncryptionConfigurationRuleApplyServerSideEncryptionByDefaultA)
from cdktf_cdktf_provider_aws.s3_bucket_versioning import (
    S3BucketVersioningA, S3BucketVersioningVersioningConfiguration)
from constructs import Construct


class MainStack(TerraformStack):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)
        self.init_stack_ctx()

        AwsProvider(self, "AWS", region=self.region, profile=self.aws_profile)

        backend_state_s3_bucket_name = f"{self.stack_name}-state-lock-bucket"
        if len(backend_state_s3_bucket_name) >= 63:
            raise ValueError("Bucket name too long")

        s3_backend_bucket = S3Bucket(
            self,
            f"{self.stack_name}-s3-backend-bucket",
            bucket=backend_state_s3_bucket_name,
            # versioning=S3BucketVersioning(enabled=True),
            # server_side_encryption_configuration=S3BucketServerSideEncryptionConfiguration(
            #     rule=S3BucketServerSideEncryptionConfigurationRule(
            #         apply_server_side_encryption_by_default=S3BucketServerSideEncryptionConfigurationRuleApplyServerSideEncryptionByDefault(
            #             sse_algorithm="AES256"
            #         )
            #     )
            # ),
            lifecycle=TerraformResourceLifecycle(
                create_before_destroy=True,
                # prevent_destroy=True,
            )
        )

        S3BucketVersioningA(
            self,
            f"{self.stack_name}-s3-backend_bucket-versioning-config",
            bucket=s3_backend_bucket.bucket,
            versioning_configuration=S3BucketVersioningVersioningConfiguration(
                status="Enabled"
            ),
        )

        # https://github.com/hashicorp/terraform-cdk/issues/2520
        S3BucketServerSideEncryptionConfigurationA(
            self,
            f"{self.stack_name}-s3-backend-bucket-encryption-config",
            bucket=s3_backend_bucket.bucket,
            rule=[
                S3BucketServerSideEncryptionConfigurationRuleA(
                    apply_server_side_encryption_by_default=S3BucketServerSideEncryptionConfigurationRuleApplyServerSideEncryptionByDefaultA(
                        sse_algorithm="AES256"
                        # sse_algorithm="aws:kms",
                        # kms_master_key_id=s3_kms_key.target_key_arn,
                    ),
                    bucket_key_enabled=True,
                )
            ],
        )

        S3BucketPolicy(self, f"{self.stack_name}-s3-backend-bucket-policy",
                       bucket=s3_backend_bucket.bucket,
                       policy=f"""
                       {{
                         "Id": "SecureTransportPolicy",
                         "Version": "2012-10-17",
                         "Statement": [
                           {{
                             "Sid": "AllowSSLRequestsOnly",
                             "Action": "s3:*",
                             "Effect": "Deny",
                             "Resource": [
                               "arn:aws:s3:::{backend_state_s3_bucket_name}",
                               "arn:aws:s3:::{backend_state_s3_bucket_name}/*"
                             ],
                             "Condition": {{
                               "Bool": {{
                                 "aws:SecureTransport": "false"
                               }}
                             }},
                             "Principal": "*"
                           }}
                         ]
                       }}
                       """,
                       )

        backend_state_table_name = f"{self.stack_name}-state-lock-table"

        dynamodb_lock_table = DynamodbTable(
            self,
            f"{self.stack_name}-dynamodb-lock-table",
            name=backend_state_table_name,
            billing_mode="PAY_PER_REQUEST",
            attribute=[{"name": "LockID", "type": "S"}],
            hash_key="LockID",
            server_side_encryption=DynamodbTableServerSideEncryption(enabled=True),
            # deletion_protection_enabled=True,
            lifecycle=TerraformResourceLifecycle(
                create_before_destroy=True,
                # prevent_destroy=True,
            )
        )

    def init_stack_ctx(self):
        self.aws_profile = os.environ["AWS_PROFILE"]
        # self.stack_stage = os.environ["STACK_STAGE"]
        self.stack_name_prefix = os.environ["STACK_NAME_PREFIX"]
        self.target_stack_name_prefix = os.environ["TARGET_NAME_PREFIX"]
        self.region = os.environ["REGION"]
        self.stack_name = f"{self.target_stack_name_prefix}-{self.stack_name_prefix}"


app = App()
MainStack(
    app,
    (
        os.environ["CDKTF_NAME"]
        if os.environ.get("CDKTF_NAME")
        else "terraform_remote_backend_stack_construct"
    ),
)

app.synth()
