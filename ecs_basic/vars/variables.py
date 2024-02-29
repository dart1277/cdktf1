from cdktf import TerraformVariable
from constructs import Construct

__all__ = ["VariablesConstruct"]


class VariablesConstruct(Construct):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)

        # self.aws_profile = TerraformVariable(self, "aws_profile",
        #                                      type="string",
        #                                      default="deploy",
        #                                      description="aws_profile"
        #                                      ).string_value
        #
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
