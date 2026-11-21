"""Tests for stage 1. The AI call and the audit log are faked, so no AWS is used."""
import pytest

from agents.clause_extractor import handler as stage

LEASE = """RESIDENTIAL LEASE AGREEMENT (FAKE TEST TEXT)

1. Term. This lease starts on January 1 and runs for twelve (12) months.

2. Automatic Renewal. Unless Tenant gives written notice at least ninety (90) days before the end of the term, this lease renews automatically for another twelve (12) months.

3. Rent. Tenant pays $1,500 per month, due on the first day of each month.
"""


@pytest.fixture
def audit_rows(monkeypatch):
    """Replace write_audit with a fake that just remembers what it was given."""
    rows = []
    monkeypatch.setattr(stage, "write_audit", lambda job, name, summary: rows.append((job, name, summary)))
    return rows


def fake_ai(monkeypatch, reply):
    """Make call_model return a ready-made reply instead of calling Bedrock."""
    monkeypatch.setattr(stage, "call_model", lambda system, text: reply)


def test_good_reply_returns_clauses(monkeypatch, audit_rows):
    fake_ai(monkeypatch, {"clauses": [
        {"clause_id": 1, "original_text": "1. Term. This lease starts on January 1 and runs for twelve (12) months."},
        {"clause_id": 2, "original_text": "3. Rent. Tenant pays $1,500 per month, due on the first day of each month."},
    ]})
    result = stage.handler({"job_id": "j1", "text": LEASE}, None)
    assert len(result["clauses"]) == 2
    assert result["job_id"] == "j1"


def test_audit_row_is_written(monkeypatch, audit_rows):
    fake_ai(monkeypatch, {"clauses": [{"clause_id": 1, "original_text": "3. Rent. Tenant pays $1,500 per month"}]})
    stage.handler({"job_id": "j1", "text": LEASE}, None)
    assert audit_rows[0][0:2] == ("j1", "1#clause-extractor")
    assert audit_rows[0][2]["clause_count"] == 1


def test_missing_clauses_key_fails(monkeypatch, audit_rows):
    fake_ai(monkeypatch, {"oops": []})
    with pytest.raises(ValueError):
        stage.handler({"job_id": "j1", "text": LEASE}, None)


def test_empty_clause_list_fails(monkeypatch, audit_rows):
    fake_ai(monkeypatch, {"clauses": []})
    with pytest.raises(ValueError):
        stage.handler({"job_id": "j1", "text": LEASE}, None)


def test_clause_missing_field_fails(monkeypatch, audit_rows):
    fake_ai(monkeypatch, {"clauses": [{"clause_id": 1}]})
    with pytest.raises(ValueError):
        stage.handler({"job_id": "j1", "text": LEASE}, None)


def test_invented_clause_fails(monkeypatch, audit_rows):
    fake_ai(monkeypatch, {"clauses": [{"clause_id": 1, "original_text": "Tenant must pay a pet fee of $500."}]})
    with pytest.raises(ValueError):
        stage.handler({"job_id": "j1", "text": LEASE}, None)
    assert audit_rows == []   # nothing is logged as success when validation fails
