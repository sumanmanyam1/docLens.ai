# ADR-004: DynamoDB design

**Date**: 2026-11-20
**Status**: Accepted
**Deciders**: suman manyam
**Category**: Data
**Reversibility**: Two-way

## Context

Need job status for polling and a per-stage audit log keyed by job id. Demo scale, one user at a time. Must be easy to explain. Resources must be removable with cdk destroy.

## Decision

Two DynamoDB tables, both on-demand billing, removal policy DESTROY:

- jobs table: partition key job_id (string). Attributes: status (RUNNING | SUCCEEDED | FAILED), created_at, result, error.
- audit_log table: partition key job_id (string), sort key stage (string, e.g. "1#clause-extractor"). Attributes: timestamp, input_summary, output_summary, decisions, status.

Query audit_log by job_id returns the full run history.

## Options Considered

### Option 0: Two tables
- Pros: each table has one clear purpose; easy to explain
- Cons: two resources and two sets of permissions

### Option 1: One table with row types
- Pros: one resource
- Cons: mixed row types are harder to explain

## Consequences

### Positive
- Simple mental model; audit log is a clean query for the submission

### Negative
- Slightly more CDK code

### Follow-up Actions
- [ ] Grant start and status Lambdas access to jobs; grant stage Lambdas access to audit_log and jobs (suman)

## Review Trigger

Need for queries across jobs or retention rules.

---

## Plain-Language Summary

**What we decided**: One table for job status, one table for the step-by-step log.
**What this means for the product**: Clear status for the page and a proof log for each run.
**What this costs**: Pennies at demo scale.
**What we're giving up**: A single-table design.
**What would trigger a change**: Needing reports across many jobs.
