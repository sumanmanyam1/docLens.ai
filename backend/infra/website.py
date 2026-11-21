"""The website: a private S3 bucket behind CloudFront (spec section 5)."""
import aws_cdk as cdk
from aws_cdk import aws_cloudfront as cloudfront
from aws_cdk import aws_cloudfront_origins as origins
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_s3_deployment as s3deploy

from infra.settings import FRONTEND_DIR, PREFIX


def create_website(stack):
    # A private bucket that holds index.html. Nobody can read it directly.
    bucket = s3.Bucket(
        stack, "FrontendBucket",
        bucket_name=f"{PREFIX}-doc-explainer-frontend-{stack.account}",
        block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
        encryption=s3.BucketEncryption.S3_MANAGED,
        enforce_ssl=True,
        removal_policy=cdk.RemovalPolicy.DESTROY,   # `cdk destroy` deletes the bucket
        auto_delete_objects=True,                   # ...and empties it first
    )

    # CloudFront gives the page an HTTPS web address. Only CloudFront may read the bucket.
    site = cloudfront.Distribution(
        stack, "FrontendSite",
        comment=f"{PREFIX}-doc-explainer-frontend",
        default_root_object="index.html",
        default_behavior=cloudfront.BehaviorOptions(
            origin=origins.S3BucketOrigin.with_origin_access_control(bucket),
            viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
        ),
    )

    # Copy the frontend/ folder into the bucket on every deploy,
    # and clear CloudFront's cache so the newest page shows straight away.
    s3deploy.BucketDeployment(
        stack, "UploadFrontend",
        sources=[s3deploy.Source.asset(FRONTEND_DIR)],
        destination_bucket=bucket,
        distribution=site,
        distribution_paths=["/*"],
    )

    cdk.CfnOutput(stack, "FrontendUrl", value=f"https://{site.distribution_domain_name}")
    return site
