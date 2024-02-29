#!/usr/bin/env python3
import os

import aws_cdk as cdk

from cdk_event_bridge_lambda.cdk_event_bridge_lambda_stack import CdkEventBridgeLambdaStack

app = cdk.App()

# cdk init app --language python
# cdk synth
# cdk bootstrap
# cdk deploy --require-approval never
# cdk destroy --require-approval never

# if context gets corrupted (account metadata is outdated or incorrect)
# cdk context --clear

CdkEventBridgeLambdaStack(app, "CdkEventBridgeLambdaStack",
                          env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'),
                                              region=os.getenv('CDK_DEFAULT_REGION'))
                          )

app.synth()
