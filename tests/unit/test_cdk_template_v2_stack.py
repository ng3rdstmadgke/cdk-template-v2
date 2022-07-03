import aws_cdk as core
import aws_cdk.assertions as assertions

from cdk_template_v2.cdk_template_v2_stack import CdkTemplateV2Stack

# example tests. To run these tests, uncomment this file along with the example
# resource in cdk_template_v2/cdk_template_v2_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = CdkTemplateV2Stack(app, "cdk-template-v2")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
