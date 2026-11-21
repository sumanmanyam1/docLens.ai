# Decision Backlog

**Date**: 2026-11-20 | **Author**: suman manyam | **Status**: Draft

| # | Decision | Category | Priority | Reversibility | Led by | Blocked by |
|---|---|---|---|---|---|---|
| D1 | Language and tooling: Python for Lambdas and CDK, pytest for local tests | Build-Buy | High | Two-way | Suman | none |
| D2 | Step Functions data passing between the 3 stages | Integration | High | Two-way | Suman | D1 |
| D3 | Job start and polling: API Gateway routes and Lambdas (submit, status) | Integration | High | Two-way | Suman | D1 |
| D4 | DynamoDB design for job status and audit log | Data | Medium | Two-way | Suman | D2 |
| D5 | Prompt design per specialist, with no-invention and disclaimer rules | Boundaries | High | Two-way | Suman | D2 |
| D6 | Local testing: real Bedrock calls or mocked responses | Build-Buy | Medium | Two-way | Suman | D1 |
| D7 | Frontend: handled by the builder outside Compass (deferred). Backend only needs a clear API contract (see D3) | Deployment | Low | Two-way | Suman | D3 |
| D8 | Deploy and account confirmation process (company account) | Deployment | Medium | Two-way | Suman | none |

## Review

Approvers: mentor and company reviewer (both must agree on project acceptance).

## Open Questions

- AWS account ID for the deploy confirmation gate
