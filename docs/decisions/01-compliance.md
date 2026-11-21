# Compliance & Data Landscape

**Date**: 2026-11-20 | **Author**: suman manyam | **Status**: Draft

## Context

Demo / showcase project for a guide review. Not released to the market. No real users.

## Regulations

- None apply (no GDPR, HIPAA, SOC2, PCI-DSS). No real personal or health data is processed.
- Compliance review: not needed (non-regulated demo project).

## Data

- Input: fake/sample documents only (e.g. a sample lease). No real personal documents.
- Stored in: S3 (uploads), DynamoDB (job status, audit log). AWS default encryption at rest.
- Region / residency: us-east-1, no residency requirement.

## Controls (engineering, not compliance)

- CR-1: Document length cap (guardrail)
- CR-2: No secrets in output (guardrail)
- CR-3: "Not legal advice" disclaimer on all output
- CR-4: Page notice: "Demo only. Do not upload real documents."
- CR-5: Per-stage audit log in DynamoDB keyed by job id
- CR-6: No API keys in code (Bedrock via IAM role)

## Retention

- Delete all resources with `cdk destroy` after the demo.

## Third Parties

- Amazon Bedrock (Claude).

## Open Questions

- None.
