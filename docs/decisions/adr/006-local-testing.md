# ADR-006: Local testing approach

**Date**: 2026-11-20
**Status**: Accepted
**Deciders**: suman manyam
**Category**: Build-Buy
**Reversibility**: Two-way

## Context

Local testing must pass before the first deploy. Bedrock runs only in AWS, so real calls need credentials and cost a few cents. A company account is used, so accidental real calls should be deliberate.

## Decision

Use both:
- pytest with mocked Bedrock responses for the main tests (free, fast, offline). Covers each Lambda's logic: input validation (empty, too long), JSON parsing, invalid-JSON failure, audit log writes (DynamoDB mocked), and the start/status Lambdas.
- One small script (run manually) that sends a sample fake lease through the real Bedrock converse() and prints the three-stage output, to check prompt quality before deploy.
- cdk synth to check the infrastructure code locally.

Real-Bedrock script is not part of the pytest run, so tests never call AWS by accident.

## Options Considered

### Option 0: Mocks only
- Pros: free, fast, offline
- Cons: does not show AI answer quality

### Option 1: Real Bedrock only
- Pros: shows real quality
- Cons: costs money, needs credentials, slow, flaky

### Option 2: Both
- Pros: fast checks plus a real-quality check
- Cons: a little more code

## Consequences

### Positive
- Bugs caught offline; real output available to show the guide

### Negative
- Mocks can drift from real model output

### Follow-up Actions
- [ ] Create a fake sample lease with known traps (auto-renewal, hidden fee, cancellation penalty) (suman)
- [ ] Write pytest tests with mocks (suman)
- [ ] Write the real-Bedrock script (suman)

## Review Trigger

Mock tests pass but real output breaks the JSON contract.

---

## Plain-Language Summary

**What we decided**: Test with fake AI answers for quick checks, and once with the real AI for quality.
**What this means for the product**: Fewer surprises at deploy time.
**What this costs**: A few cents.
**What we're giving up**: Nothing major.
**What would trigger a change**: Mocks stop matching real output.
