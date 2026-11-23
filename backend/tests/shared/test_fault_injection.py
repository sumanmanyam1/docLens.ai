"""Tests for the demo switch that makes an agent fail on purpose."""
import pytest

from shared.fault_injection import DemoFailure, maybe_fail

DOC = "1. Rent. Tenant pays $1,500.\n\n[[DEMO-FAIL:risk_flagger]]"


def test_switch_off_ignores_the_marker(monkeypatch):
    monkeypatch.delenv("DEMO_FAULTS", raising=False)
    maybe_fail("risk_flagger", DOC)             # no error


def test_switch_on_and_marker_fails_that_agent(monkeypatch):
    monkeypatch.setenv("DEMO_FAULTS", "on")
    with pytest.raises(DemoFailure):
        maybe_fail("risk_flagger", DOC)


def test_other_agents_are_not_affected(monkeypatch):
    monkeypatch.setenv("DEMO_FAULTS", "on")
    maybe_fail("clause_extractor", DOC)         # no error
    maybe_fail("plain_english_rewriter", DOC)   # no error


def test_document_without_marker_works(monkeypatch):
    monkeypatch.setenv("DEMO_FAULTS", "on")
    maybe_fail("risk_flagger", "1. Rent. Tenant pays $1,500.")


def test_agent_fails_before_calling_the_ai(monkeypatch):
    """The forced failure happens first, so a demo failure costs no AI call."""
    from agents.risk_flagger import handler as stage
    monkeypatch.setenv("DEMO_FAULTS", "on")
    def no_ai(*args):
        raise AssertionError("the AI must not be called")
    monkeypatch.setattr(stage, "call_model", no_ai)
    monkeypatch.setattr(stage, "write_audit", lambda *a: None)
    with pytest.raises(DemoFailure):
        stage.handler({"job_id": "j1", "text": DOC, "clauses": [{"clause_id": 1, "original_text": "1. Rent."}]}, None)
