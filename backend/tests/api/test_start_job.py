"""Tests for the start_job Lambda. Bad input is rejected; good input starts a job."""
import json

import pytest

from api.start_job import handler as start


def make_event(text):
    return {"body": json.dumps({"text": text})}


@pytest.fixture
def started(monkeypatch):
    """Replace the real Step Functions call with a fake that records its input."""
    calls = []
    monkeypatch.setattr(start, "_start_pipeline", lambda job_id, text: calls.append((job_id, text)))
    return calls


def test_empty_text_rejected(aws, started):
    assert start.handler(make_event(""), None)["statusCode"] == 400
    assert started == []


def test_too_long_rejected(aws, started):
    assert start.handler(make_event("a" * 20_001), None)["statusCode"] == 400
    assert started == []


def test_bad_json_rejected(aws, started):
    assert start.handler({"body": "not json"}, None)["statusCode"] == 400


def test_valid_text_starts_a_job(aws, started):
    reply = start.handler(make_event("A short lease."), None)
    job_id = json.loads(reply["body"])["job_id"]

    assert reply["statusCode"] == 202
    assert started == [(job_id, "A short lease.")]
    job = aws.Table("jobs").get_item(Key={"job_id": job_id})["Item"]
    assert job["status"] == "RUNNING"


def test_exactly_max_length_is_accepted(aws, started):
    assert start.handler(make_event("a" * 20_000), None)["statusCode"] == 202


def test_failure_to_start_marks_job_failed(aws, monkeypatch):
    def boom(job_id, text):
        raise RuntimeError("step functions is down")
    monkeypatch.setattr(start, "_start_pipeline", boom)

    reply = start.handler(make_event("A short lease."), None)

    assert reply["statusCode"] == 500
    jobs = aws.Table("jobs").scan()["Items"]
    assert len(jobs) == 1 and jobs[0]["status"] == "FAILED"
