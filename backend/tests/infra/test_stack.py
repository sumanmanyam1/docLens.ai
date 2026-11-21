"""Checks the CDK stack by building the template on this machine. Nothing is deployed."""
import json

import aws_cdk as cdk
import pytest
from aws_cdk.assertions import Match, Template

from infra.stack import DocExplainerStack


@pytest.fixture(scope="module")
def template():
    app = cdk.App()
    stack = DocExplainerStack(app, "TestStack", env=cdk.Environment(account="111111111111", region="us-east-1"))
    return Template.from_stack(stack)


def test_two_tables_that_can_be_destroyed(template):
    template.resource_count_is("AWS::DynamoDB::Table", 2)
    for table in template.find_resources("AWS::DynamoDB::Table").values():
        assert table["DeletionPolicy"] == "Delete"


def our_lambdas(template):
    """Our 5 named Lambdas. CDK also adds unnamed helper Lambdas for the website upload."""
    return [f for f in template.find_resources("AWS::Lambda::Function").values()
            if "FunctionName" in f["Properties"]]


def test_five_python_lambdas(template):
    lambdas = our_lambdas(template)
    assert len(lambdas) == 5
    assert all(f["Properties"]["Runtime"] == "python3.12" for f in lambdas)


def test_one_state_machine(template):
    template.resource_count_is("AWS::StepFunctions::StateMachine", 1)


def test_state_machine_has_three_stages_with_retry_and_catch(template):
    machine = next(iter(template.find_resources("AWS::StepFunctions::StateMachine").values()))
    definition = json.dumps(machine["Properties"]["DefinitionString"])
    for name in ("Extract clauses", "Flag risks", "Rewrite in plain English", "Save result", "Save failure"):
        assert name in definition
    assert definition.count("MaxAttempts") == 3     # one Retry per stage
    assert definition.count("Catch") >= 3


def test_api_has_the_two_routes(template):
    template.has_resource_properties("AWS::ApiGatewayV2::Route", {"RouteKey": "POST /jobs"})
    template.has_resource_properties("AWS::ApiGatewayV2::Route", {"RouteKey": "GET /jobs/{job_id}"})


def test_api_is_throttled(template):
    template.has_resource_properties("AWS::ApiGatewayV2::Stage", {
        "DefaultRouteSettings": {"ThrottlingRateLimit": 2, "ThrottlingBurstLimit": 5}})


def test_bedrock_is_scoped_not_wildcard(template):
    policies = template.find_resources("AWS::IAM::Policy")
    statements = [s for p in policies.values() for s in p["Properties"]["PolicyDocument"]["Statement"]]
    bedrock = [s for s in statements if s["Action"] == "bedrock:InvokeModel"]
    assert bedrock, "stage Lambdas need Bedrock permission"
    assert all(s["Resource"] != "*" for s in bedrock)


def test_every_named_resource_starts_with_suman(template):
    names = []
    names += [f["Properties"]["FunctionName"] for f in our_lambdas(template)]
    for kind, key in (("AWS::DynamoDB::Table", "TableName"),
                      ("AWS::StepFunctions::StateMachine", "StateMachineName"),
                      ("AWS::ApiGatewayV2::Api", "Name")):
        for resource in template.find_resources(kind).values():
            names.append(resource["Properties"][key])
    for bucket in template.find_resources("AWS::S3::Bucket").values():
        names.append(bucket["Properties"]["BucketName"])
    assert len(names) == 2 + 5 + 1 + 1 + 1
    assert all(name.startswith("suman-") for name in names)


def test_website_bucket_is_private_and_encrypted(template):
    template.resource_count_is("AWS::S3::Bucket", 1)
    template.has_resource_properties("AWS::S3::Bucket", {
        "PublicAccessBlockConfiguration": {
            "BlockPublicAcls": True, "BlockPublicPolicy": True,
            "IgnorePublicAcls": True, "RestrictPublicBuckets": True},
        "BucketEncryption": Match.any_value(),
    })


def test_website_bucket_is_deleted_by_cdk_destroy(template):
    bucket = next(iter(template.find_resources("AWS::S3::Bucket").values()))
    assert bucket["DeletionPolicy"] == "Delete"


def test_one_cloudfront_site_with_https_and_index_page(template):
    template.resource_count_is("AWS::CloudFront::Distribution", 1)
    template.has_resource_properties("AWS::CloudFront::Distribution", {
        "DistributionConfig": Match.object_like({
            "DefaultRootObject": "index.html",
            "DefaultCacheBehavior": Match.object_like({"ViewerProtocolPolicy": "redirect-to-https"}),
        })})


def test_cloudfront_reads_bucket_with_origin_access_control(template):
    template.resource_count_is("AWS::CloudFront::OriginAccessControl", 1)


def test_frontend_url_is_an_output(template):
    assert "FrontendUrl" in template.find_outputs("*")


def test_lambda_handlers_point_into_src(template):
    handlers = {f["Properties"]["FunctionName"]: f["Properties"]["Handler"] for f in our_lambdas(template)}
    assert handlers == {
        "suman-clause-extractor": "agents.clause_extractor.handler.handler",
        "suman-risk-flagger": "agents.risk_flagger.handler.handler",
        "suman-plain-english-rewriter": "agents.plain_english_rewriter.handler.handler",
        "suman-start-job": "api.start_job.handler.handler",
        "suman-get-status": "api.get_status.handler.handler",
    }


def test_every_agent_has_a_prompt_file():
    from pathlib import Path
    agents_dir = Path(__file__).parents[2] / "src" / "agents"
    for agent in ("clause_extractor", "risk_flagger", "plain_english_rewriter"):
        assert (agents_dir / agent / "prompt.md").read_text().strip()
