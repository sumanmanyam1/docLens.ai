"""Runs stage 1 -> 2 -> 3 in a row on the sample lease with fake AI replies.

This is a small preview of what Step Functions will do: each stage's output
becomes the next stage's input.
"""
import pytest

from agents.clause_extractor import handler as s1
from agents.plain_english_rewriter import handler as s3
from agents.risk_flagger import handler as s2

LEASE = """RESIDENTIAL LEASE AGREEMENT (FAKE TEST TEXT)

1. Term. This lease starts on January 1 and runs for twelve (12) months.

2. Automatic Renewal. Unless Tenant gives written notice at least ninety (90) days before the end of the term, this lease renews automatically for another twelve (12) months.

3. Rent. Tenant pays $1,500 per month, due on the first day of each month.
"""


def test_three_stages_in_a_row(monkeypatch):
    for stage in (s1, s2, s3):
        monkeypatch.setattr(stage, "write_audit", lambda job, name, summary: None)

    monkeypatch.setattr(s1, "call_model", lambda system, text: {"clauses": [
        {"clause_id": 1, "original_text": "2. Automatic Renewal. Unless Tenant gives written notice at least ninety (90) days before the end of the term"},
    ]})
    monkeypatch.setattr(s2, "call_model", lambda system, text: {"clauses": [
        {"clause_id": 1, "risk_level": "high", "category": "auto-renewal", "reason": "Renews unless you give 90 days' notice."},
    ]})
    monkeypatch.setattr(s3, "call_model", lambda system, text: {"clauses": [
        {"clause_id": 1, "plain_english": "The lease renews by itself unless you tell the landlord 90 days before it ends."},
    ]})

    data = {"job_id": "j1", "text": LEASE}
    data = s1.handler(data, None)
    data = s2.handler(data, None)
    data = s3.handler(data, None)

    clause = data["result"]["clauses"][0]
    assert clause["risk_level"] == "high"
    assert "90 days" in clause["plain_english"]
    assert "not legal advice" in data["result"]["disclaimer"]
