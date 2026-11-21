# Project Brief: Document-Explainer Pipeline

**Date**: 2026-11-20 | **Author**: suman manyam | **Status**: Draft

## Problem

People facing dense legal documents (leases, insurance policies, terms of service) cannot tell what the document says or which clauses are risky (auto-renewal, hidden fees, cancellation traps).

## Target Users

Everyday people with no legal background. Any document type goes through one pipeline.

## Success Metrics

- Whole stack deploys with one `cdk deploy`
- A sample lease goes in; a plain-English, clause-by-clause breakdown with flagged risks comes out on the page
- Each stage writes an audit log to DynamoDB keyed by job id
- Every result carries a "not legal advice" disclaimer and does not claim the document says something it does not
- Lambdas pass local tests before the first deploy

## Scope

### In Scope (MVP)
- Paste text (file upload via S3 is optional)
- Step Functions pipeline: clause-extractor -> risk-flagger -> plain-english-rewriter (Lambda + Bedrock converse)
- Async submit, status polling, result rendered on the page (page-only MVP)
- Reliability: bounded loops, Retry/Catch, length cap, audit log
- Local testing (unit tests, optional mocked Bedrock, `cdk synth`) before deploy
- README with architecture diagram, deploy steps, GitHub push

### Optional (only if time remains)
- File upload via presigned S3 URL

### Out of Scope
- Email via SES (dropped by choice)
- Login/authentication (demo only)
- Lawyer-grade accuracy or professional users
- Scheduled runs
- Multiple languages

## Constraints

| Constraint | Value | Flexibility |
|-----------|-------|-------------|
| Budget | Low (student demo); budget not confirmed | Open |
| Timeline | 1-2 days build; demo to guide on Monday | Fixed |
| Team size | 1 (solo) | Fixed |
| Cloud / region | AWS us-east-1 | Fixed |
| Model | us.anthropic.claude-sonnet-4-6 via Bedrock | Fixed |
| IaC | AWS CDK | Fixed |

## Exit Check (acceptance criteria, from spec section 7)

- [ ] EC-1: Three specialist Lambdas, each with its own focused system prompt
- [ ] EC-2: Step Functions chains extract -> flag -> rewrite with Retry/Catch
- [ ] EC-3: All four Day-4 reliability patterns demonstrated (bounded loop, error recovery, guardrails, audit log)
- [ ] EC-4: "Not legal advice" disclaimer + no-fabrication guardrail enforced
- [ ] EC-5: `cdk deploy` stands up the whole stack, including the state machine
- [ ] EC-6: Lambdas call Claude via Bedrock `converse()` with no API key in code
- [ ] EC-7: Submit -> poll -> breakdown renders on page (no email)
- [ ] EC-8: README with architecture diagram and deploy steps
- [ ] EC-9: Code pushed to GitHub

## Submission Checklist

- [ ] GitHub repo (CDK + 4 Lambdas + `index.html`)
- [ ] README
- [ ] Screenshot/recording of a rendered breakdown
- [ ] Audit log from one real run (all three stages)

## Business Model

Learning/portfolio project. No revenue.

## Open Questions

- Exact budget ceiling for AWS/Bedrock costs
- Which AWS account will be used for deploy (needed before Ship)
- Document length cap value

## Next Step

Compliance & Data Landscape (Define section 2).
