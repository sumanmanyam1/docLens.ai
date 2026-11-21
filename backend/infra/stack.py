"""The whole system in one place. Each line builds one part (see the files next to this one).

CDK turns this into a CloudFormation template. Nothing is created in AWS until
someone runs `cdk deploy`.

  storage.py       Memory:        2 DynamoDB tables
  agents.py        Agents + API:  5 Lambda functions and their permissions
  orchestrator.py  Orchestrator:  Step Functions runs the 3 agents with Retry and Catch
  api.py           Front desk:    HTTP API (POST /jobs, GET /jobs/{job_id})
  website.py       Website:       private S3 bucket + CloudFront
"""
import aws_cdk as cdk
from constructs import Construct

from infra import agents, api, orchestrator, storage, website


class DocExplainerStack(cdk.Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        jobs_table, audit_table = storage.create_tables(self)
        fns = agents.create_lambdas(self, (jobs_table, audit_table))
        orchestrator.create_pipeline(self, fns, jobs_table)
        api.create_api(self, fns)
        website.create_website(self)
