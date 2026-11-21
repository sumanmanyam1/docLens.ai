"""Memory: the two DynamoDB tables (ADR-004).

- jobs:      one row per job (status and the finished result)
- audit_log: one row per agent per job (what each agent did)
"""
import aws_cdk as cdk
from aws_cdk import aws_dynamodb as dynamodb

from infra.settings import PREFIX


def create_tables(stack):
    """Return (jobs_table, audit_table)."""
    jobs_table = dynamodb.Table(
        stack, "JobsTable",
        table_name=f"{PREFIX}-jobs",
        partition_key=dynamodb.Attribute(name="job_id", type=dynamodb.AttributeType.STRING),
        billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,  # pay only when used
        removal_policy=cdk.RemovalPolicy.DESTROY,           # `cdk destroy` deletes it
    )

    audit_table = dynamodb.Table(
        stack, "AuditLogTable",
        table_name=f"{PREFIX}-audit-log",
        partition_key=dynamodb.Attribute(name="job_id", type=dynamodb.AttributeType.STRING),
        sort_key=dynamodb.Attribute(name="stage", type=dynamodb.AttributeType.STRING),
        billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
        removal_policy=cdk.RemovalPolicy.DESTROY,
    )
    return jobs_table, audit_table
