#!/usr/bin/env python
import os

from cdktf import App, S3Backend, TerraformStack, TerraformOutput, DataTerraformRemoteStateS3
from cdktf_cdktf_provider_aws.provider import AwsProvider
from constructs import Construct

from vars.variables import VariablesConstruct


class MainStack(TerraformStack):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)
        self.init_stack_ctx()
        backend_state_table_name = f"{self.backend_stack_name_prefix}-state-lock-table"
        backend_state_s3_bucket_name = f"{self.backend_stack_name_prefix}-state-lock-bucket"

        AwsProvider(self, "AWS", region=self.region, profile=self.aws_profile)

        S3Backend(self,
                  bucket=backend_state_s3_bucket_name,
                  key=f"{self.stack_name}/terraform.tfstate",
                  encrypt=True,
                  region=self.region,
                  dynamodb_table=backend_state_table_name,
                  profile=self.aws_profile,
                  workspace_key_prefix=self.stack_stage
                  )

        remote_state = DataTerraformRemoteStateS3(self, f"{self.stack_name}-remote-state",
                                                  bucket=backend_state_s3_bucket_name,
                                                  key=f"s3-be-sbx/terraform.tfstate",
                                                  region=self.region
                                                  )

        s3_backend_bucket_arn = remote_state.get("s3-be-sbx-state-bucket-arn-1")

        TerraformOutput(self, f"{self.stack_name}-imported-state-bucket-arn-1",
                        value=s3_backend_bucket_arn,
                        )

        TerraformOutput(self, f"{self.stack_name}-tf-msg",
                        value=self.variables.tf_msg,
                        )

    def init_stack_ctx(self):
        self.variables = VariablesConstruct(self, f"{id}_variables")
        self.aws_profile = os.environ["AWS_PROFILE"]  # variables.aws_profile
        self.stack_stage = os.environ["STACK_STAGE"]  # variables.stack_stage
        self._stack_name_prefix = os.environ["STACK_NAME_PREFIX"]  # variables.stack_name_prefix
        self.backend_stack_name_prefix = os.environ["BACKEND_STACK_NAME_PREFIX"]  # variables.stack_name_prefix
        self.region = os.environ["REGION"]  # variables.region
        self.stack_name = f"{self._stack_name_prefix}-{self.stack_stage}"


app = App()
MainStack(app, os.environ["CDKTF_NAME"] if os.environ.get("CDKTF_NAME") else "main_stack_construct")

app.synth()
