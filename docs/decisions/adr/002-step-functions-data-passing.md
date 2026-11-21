# ADR-002: Step Functions data passing

**Date**: 2026-11-20
**Status**: Accepted
**Deciders**: suman manyam
**Category**: Integration
**Reversibility**: Two-way

## Context

Three stages (clause-extractor, risk-flagger, plain-english-rewriter) run in order. Input is capped at 20,000 characters, so payloads stay far below the Step Functions 256 KB limit. DynamoDB is still used for job status and the audit log.

## Decision

Pass data between stages through the state machine. Each stage's output becomes the next stage's input. The state carries job_id, text, clauses, risks, and the final explanation. Each stage also writes its decisions to the DynamoDB audit log.

## Options Considered

### Option 0: Pass through the state machine
- Pros: simple; less code; easy to see in the execution view
- Cons: limited to 256 KB payload

### Option 1: Pass only job_id, store data in DynamoDB
- Pros: no payload limit
- Cons: more reads and writes; more code

## Consequences

### Positive
- Less code; each stage is a pure function of its input

### Negative
- Larger documents would need option 1

### Follow-up Actions
- [ ] Enforce the 20,000-character cap at submit time (suman)

## Review Trigger

Input cap is raised above what fits in a 256 KB payload.

---

## Plain-Language Summary

**What we decided**: Each step hands its result straight to the next step.
**What this means for the product**: Simple and easy to follow.
**What this costs**: Nothing extra.
**What we're giving up**: Very large documents.
**What would trigger a change**: Raising the size limit a lot.
