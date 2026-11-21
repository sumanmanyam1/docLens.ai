"""The Lambda functions: 3 AI agents + 2 API functions (ADR-001, 003, 005).

Every Lambda gets the whole src/ folder as its code, so it can use src/shared/.
Each one only gets the permissions it needs (least privilege).
"""
from types import SimpleNamespace

import aws_cdk as cdk
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as lambda_

from infra.settings import MODEL_ID, PREFIX, SRC_DIR


def _make_lambda(stack, group, folder, timeout_seconds, tables):
    """Create one Lambda from src/<group>/<folder>/handler.py."""
    jobs_table, audit_table = tables
    return lambda_.Function(
        stack, f"{folder}_fn",
        function_name=f"{PREFIX}-{folder.replace('_', '-')}",    # e.g. suman-clause-extractor
        runtime=lambda_.Runtime.PYTHON_3_12,
        code=lambda_.Code.from_asset(SRC_DIR, exclude=["**/__pycache__"]),
        handler=f"{group}.{folder}.handler.handler",            # e.g. agents.clause_extractor.handler.handler
        timeout=cdk.Duration.seconds(timeout_seconds),
        memory_size=256,
        environment={
            "JOBS_TABLE": jobs_table.table_name,
            "AUDIT_TABLE": audit_table.table_name,
            "MODEL_ID": MODEL_ID,
        },
    )


def create_lambdas(stack, tables):
    """Return all five Lambdas as fns.extractor, fns.flagger, fns.rewriter, fns.start, fns.status."""
    jobs_table, audit_table = tables
    fns = SimpleNamespace(
        # The three agents call the AI, so they get a longer timeout.
        extractor=_make_lambda(stack, "agents", "clause_extractor", 90, tables),
        flagger=_make_lambda(stack, "agents", "risk_flagger", 90, tables),
        rewriter=_make_lambda(stack, "agents", "plain_english_rewriter", 90, tables),
        # The two API functions should answer quickly.
        start=_make_lambda(stack, "api", "start_job", 10, tables),
        status=_make_lambda(stack, "api", "get_status", 10, tables),
    )

    # Permission to call the AI model through Bedrock (the 3 agents only).
    # The first resource is the cross-region "inference profile", the second
    # is the model itself, which the profile may route to in several regions.
    bedrock_policy = iam.PolicyStatement(
        actions=["bedrock:InvokeModel"],
        resources=[
            f"arn:aws:bedrock:{stack.region}:{stack.account}:inference-profile/{MODEL_ID}",
            "arn:aws:bedrock:*::foundation-model/anthropic.claude-sonnet-4-6*",
        ],
    )
    for fn in (fns.extractor, fns.flagger, fns.rewriter):
        fn.add_to_role_policy(bedrock_policy)
        audit_table.grant_write_data(fn)          # each agent writes an audit row

    # start_job creates job rows; get_status reads jobs and counts audit rows.
    jobs_table.grant_read_write_data(fns.start)
    jobs_table.grant_read_data(fns.status)
    audit_table.grant_read_data(fns.status)
    return fns
