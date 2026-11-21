"""Tests for the LLM helper (shared/llm.py). boto3 is faked, so no AWS is used."""
import pytest

from shared import llm


class FakeClient:
    """Pretends to be the Bedrock client and returns a ready-made reply."""
    def __init__(self, reply_text):
        self.reply_text = reply_text

    def converse(self, **kwargs):
        return {"output": {"message": {"content": [{"text": self.reply_text}]}}}


def ask(monkeypatch, reply_text):
    monkeypatch.setattr(llm.boto3, "client", lambda *a, **k: FakeClient(reply_text))
    return llm.call_model("system", "user")


def test_plain_json_is_parsed(monkeypatch):
    assert ask(monkeypatch, '{"clauses": []}') == {"clauses": []}


def test_json_wrapped_in_code_fences_is_parsed(monkeypatch):
    assert ask(monkeypatch, '```json\n{"clauses": []}\n```') == {"clauses": []}


def test_plain_fences_without_label_are_parsed(monkeypatch):
    assert ask(monkeypatch, '```\n{"a": 1}\n```') == {"a": 1}


def test_invalid_json_still_fails(monkeypatch):
    with pytest.raises(ValueError):          # json.JSONDecodeError is a ValueError
        ask(monkeypatch, "Sorry, I cannot do that.")
