# Build Readiness: Document-Explainer Pipeline

**Decisions completed**: 7 (ADR-001 to ADR-006, ADR-008)
**Decisions deferred**: D7 frontend (built by the owner in frontend/)

## Architecture at a Glance
- **Compute**: Python 3.12 Lambdas: clause-extractor, risk-flagger, plain-english-rewriter, start, status
- **Orchestration**: Step Functions chains the three stages with Retry (3) and Catch; data passes through the state machine
- **Data**: DynamoDB tables jobs and audit_log, on-demand, removable
- **API**: API Gateway HTTP API: POST /jobs, GET /jobs/{job_id}, CORS on
- **AI**: Bedrock converse() with us.anthropic.claude-sonnet-4-6, JSON output per stage
- **Deployment**: CDK (Python), us-east-1, company account <ACCOUNT_ID> via SSO profile, confirmation gate before every deploy

## Build Constraints
- Input cap 20,000 characters; result target under 2 minutes
- Every result carries the not-legal-advice disclaimer; prompts use only the document's text
- No API keys in code; least-privilege IAM via CDK grants
- Local tests must pass and cdk synth must succeed before any deploy
- NO DEPLOYS until the owner says so

## Known Risks Entering Build
- R1 AWS setup: Bedrock model access not yet confirmed in the account
- R2 AI misreading clauses: test on fake lease with known traps
- R3 Time: 1-2 days; Monday demo
- R4 CDK and Step Functions are new to the builder

## Recommended Build Order
1. Fake sample lease; three stage Lambdas with mocked pytest tests
2. Start and status Lambdas with tests
3. CDK stack (tables, Lambdas, state machine, API); verify with cdk synth
4. Real-Bedrock script for output quality
5. Deploy only on owner approval, after the confirmation gate
6. README with architecture diagram; screenshot and audit log from one run
