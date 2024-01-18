from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_s3_deployment as s3_deployment
)
from constructs import Construct

class AirflowSourceStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # s3 bucket containing DAG code
        self.source_bucket = s3.Bucket(
            self,
            "mwaa_source_bucket",
            versioned=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL
        )

        # deploy DAG code to S3 Bucket
        s3_deployment.BucketDeployment(
            self,
            "mwaa_source_bucket_dags_deployment",
            sources=[s3_deployment.Source.asset("./dags")],
            destination_bucket=self.source_bucket,
            destination_key_prefix="dags"
        )

        # deploy requirements to S3 Bucket
        s3_deployment.BucketDeployment(
            self,
            "mwaa_source_requirements_deployment",
            sources=[s3_deployment.Source.asset("./requires")],
            destination_bucket=self.source_bucket,
            destination_key_prefix="requires"
        )
