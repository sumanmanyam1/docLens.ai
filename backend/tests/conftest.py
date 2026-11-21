"""Shared test setup: a fake AWS (moto) with the two DynamoDB tables.

Fake credentials are set so a test can never reach the real AWS by accident.
"""
import os

import boto3
import pytest
from moto import mock_aws

# CDK complains about this machine's cache folder permissions, so turn its cache off.
os.environ.setdefault("JSII_RUNTIME_PACKAGE_CACHE", "disabled")


@pytest.fixture
def aws(monkeypatch):
    for name, value in {"AWS_ACCESS_KEY_ID": "testing", "AWS_SECRET_ACCESS_KEY": "testing",
                        "AWS_SESSION_TOKEN": "testing", "AWS_DEFAULT_REGION": "us-east-1"}.items():
        monkeypatch.setenv(name, value)
    with mock_aws():
        db = boto3.resource("dynamodb", region_name="us-east-1")
        db.create_table(
            TableName="jobs", BillingMode="PAY_PER_REQUEST",
            KeySchema=[{"AttributeName": "job_id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "job_id", "AttributeType": "S"}])
        db.create_table(
            TableName="audit_log", BillingMode="PAY_PER_REQUEST",
            KeySchema=[{"AttributeName": "job_id", "KeyType": "HASH"}, {"AttributeName": "stage", "KeyType": "RANGE"}],
            AttributeDefinitions=[{"AttributeName": "job_id", "AttributeType": "S"},
                                  {"AttributeName": "stage", "AttributeType": "S"}])
        yield db
