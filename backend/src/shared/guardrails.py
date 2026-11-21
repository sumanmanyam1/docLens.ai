"""Output guardrail: hide secrets before anything is shown to the user (spec section 4).

A document might contain things like passwords or access keys, and the AI might
copy them into its answer. Before the result is saved, we replace anything that
looks like a secret with "[REDACTED]".

This is a simple pattern check. It catches common formats, not every possible secret.
"""
import re

REDACTED = "[REDACTED]"

# Each pattern describes one kind of secret. The names are only for the audit log.
SECRET_PATTERNS = {
    # AWS access key id, e.g. AKIAIOSFODNN7EXAMPLE
    "aws_access_key": re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    # A private key block (-----BEGIN ... PRIVATE KEY----- ... -----END ...-----)
    "private_key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.S),
    # Common API key formats, e.g. sk-..., ghp_..., xoxb-...
    "api_key": re.compile(r"\b(?:sk-[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{30,}|xox[abp]-[A-Za-z0-9-]{10,})\b"),
    # "password: hunter2", "secret = abc123", "api key: xyz" -> keep the label, hide the value
    "labelled_secret": re.compile(
        r"(?i)\b(password|passwd|pwd|secret|api[ _-]?key|access[ _-]?key|token)(\s*[:=]\s*)(\S+)"),
}


def redact_text(text):
    """Return (clean_text, number_of_secrets_hidden)."""
    if not isinstance(text, str):
        return text, 0
    hidden = 0
    for name, pattern in SECRET_PATTERNS.items():
        if name == "labelled_secret":
            # Keep "password: " so the reader understands, hide only the value.
            text, n = pattern.subn(lambda m: m.group(1) + m.group(2) + REDACTED, text)
        else:
            text, n = pattern.subn(REDACTED, text)
        hidden += n
    return text, hidden


def redact_clauses(clauses, fields=("original_text", "plain_english", "reason")):
    """Hide secrets in the given fields of every clause. Return (clean_clauses, total_hidden)."""
    clean, total = [], 0
    for clause in clauses:
        clause = dict(clause)          # copy, so we never change the caller's data
        for field in fields:
            clause[field], n = redact_text(clause.get(field))
            total += n
        clean.append(clause)
    return clean, total
