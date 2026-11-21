# Risks & Assumptions

**Date**: 2026-11-20 | **Author**: suman manyam | **Status**: Draft

## Assumptions

- Company admin AWS account is approved for this project (account ID not yet recorded)
- Claude model access can be enabled in Bedrock us-east-1
- Only fake/sample documents are used
- Builder knows AWS, API Gateway, DynamoDB, S3; CDK and Step Functions are new

## Risks

| ID | Risk | Impact | Likelihood | Mitigation | Owner |
|---|---|---|---|---|---|
| R1 | AWS setup blockers (Bedrock access, IAM, bootstrap) | High | Medium | Enable Bedrock access first and test one converse() call; use CDK grants; confirm account with sts get-caller-identity | Suman |
| R2 | AI misreads or invents clause content | High | Medium | Prompts limited to document text; show original clause beside explanation; disclaimer; test on known sample lease | Suman |
| R3 | Not finishing in 1-2 days | High | Medium | Smallest working version first; local tests; deploy early; Lambdas, then Step Functions, then API and page | Suman |
| R4 | CDK and Step Functions are new | Medium | High | Learn on small pieces; cdk synth to check; start with a minimal state machine | Suman |

## Riskiest Bet

CDK and Step Functions are both new, and they carry the most work. Test cheaply by deploying a minimal one-step state machine early.

## Open Questions

- AWS account ID for the deploy confirmation gate
