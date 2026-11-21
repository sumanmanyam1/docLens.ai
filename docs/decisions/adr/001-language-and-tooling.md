# ADR-001: Language and tooling

**Date**: 2026-11-20
**Status**: Accepted
**Deciders**: suman manyam
**Category**: Build-Buy
**Reversibility**: Two-way

## Context

Solo builder, 1-2 day build, demo on Monday. Knows AWS, API Gateway, DynamoDB, S3. CDK and Step Functions are new. Lambdas call Bedrock converse(). Local testing before deploy is required. The frontend is handled by the builder separately and is out of scope here.

## Decision

- Python 3.12 for the Lambdas and for CDK
- boto3 for AWS and Bedrock calls
- pytest for local tests

## Options Considered

### Option 0: Python
- Pros: easy to read and explain; one language for Lambdas and CDK; simple boto3 Bedrock call; quick pytest tests
- Cons: CDK examples are more common in TypeScript

### Option 1: TypeScript
- Pros: most common CDK choice; typed
- Cons: more setup and type definitions; slower for a 1-2 day build

## Consequences

### Positive
- Less to learn; faster local testing; easy to explain

### Negative
- Fewer CDK examples online than TypeScript

### Follow-up Actions
- [ ] Confirm python3.12 runtime is available for Lambda (suman)
- [ ] Set up pytest project layout (suman)

## Review Trigger

Python 3.12 is unavailable as a Lambda runtime, or CDK in Python proves too hard.

---

## Plain-Language Summary

**What we decided**: Build the backend and infrastructure in Python.
**What this means for the product**: Same language everywhere, easy to explain.
**What this costs**: Nothing extra.
**What we're giving up**: The larger pool of TypeScript CDK examples.
**What would trigger a change**: Runtime unavailable or CDK Python too hard.
