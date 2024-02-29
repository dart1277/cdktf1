import aws_cdk as core
import aws_cdk.assertions as assertions

from cdk_event_bridge_lambda.cdk_event_bridge_lambda_stack import CdkEventBridgeLambdaStack

# example tests. To run these tests, uncomment this file along with the example
# resource in cdk_event_bridge_lambda/cdk_event_bridge_lambda_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = CdkEventBridgeLambdaStack(app, "cdk-event-bridge-lambda")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
