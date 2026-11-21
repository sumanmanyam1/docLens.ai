"""Tests for stage 2. The AI call and the audit log are faked, so no AWS is used."""
import pytest

from agents.risk_flagger import handler as stage

CLAUSES = [
    {"clause_id": 1, "original_text": "Term. Twelve months."},
    {"clause_id": 2, "original_text": "Automatic Renewal. The lease renews unless notice is given 90 days before."},
]


def good_reply():
    return {"clauses": [
        {"clause_id": 1, "risk_level": "low", "category": "other", "reason": ""},
        {"clause_id": 2, "risk_level": "high", "category": "auto-renewal", "reason": "Renews for a year if you miss the notice."},
    ]}


@pytest.fixture
def audit_rows(monkeypatch):
    rows = []
    monkeypatch.setattr(stage, "write_audit", lambda job, name, summary: rows.append((job, name, summary)))
    return rows


def run(monkeypatch, reply):
    """Run the stage with a fake AI reply."""
    monkeypatch.setattr(stage, "call_model", lambda system, text: reply)
    return stage.handler({"job_id": "j1", "text": "whole document", "clauses": CLAUSES}, None)


def test_good_reply_adds_risk_fields(monkeypatch, audit_rows):
    result = run(monkeypatch, good_reply())
    assert result["clauses"][1]["risk_level"] == "high"
    assert result["clauses"][1]["category"] == "auto-renewal"
    assert result["job_id"] == "j1"


def test_original_text_is_not_changed(monkeypatch, audit_rows):
    reply = good_reply()
    reply["clauses"][1]["original_text"] = "AI rewrote this"   # the AI must not be able to change it
    result = run(monkeypatch, reply)
    assert result["clauses"][1]["original_text"] == CLAUSES[1]["original_text"]


def test_audit_row_has_counts(monkeypatch, audit_rows):
    run(monkeypatch, good_reply())
    assert audit_rows[0][0:2] == ("j1", "2#risk-flagger")
    assert audit_rows[0][2]["high"] == 1 and audit_rows[0][2]["low"] == 1


def test_missing_clause_fails(monkeypatch, audit_rows):
    reply = good_reply()
    reply["clauses"].pop()
    with pytest.raises(ValueError):
        run(monkeypatch, reply)


def test_extra_clause_fails(monkeypatch, audit_rows):
    reply = good_reply()
    reply["clauses"].append({"clause_id": 99, "risk_level": "low", "category": "other", "reason": ""})
    with pytest.raises(ValueError):
        run(monkeypatch, reply)


def test_bad_risk_level_fails(monkeypatch, audit_rows):
    reply = good_reply()
    reply["clauses"][0]["risk_level"] = "scary"
    with pytest.raises(ValueError):
        run(monkeypatch, reply)


def test_bad_category_fails(monkeypatch, audit_rows):
    reply = good_reply()
    reply["clauses"][0]["category"] = "made-up"
    with pytest.raises(ValueError):
        run(monkeypatch, reply)


def test_high_risk_without_reason_fails(monkeypatch, audit_rows):
    reply = good_reply()
    reply["clauses"][1]["reason"] = ""
    with pytest.raises(ValueError):
        run(monkeypatch, reply)


def test_nothing_logged_when_validation_fails(monkeypatch, audit_rows):
    with pytest.raises(ValueError):
        run(monkeypatch, {"clauses": []})
    assert audit_rows == []
