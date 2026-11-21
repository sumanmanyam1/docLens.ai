# ADR-005: Prompt design per specialist

**Date**: 2026-11-20
**Status**: Accepted
**Deciders**: suman manyam
**Category**: Boundaries
**Reversibility**: Two-way

## Context

Three specialists call Claude via Bedrock converse(). The output must not invent content about the document (risk R2), must carry a not-legal-advice disclaimer, and must be easy to test locally.

## Decision

Each stage has its own focused system prompt and returns JSON.

Shared rules in every prompt:
- Use only the document's text; add no facts
- Say "unclear" instead of guessing
- Return valid JSON only, in the stated schema

Stages:
1. clause-extractor: input { text }; output { clauses: [{ clause_id, original_text }] }. Keeps original wording.
2. risk-flagger: input clauses; output adds { risk_level: low | medium | high, category, reason } per clause. Categories include auto-renewal, hidden fees, cancellation, liability, other.
3. plain-english-rewriter: output adds { plain_english } per clause, shown beside original_text, plus a disclaimer field: "This is a plain-language explanation, not legal advice."

Output validation: each stage parses the JSON and checks required fields; invalid output counts as a stage failure (triggers Retry).

## Options Considered

### Option 0: JSON between stages
- Pros: fixed fields; reliable hand-off; easy to test
- Cons: model may return invalid JSON, so validation is needed

### Option 1: Plain text between stages
- Pros: easier to read
- Cons: harder to test; easier to break between stages

## Consequences

### Positive
- Testable with exact fields; original clause shown beside explanation reduces misleading output

### Negative
- Needs JSON parsing and validation code

### Follow-up Actions
- [ ] Write the three prompts as separate files in each Lambda (suman)
- [ ] Test on a sample lease with known traps (suman)

## Review Trigger

Frequent invalid JSON or missed risky clauses in testing.

---

## Plain-Language Summary

**What we decided**: Three focused prompts, each returns a fixed structured result.
**What this means for the product**: Original clause beside plain-English version, with a risk flag and a disclaimer.
**What this costs**: A few cents per run.
**What we're giving up**: Free-form answers.
**What would trigger a change**: The AI missing obvious risky clauses in tests.
