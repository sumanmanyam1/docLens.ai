"""Stage 3: rewrite each clause in plain English and add the disclaimer (ADR-005).

Input : the output of stage 2 (clauses with risk fields).
Output: every clause also gets "plain_english", and the event gets a "result"
        holding the disclaimer and the finished clauses.

The AI only returns the plain-English text. We copy it onto the clauses, so the
original wording and the risk labels can never be changed by the AI.
The disclaimer comes from our code, not from the AI.
Before saving, any secrets (passwords, keys) are replaced with [REDACTED].
"""
import json
from pathlib import Path

from shared.memory import write_audit
from shared.llm import call_model
from shared.config import DISCLAIMER
from shared.guardrails import redact_clauses

STAGE_NAME = "3#plain-english-rewriter"

# The agent's instructions live in prompt.md next to this file, so you can read
# and change them without touching the code.
SYSTEM_PROMPT = (Path(__file__).parent / "prompt.md").read_text()


def validate_rewrites(reply, clauses):
    """Check the AI's reply against the clauses we sent. Raise ValueError if wrong.

    A raised error makes the stage fail, and Step Functions then retries it.
    Returns a dict that maps clause_id -> plain English text.
    """
    rewrites = reply.get("clauses") if isinstance(reply, dict) else None
    if not isinstance(rewrites, list):
        raise ValueError("reply must contain a 'clauses' list")

    # The AI must explain exactly the clauses we sent: none missing, none extra.
    expected_ids = [c["clause_id"] for c in clauses]
    got_ids = [r.get("clause_id") for r in rewrites if isinstance(r, dict)]
    if sorted(got_ids, key=str) != sorted(expected_ids, key=str):
        raise ValueError("reply must cover exactly the clauses we sent")

    for rewrite in rewrites:
        text = rewrite.get("plain_english")
        if not isinstance(text, str) or not text.strip():
            raise ValueError(f"clause {rewrite['clause_id']}: plain_english is required")

    return {r["clause_id"]: r["plain_english"].strip() for r in rewrites}


def handler(event, context):
    job_id = event["job_id"]
    clauses = event["clauses"]

    reply = call_model(SYSTEM_PROMPT, json.dumps({"clauses": clauses}))   # 1. ask the AI
    rewrites = validate_rewrites(reply, clauses)                          # 2. check its answer

    # 3. add the plain English to the clauses (everything else is untouched)
    finished = [{**c, "plain_english": rewrites[c["clause_id"]]} for c in clauses]

    # 4. guardrail: hide anything that looks like a password or key
    finished, secrets_hidden = redact_clauses(finished)

    write_audit(job_id, STAGE_NAME, {                                     # 5. record it
        "status": "ok",
        "clause_count": len(finished),
        "secrets_redacted": secrets_hidden,
    })

    # 6. the final result: what the page shows. The disclaimer is always added by us.
    result = {"disclaimer": DISCLAIMER, "clauses": finished}
    return {**event, "clauses": finished, "result": result}
