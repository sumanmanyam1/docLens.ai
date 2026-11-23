# Demo: a Step Functions stage fails and Catch fires

**Goal:** show that when an agent keeps failing, Step Functions retries it 3 times,
then **Catch** escalates: the job is saved as **FAILED** and the page shows an error
instead of waiting forever.

## How it works
- `backend/src/shared/fault_injection.py` is a **demo switch**. If a document contains
  `[[DEMO-FAIL:<agent>]]`, that agent raises `DemoFailure` before calling the AI.
- It only works when the Lambda setting `DEMO_FAULTS` is `on`. That is set for the
  3 agents in `backend/infra/settings.py`. Set it to `off` for real use and redeploy.
- The retry and catch rules are in `backend/infra/orchestrator.py`:
  `add_retry(max_attempts=3, interval=2 s, backoff_rate=2.0)` and `add_catch(save_failure)`.

## Before the demo (once)
The switch must be deployed: `./scripts/update.sh`.

## Steps
1. Open the website and attach **`test_docs/input/sample_demo_catch.txt`**. Click the arrow.
2. **On the page:** step 1 gets a tick, step 2 stays highlighted. After about 20 to 30 seconds
   the page returns to the form with *"The analysis failed. Please try again."*
3. **In the AWS console** (region N. Virginia): **Step Functions → State machines →
   `suman-doc-explainer-pipeline`** → open the newest execution (status **Failed**).
4. **Graph view:** "Extract clauses" is green, **"Flag risks" is red**, and the path continues to
   **"Save failure"** and **"Job failed"**. Point at this: *"That arrow is Catch."*
5. Click **"Flag risks"** → **Events / Step details:** 4 attempts with waits of 2, 4 and 8 seconds,
   error `DemoFailure`. Point at this: *"That is Retry with backoff."*
6. **DynamoDB → Tables → `suman-jobs` → Explore items:** the job has `status = FAILED`.
7. **DynamoDB → `suman-audit-log`:** only the `1#clause-extractor` row exists for this job.
   *"Agent 2 never finished, so it never wrote its row. That is also why the page showed one tick."*
8. (Optional) **CloudWatch → Log groups → `/aws/lambda/suman-risk-flagger`:** `DemoFailure` four times.

## What to say
> "If an agent keeps failing, Step Functions retries it three times with growing waits.
> If it still fails, Catch sends the job to a 'Save failure' step that marks it FAILED,
> so the user sees an error instead of a page that waits forever. Here I forced agent 2
> to fail with a demo switch that is only active when DEMO_FAULTS is on."

## Cost
Almost nothing: the failing agent stops before calling the AI. Only agent 1 calls Bedrock.

## Not covered yet
**Max-iterations escalation** needs the bounded agent loop, which is not built yet.
