from cdktf import TerraformVariable
from constructs import Construct

__all__ = ["VariablesConstruct"]


class VariablesConstruct(Construct):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)

        # note "scope" arg - main stack construct reference
        # variable precedence in tf is (highest to lowest):
        # * any_name.auto.tfvars
        # * terraform.tfvars
        # * --var="tfMsg=a" # on commandline
        # * TF_VAR_tfMsg="aaaaaaaaaaaa" # environment variable

        self.tf_msg = TerraformVariable(scope, "tfMsg",
                                        type="string",
                                        default="a",
                                        description="tf_msg"
                                        ).string_value

        # self.stack_stage = TerraformVariable(self, "stack_stage",
        #                                      type="string",
        #                                      description="stack_stage"
        #                                      ).string_value
        #
        # self.stack_name_prefix = TerraformVariable(self, "stack_name_prefix",
        #                                            type="string",
        #                                            default="sbx_stack",
        #                                            description="stack_name_prefix"
        #                                            ).string_value
        #
        # self.region = TerraformVariable(self, "region",
        #                                 type="string",
        #                                 description="region"
        #                                 ).string_value

        #
        # self.aws_profile = TerraformVariable(self, "",
        #                                      type="string",
        #                                      default="",
        #                                      description=""
        #                                      )
        #
