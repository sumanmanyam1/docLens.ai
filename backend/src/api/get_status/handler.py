"""GET /jobs/{job_id}: return the job status and result (ADR-003, ADR-004).

Reply: {job_id, status, completed_stages, result?, error?}
- status is RUNNING, SUCCEEDED or FAILED (saved in the jobs table).
- completed_stages (0 to 3) is how many audit_log rows the job has.
  Each finished stage writes one row, so this gives the page real progress.
- The finished result is saved in the jobs table as a JSON string ("result_json").
"""
import json

import boto3
from boto3.dynamodb.conditions import Key

from shared.config import AUDIT_TABLE, JOBS_TABLE, REGION

TOTAL_STAGES = 3


def _response(status_code, body):
    return {"statusCode": status_code, "body": json.dumps(body)}


def _count_finished_stages(job_id):
    """Count this job's audit rows. Each finished stage wrote one."""
    table = boto3.resource("dynamodb", region_name=REGION).Table(AUDIT_TABLE)
    reply = table.query(KeyConditionExpression=Key("job_id").eq(job_id), Select="COUNT")
    return min(reply["Count"], TOTAL_STAGES)


def handler(event, context):
    job_id = (event.get("pathParameters") or {}).get("job_id", "")

    table = boto3.resource("dynamodb", region_name=REGION).Table(JOBS_TABLE)
    job = table.get_item(Key={"job_id": job_id}).get("Item")
    if not job:
        return _response(404, {"error": "job not found"})

    status = job["status"]
    reply = {"job_id": job_id, "status": status}

    if status == "SUCCEEDED":
        reply["completed_stages"] = TOTAL_STAGES
        reply["result"] = json.loads(job["result_json"])
    else:
        reply["completed_stages"] = _count_finished_stages(job_id)
        if status == "FAILED":
            reply["error"] = job.get("error", "The analysis failed.")

    return _response(200, reply)
