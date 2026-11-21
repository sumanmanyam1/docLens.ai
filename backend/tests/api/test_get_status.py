"""Tests for the get_status Lambda: it reads the job and counts finished stages."""
import json

from api.get_status import handler as status


def ask(job_id):
    reply = status.handler({"pathParameters": {"job_id": job_id}}, None)
    return reply["statusCode"], json.loads(reply["body"])


def add_job(aws, job_id, state, **extra):
    aws.Table("jobs").put_item(Item={"job_id": job_id, "status": state, **extra})


def add_audit(aws, job_id, stage):
    aws.Table("audit_log").put_item(Item={"job_id": job_id, "stage": stage})


def test_unknown_job_is_404(aws):
    code, body = ask("nope")
    assert code == 404


def test_running_job_with_no_stages_done(aws):
    add_job(aws, "j1", "RUNNING")
    code, body = ask("j1")
    assert (code, body["status"], body["completed_stages"]) == (200, "RUNNING", 0)
    assert "result" not in body


def test_running_job_counts_finished_stages(aws):
    add_job(aws, "j1", "RUNNING")
    add_audit(aws, "j1", "1#clause-extractor")
    add_audit(aws, "j1", "2#risk-flagger")
    add_audit(aws, "other-job", "1#clause-extractor")   # must not be counted
    assert ask("j1")[1]["completed_stages"] == 2


def test_succeeded_job_returns_result(aws):
    result = {"disclaimer": "not legal advice", "clauses": []}
    add_job(aws, "j1", "SUCCEEDED", result_json=json.dumps(result))
    code, body = ask("j1")
    assert body["status"] == "SUCCEEDED"
    assert body["completed_stages"] == 3
    assert body["result"] == result


def test_failed_job_returns_error(aws):
    add_job(aws, "j1", "FAILED", error="Stage 2 failed.")
    code, body = ask("j1")
    assert body["status"] == "FAILED"
    assert body["error"] == "Stage 2 failed."
