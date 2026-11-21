"""Shared settings used by all Lambdas.

Keeping them in one place means you change a value once, not in five files.
"""
import os

# Longest document we accept (see ADR-003). Longer text is rejected.
MAX_CHARS = 20_000

# The AI model we call through Amazon Bedrock.
MODEL_ID = os.environ.get("MODEL_ID", "us.anthropic.claude-sonnet-4-6")
REGION = os.environ.get("AWS_REGION", "us-east-1")

# DynamoDB table names. CDK passes the real names in as environment variables.
JOBS_TABLE = os.environ.get("JOBS_TABLE", "jobs")
AUDIT_TABLE = os.environ.get("AUDIT_TABLE", "audit_log")

# Added to every final result (see ADR-005).
DISCLAIMER = "This is a plain-language explanation, not legal advice."

# ARN of the Step Functions state machine. CDK passes the real value in.
STATE_MACHINE_ARN = os.environ.get("STATE_MACHINE_ARN", "")
