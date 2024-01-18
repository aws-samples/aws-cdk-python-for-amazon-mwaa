import aws_cdk as core
import aws_cdk.assertions as assertions

from aws_cdk_python_for_amazon_mwaa.aws_cdk_python_for_amazon_mwaa_stack import AwsCdkPythonForAmazonMwaaStack

# example tests. To run these tests, uncomment this file along with the example
# resource in aws_cdk_python_for_amazon_mwaa/aws_cdk_python_for_amazon_mwaa_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = AwsCdkPythonForAmazonMwaaStack(app, "aws-cdk-python-for-amazon-mwaa")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
