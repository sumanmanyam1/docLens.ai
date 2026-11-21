# ADR-003: Job start and polling API

**Date**: 2026-11-20
**Status**: Accepted
**Deciders**: suman manyam
**Category**: Integration
**Reversibility**: Two-way

## Context

The pipeline takes longer than the 29s API Gateway limit, so the flow is async: submit, then poll. Input is capped at 20,000 characters. Solo builder who needs a design that is easy to explain and test locally. The frontend is built separately and needs a clear API contract.

## Decision

API Gateway HTTP API with two routes, each backed by a Lambda:

- POST /jobs -> start Lambda: validates input (non-empty, max 20,000 chars), creates the job record in DynamoDB (status RUNNING), starts the Step Functions execution, returns { job_id }. Returns 400 with a clear message if input is invalid or too long.
- GET /jobs/{job_id} -> status Lambda: reads DynamoDB, returns { job_id, status: RUNNING | SUCCEEDED | FAILED, completed_stages: 0-3, result?, error? }. completed_stages is the number of audit_log rows for the job, so the page can show real progress. Returns 404 if the job is unknown.

Request body for POST /jobs: { "text": "..." }
CORS enabled so the frontend can call the API.

## Options Considered

### Option 0: Start Lambda behind API Gateway
- Pros: plain Python, easy to read, explain, and test locally; input validation in code
- Cons: one more Lambda

### Option 1: API Gateway direct to Step Functions
- Pros: less code
- Cons: logic hidden in API config; harder to test locally and to validate input

## Consequences

### Positive
- Simple, testable; clear contract for the frontend

### Negative
- One extra Lambda to maintain

### Follow-up Actions
- [ ] Unit test start Lambda (valid, empty, too long) locally (suman)
- [ ] Share the API contract with the frontend (suman)

## Review Trigger

Need for auth, rate limiting, or larger inputs.

---

## Plain-Language Summary

**What we decided**: The page sends the document to a small Lambda that checks it and starts the pipeline. The page then asks a second Lambda for the status.
**What this means for the product**: Clear submit-then-check flow.
**What this costs**: Nothing meaningful.
**What we're giving up**: A little less "no-code" simplicity.
**What would trigger a change**: Needing login or rate limits.
