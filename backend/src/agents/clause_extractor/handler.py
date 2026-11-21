"""Stage 1: split the document into numbered clauses (ADR-005).

Input : {"job_id": ..., "text": ...}
Output: the same data plus
        "clauses": [{"clause_id": 1, "original_text": "..."}, ...]

Steps: ask the AI -> check its answer -> write an audit row -> pass it on.
"""
from pathlib import Path

from shared.memory import write_audit
from shared.llm import call_model

STAGE_NAME = "1#clause-extractor"

# The agent's instructions live in prompt.md next to this file, so you can read
# and change them without touching the code.
SYSTEM_PROMPT = (Path(__file__).parent / "prompt.md").read_text()


def _squash(text):
    """Collapse all whitespace so we can compare texts fairly."""
    return " ".join(text.split())


def validate_clauses(reply, document_text):
    """Check the AI's reply. Raise ValueError if anything looks wrong.

    A raised error makes the stage fail, and Step Functions then retries it.
    """
    clauses = reply.get("clauses") if isinstance(reply, dict) else None
    if not isinstance(clauses, list) or not clauses:
        raise ValueError("reply must contain a non-empty 'clauses' list")

    document = _squash(document_text)
    for clause in clauses:
        if "clause_id" not in clause or "original_text" not in clause:
            raise ValueError("each clause needs 'clause_id' and 'original_text'")
        # Guard against made-up text: every clause must really be in the document.
        if _squash(clause["original_text"]) not in document:
            raise ValueError(f"clause {clause['clause_id']} is not found in the document")
    return clauses


def handler(event, context):
    # AWS calls this function. "event" is the input from Step Functions.
    job_id = event["job_id"]
    text = event["text"]

    reply = call_model(SYSTEM_PROMPT, text)         # 1. ask the AI
    clauses = validate_clauses(reply, text)         # 2. check its answer

    write_audit(job_id, STAGE_NAME, {               # 3. record what we did
        "status": "ok",
        "clause_count": len(clauses),
    })
    return {**event, "clauses": clauses}            # 4. pass the result on
