"""Tests for the output guardrail that hides secrets."""
from shared.guardrails import REDACTED, redact_clauses, redact_text


def test_normal_text_is_unchanged():
    text = "Tenant pays $1,500 per month, due on the first day."
    assert redact_text(text) == (text, 0)


def test_aws_access_key_is_hidden():
    clean, n = redact_text("Use key AKIAIOSFODNN7EXAMPLE to log in.")
    assert "AKIA" not in clean and n == 1


def test_password_value_is_hidden_but_label_kept():
    clean, n = redact_text("The wifi password: hunter2abc is on the fridge.")
    assert clean == f"The wifi password: {REDACTED} is on the fridge." and n == 1


def test_api_key_is_hidden():
    clean, n = redact_text("token sk-abcdefghijklmnopqrstuvwxyz123456")
    assert "sk-abc" not in clean and n == 1


def test_private_key_block_is_hidden():
    block = "-----BEGIN RSA PRIVATE KEY-----\nMIIEow\n-----END RSA PRIVATE KEY-----"
    clean, n = redact_text(f"Key: {block} end")
    assert "MIIEow" not in clean and n >= 1


def test_redact_clauses_checks_all_fields_and_copies():
    clauses = [{"clause_id": 1, "original_text": "password: abc123",
                "plain_english": "Your password is abc123.", "reason": ""}]
    clean, n = redact_clauses(clauses)
    assert "abc123" not in clean[0]["original_text"]
    assert clauses[0]["original_text"] == "password: abc123"   # caller's data unchanged
    assert n == 1   # "password is abc123" has no ':' or '=', so only the labelled one counts


def test_non_text_fields_are_left_alone():
    assert redact_text(None) == (None, 0)
