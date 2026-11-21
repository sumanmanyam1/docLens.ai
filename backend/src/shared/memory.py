"""Memory: the audit log. Each agent writes one row per job into the audit_log table.

The audit log is the proof of what each stage did for a given job.
"""
import time

import boto3

from shared.config import AUDIT_TABLE, REGION


def write_audit(job_id: str, stage: str, summary: dict) -> None:
    """Save one row: which job, which stage, when, and a short summary."""
    table = boto3.resource("dynamodb", region_name=REGION).Table(AUDIT_TABLE)
    table.put_item(Item={
        "job_id": job_id,
        "stage": stage,
        "timestamp": int(time.time()),
        **summary,
    })
