#!/usr/bin/env python3
import os

import aws_cdk as cdk

from aws_cdk_python_for_amazon_mwaa.aws_cdk_python_for_amazon_mwaa_stack import AwsCdkPythonForAmazonMwaaStack
from aws_cdk_python_for_amazon_mwaa.airflow_source_stack import AirflowSourceStack



app = cdk.App()

mwaa_source = AirflowSourceStack(app, "AirflowSourceStack")

AwsCdkPythonForAmazonMwaaStack(
    app, 
    "AwsCdkPythonForAmazonMwaaStack",
    source_bucket=mwaa_source.source_bucket

    # If you don't specify 'env', this stack will be environment-agnostic.
    # Account/Region-dependent features and context lookups will not work,
    # but a single synthesized template can be deployed anywhere.

    # Uncomment the next line to specialize this stack for the AWS Account
    # and Region that are implied by the current CLI configuration.

    #env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),

    # Uncomment the next line if you know exactly what Account and Region you
    # want to deploy the stack to. */

    #env=cdk.Environment(account='123456789012', region='us-east-1'),

    # For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html
    )

app.synth()
