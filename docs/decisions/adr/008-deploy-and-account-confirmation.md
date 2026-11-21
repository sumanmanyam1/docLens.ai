# ADR-008: Deploy and account confirmation process

**Date**: 2026-11-20
**Status**: Accepted
**Deciders**: suman manyam
**Category**: Deployment
**Reversibility**: Two-way

## Context

Deploys go to a company AWS account. Local machine has several profiles, some for a personal root account, so deploying with default credentials could hit the wrong account. Local testing must pass first.

## Decision

- Approved target for environment "demo": account <ACCOUNT_ID>, profile <your-aws-profile> (SSO, AWSAdministratorAccess), region us-east-1.
- No deploy until local tests pass and cdk synth succeeds.
- Before any deploy or other state-changing AWS action: run aws sts get-caller-identity with the profile, compare the account to the recorded target, show the target block, and wait for an explicit "yes". Stop on mismatch.
- Never deploy with the default profile or ambient credentials.
- Currently: no deploys are allowed (user instruction). Read-only checks are fine.
- After the demo, run cdk destroy (with the same confirmation).

## Options Considered

### Option 0: Record the account and confirm before every deploy
- Pros: prevents wrong-account deploys
- Cons: one extra confirmation step

### Option 1: Use default credentials
- Pros: fewer steps
- Cons: default points to a personal root account; risky

## Consequences

### Positive
- Safe deploys; clear target

### Negative
- SSO login needed each session

### Follow-up Actions
- [ ] Enable Bedrock model access in us-east-1 for this account (suman) - not yet done
- [ ] Run cdk bootstrap only when deploy is allowed (suman)

## Review Trigger

Account changes, or deploys are approved.

---

## Plain-Language Summary

**What we decided**: Use the company account <ACCOUNT_ID> and always confirm before deploying.
**What this means for the product**: No accidental deploys to the wrong account.
**What this costs**: Nothing.
**What we're giving up**: A little speed.
**What would trigger a change**: Using a different account.
