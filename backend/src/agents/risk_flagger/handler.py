"""Stage 2: tag each clause as low / medium / high risk (ADR-005).

Input : the output of stage 1, with "clauses": [{"clause_id", "original_text"}]
Output: every clause also gets "risk_level", "category" and "reason".

The AI only returns the risk labels. We copy them onto the clauses from
stage 1, so the AI can never change the original wording.
"""
import json
from pathlib import Path

from shared.fault_injection import maybe_fail
from shared.memory import write_audit
from shared.llm import call_model

STAGE_NAME = "2#risk-flagger"

RISK_LEVELS = ["low", "medium", "high"]
CATEGORIES = ["auto-renewal", "hidden fees", "cancellation", "liability", "other"]

# The agent's instructions live in prompt.md next to this file, so you can read
# and change them without touching the code.
SYSTEM_PROMPT = (Path(__file__).parent / "prompt.md").read_text()


def validate_flags(reply, clauses):
    """Check the AI's reply against the clauses we sent. Raise ValueError if wrong.

    A raised error makes the stage fail, and Step Functions then retries it.
    Returns a dict that maps clause_id -> the flag for that clause.
    """
    flags = reply.get("clauses") if isinstance(reply, dict) else None
    if not isinstance(flags, list):
        raise ValueError("reply must contain a 'clauses' list")

    # The AI must judge exactly the clauses we sent: none missing, none extra.
    expected_ids = [c["clause_id"] for c in clauses]
    got_ids = [f.get("clause_id") for f in flags if isinstance(f, dict)]
    if sorted(got_ids, key=str) != sorted(expected_ids, key=str):
        raise ValueError("reply must cover exactly the clauses we sent")

    for flag in flags:
        if flag.get("risk_level") not in RISK_LEVELS:
            raise ValueError(f"clause {flag['clause_id']}: bad risk_level")
        if flag.get("category") not in CATEGORIES:
            raise ValueError(f"clause {flag['clause_id']}: bad category")
        needs_reason = flag["risk_level"] in ("medium", "high")
        if needs_reason and not str(flag.get("reason", "")).strip():
            raise ValueError(f"clause {flag['clause_id']}: reason is required")

    return {f["clause_id"]: f for f in flags}


def handler(event, context):
    job_id = event["job_id"]
    clauses = event["clauses"]
    maybe_fail("risk_flagger", event.get("text", ""))  # demo switch: fail on purpose if asked

    reply = call_model(SYSTEM_PROMPT, json.dumps({"clauses": clauses}))   # 1. ask the AI
    flags = validate_flags(reply, clauses)                                # 2. check its answer

    # 3. add the risk labels to the clauses from stage 1 (original text is untouched)
    flagged = []
    for clause in clauses:
        flag = flags[clause["clause_id"]]
        flagged.append({
            **clause,
            "risk_level": flag["risk_level"],
            "category": flag["category"],
            "reason": flag.get("reason", ""),
        })

    counts = {level: sum(1 for c in flagged if c["risk_level"] == level) for level in RISK_LEVELS}
    write_audit(job_id, STAGE_NAME, {"status": "ok", **counts})           # 4. record what we did
    return {**event, "clauses": flagged}                                  # 5. pass the result on
