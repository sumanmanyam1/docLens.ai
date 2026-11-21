"""Tests for stage 3. The AI call and the audit log are faked, so no AWS is used."""
import pytest

from agents.plain_english_rewriter import handler as stage

CLAUSES = [
    {"clause_id": 1, "original_text": "Term. Twelve months.", "risk_level": "low", "category": "other", "reason": ""},
    {"clause_id": 2, "original_text": "Automatic Renewal. Renews unless notice 90 days before.",
     "risk_level": "high", "category": "auto-renewal", "reason": "Renews for a year."},
]


def good_reply():
    return {"clauses": [
        {"clause_id": 1, "plain_english": "The lease lasts 12 months."},
        {"clause_id": 2, "plain_english": "It renews by itself unless you give notice 90 days before it ends."},
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


def test_good_reply_adds_plain_english(monkeypatch, audit_rows):
    result = run(monkeypatch, good_reply())
    assert result["clauses"][0]["plain_english"] == "The lease lasts 12 months."
    assert result["job_id"] == "j1"


def test_result_has_disclaimer_and_clauses(monkeypatch, audit_rows):
    result = run(monkeypatch, good_reply())["result"]
    assert "not legal advice" in result["disclaimer"]
    assert len(result["clauses"]) == 2


def test_disclaimer_comes_from_code_not_ai(monkeypatch, audit_rows):
    reply = good_reply()
    reply["disclaimer"] = "This is great legal advice!"   # the AI must not be able to set it
    result = run(monkeypatch, reply)["result"]
    assert "not legal advice" in result["disclaimer"]


def test_original_text_and_risk_are_not_changed(monkeypatch, audit_rows):
    reply = good_reply()
    reply["clauses"][1]["original_text"] = "AI rewrote this"
    reply["clauses"][1]["risk_level"] = "low"
    clause = run(monkeypatch, reply)["clauses"][1]
    assert clause["original_text"] == CLAUSES[1]["original_text"]
    assert clause["risk_level"] == "high"


def test_audit_row_is_written(monkeypatch, audit_rows):
    run(monkeypatch, good_reply())
    assert audit_rows[0][0:2] == ("j1", "3#plain-english-rewriter")
    assert audit_rows[0][2]["clause_count"] == 2


def test_missing_clause_fails(monkeypatch, audit_rows):
    reply = good_reply()
    reply["clauses"].pop()
    with pytest.raises(ValueError):
        run(monkeypatch, reply)


def test_extra_clause_fails(monkeypatch, audit_rows):
    reply = good_reply()
    reply["clauses"].append({"clause_id": 99, "plain_english": "Invented clause."})
    with pytest.raises(ValueError):
        run(monkeypatch, reply)


def test_empty_plain_english_fails(monkeypatch, audit_rows):
    reply = good_reply()
    reply["clauses"][0]["plain_english"] = "   "
    with pytest.raises(ValueError):
        run(monkeypatch, reply)


def test_nothing_logged_when_validation_fails(monkeypatch, audit_rows):
    with pytest.raises(ValueError):
        run(monkeypatch, {"clauses": []})
    assert audit_rows == []


def test_secrets_are_redacted_in_the_result(monkeypatch, audit_rows):
    clauses = [{"clause_id": 1, "original_text": "Door code password: 9921xyz.",
                "risk_level": "low", "category": "other", "reason": ""}]
    monkeypatch.setattr(stage, "call_model", lambda s, t: {"clauses": [
        {"clause_id": 1, "plain_english": "The door password: 9921xyz opens the door."}]})
    result = stage.handler({"job_id": "j1", "clauses": clauses}, None)["result"]
    assert "9921xyz" not in result["clauses"][0]["original_text"]
    assert "9921xyz" not in result["clauses"][0]["plain_english"]
    assert audit_rows[0][2]["secrets_redacted"] == 2
