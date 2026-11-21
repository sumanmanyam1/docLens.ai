"""POST /jobs: check the input, create a job, start the pipeline (ADR-003).

Steps: check the text -> save a RUNNING job -> start Step Functions -> return job_id.
The page then polls GET /jobs/{job_id} (see get_status).
"""
import json
import time
import uuid

import boto3

from shared.config import JOBS_TABLE, MAX_CHARS, REGION, STATE_MACHINE_ARN


def _response(status_code, body):
    """Build the reply format API Gateway expects."""
    return {"statusCode": status_code, "body": json.dumps(body)}


def _jobs_table():
    return boto3.resource("dynamodb", region_name=REGION).Table(JOBS_TABLE)


def _start_pipeline(job_id, text):
    """Start the Step Functions state machine. Tests replace this with a fake."""
    boto3.client("stepfunctions", region_name=REGION).start_execution(
        stateMachineArn=STATE_MACHINE_ARN,
        input=json.dumps({"job_id": job_id, "text": text}),
    )


def handler(event, context):
    # 1. Read and check the input.
    try:
        body = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return _response(400, {"error": "body must be valid JSON"})
    text = (body.get("text") or "").strip() if isinstance(body, dict) else ""

    if not text:
        return _response(400, {"error": "text is required"})
    if len(text) > MAX_CHARS:
        return _response(400, {"error": f"text exceeds {MAX_CHARS} characters"})

    # 2. Save the job so the page can ask about it straight away.
    job_id = uuid.uuid4().hex
    table = _jobs_table()
    table.put_item(Item={"job_id": job_id, "status": "RUNNING", "created_at": int(time.time())})

    # 3. Start the pipeline. If that fails, mark the job FAILED so it never hangs.
    try:
        _start_pipeline(job_id, text)
    except Exception:
        table.update_item(
            Key={"job_id": job_id},
            UpdateExpression="SET #s = :s, #e = :e",
            ExpressionAttributeNames={"#s": "status", "#e": "error"},
            ExpressionAttributeValues={":s": "FAILED", ":e": "Could not start the analysis."},
        )
        return _response(500, {"error": "could not start the analysis"})

    return _response(202, {"job_id": job_id})
