# Answer key: Catch demo

Document: `sample_demo_catch.txt` (fake sample). It contains the marker
`[[DEMO-FAIL:risk_flagger]]`, which makes **agent 2 (risk flagger) fail on purpose**.

This is **not** a risk-rating test. It demonstrates Step Functions **Retry** and **Catch**.

## What you should see

| Where | Expected |
|---|---|
| Web page, progress steps | Step 1 "Splitting into clauses" ticked; step 2 "Flagging risks" highlighted |
| Web page, after about 20 to 30 seconds | Back to the form with the message **"The analysis failed. Please try again."** |
| Step Functions run (`suman-doc-explainer-pipeline`) | "Extract clauses" green → **"Flag risks" red** → "Save failure" → "Job failed". Status: **Failed** |
| "Flag risks" step details | **4 attempts** (1 + 3 retries), waits of 2 s, 4 s and 8 s, error `DemoFailure` |
| DynamoDB `suman-jobs` | `status = FAILED`, `error = "The analysis failed. Please try again."` |
| DynamoDB `suman-audit-log` | **Only 1 row** for this job: `1#clause-extractor` (agent 2 never finished) |
| CloudWatch logs `/aws/lambda/suman-risk-flagger` | `DemoFailure: Forced failure for demo in risk_flagger` four times |

## Pass if
- [ ] The job ends **FAILED** (the page did not wait forever)
- [ ] "Flag risks" shows **4 attempts**, then the run took the **Save failure** path
- [ ] The audit log has **only** the clause-extractor row

## Try the other agents
Change the marker in the document to fail a different stage:

| Marker | Fails | Steps ticked before the error |
|---|---|---|
| `[[DEMO-FAIL:clause_extractor]]` | agent 1 | 0 |
| `[[DEMO-FAIL:risk_flagger]]` | agent 2 | 1 |
| `[[DEMO-FAIL:plain_english_rewriter]]` | agent 3 | 2 |
