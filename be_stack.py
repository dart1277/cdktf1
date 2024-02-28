from constructs import Construct
from cdktf import App, CloudBackend, NamedCloudWorkspace, TerraformStack, TerraformOutput
class RemoteBackendStack(TerraformStack):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)

        CloudBackend(self,
            hostname = "app.terraform.io",
            organization = "company",
            workspaces = NamedCloudWorkspace("my-app-prod")
        )

        TerraformOutput(self, "dns-server",
            value = "hello-world"
        )

app = App()
RemoteBackendStack(app, "hello-terraform")
app.synth()