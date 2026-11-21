"""The front desk: an HTTP API with two routes (ADR-003).

  POST /jobs            -> start_job   (send a document, get a job_id)
  GET  /jobs/{job_id}   -> get_status  (ask "is it done yet?")
"""
import aws_cdk as cdk
from aws_cdk import aws_apigatewayv2 as apigw
from aws_cdk import aws_apigatewayv2_integrations as integrations

from infra.settings import PREFIX


def create_api(stack, fns):
    api = apigw.HttpApi(
        stack, "Api",
        api_name=f"{PREFIX}-doc-explainer-api",
        cors_preflight=apigw.CorsPreflightOptions(   # lets the web page call the API
            allow_origins=["*"],                      # demo only; restrict for real use
            allow_methods=[apigw.CorsHttpMethod.GET, apigw.CorsHttpMethod.POST],
            allow_headers=["content-type"],
        ),
    )
    api.add_routes(
        path="/jobs",
        methods=[apigw.HttpMethod.POST],
        integration=integrations.HttpLambdaIntegration("StartJob", fns.start),
    )
    api.add_routes(
        path="/jobs/{job_id}",
        methods=[apigw.HttpMethod.GET],
        integration=integrations.HttpLambdaIntegration("GetStatus", fns.status),
    )

    # The API has no login, so cap the request rate to limit Bedrock cost (demo safety).
    api.default_stage.node.default_child.default_route_settings = apigw.CfnStage.RouteSettingsProperty(
        throttling_rate_limit=2,
        throttling_burst_limit=5,
    )

    cdk.CfnOutput(stack, "ApiUrl", value=api.api_endpoint)
    return api
