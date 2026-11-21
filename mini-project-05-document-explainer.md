# Mini-Project Spec: Document-Explainer Pipeline

> **Week 6** · **Owner:** [student name]
> **Build budget:** 1–2 days
> **Deliverable:** A deployed AWS multi-agent pipeline that turns a pasted/uploaded lease or policy into a plain-English, clause-by-clause breakdown with flagged concerns.

---

## 1. Goal & User Outcome

**Who uses it:** Someone facing a dense legal/contract document (lease, insurance policy, terms of service) who wants it in plain language.

**What they get:** A clause-by-clause breakdown rewritten in plain English, with risky clauses (auto-renewal, hidden fees, cancellation traps) flagged.

**How they trigger it:**
- [x] Web form (API Gateway HTTP API → Lambda) — a paste box, or presigned upload for a text file *(Baseline front door)*
- [x] File dropped in S3 (presigned upload → S3 event) *(for larger documents)*
- [ ] Scheduled run — not applicable

**How they receive results:**
- [x] Rendered on the page (async — poll until the pipeline finishes)
- [x] Outbound email via SES (the finished breakdown)

---

## 2. Agent Design (Day 1 + Day 5)

This is the Day-5 multi-agent pattern deployed as a Day-6 Step Functions state machine (one Lambda per specialist, chained).

| Part | This project |
|------|--------------|
| **Brain** (LLM + system prompt) | Three specialists, each with a focused prompt (see below) |
| **Tools** (Hands) | Mostly LLM reasoning; `read_document` to load text from S3 |
| **Memory** (Notebook) | Each stage passes its output to the next via Step Functions state |
| **Skills** (Playbook) | Extract clauses → flag risks → rewrite in plain English |

**Single-agent or multi-agent?**
- [ ] Single agent
- [x] Orchestrator / pipeline (Step Functions, 1 Lambda per specialist) *(Day 5 — core to this project)*

**Pipeline stages:** `clause-extractor` → `risk-flagger` → `plain-english-rewriter`.

---

## 3. Tools (Days 2–3)

| Tool name | What it does | Real API or mock? | Input schema (fields) |
|-----------|--------------|-------------------|-----------------------|
| `read_document` | Load the document text from S3 (or accept pasted text) | S3 read / direct input | `s3_key: string` or `text: string` |
| `extract_clauses` | Split the document into discrete clauses | LLM-driven | `text: string` |
| `flag_risks` | Tag clauses with risk categories | LLM-driven | `clauses: array` |

> No external API; all reasoning is Bedrock-driven over the user's document.

---

## 4. Reliability & Guardrails (Day 4) — **Baseline, not optional**

- [x] **Max iterations** — each stage Lambda has a bounded agent loop.
- [x] **Error recovery** — Step Functions `Retry`/`Catch` on each stage; a failed stage escalates rather than silently dropping.
- [x] **Guardrails** — input: document length cap; output: no leaked secrets.
- [x] **Audit log** — each stage writes its decisions to DynamoDB keyed by job id.

**Project-specific guardrail rule:** The output must carry a clear "this is a plain-language explanation, not legal advice" disclaimer and must not state the document says something it does not.

---

## 5. AWS Architecture (Day 6) — **Baseline**

| Service | Used for | Baseline / Stretch |
|---------|----------|--------------------|
| **Lambda** | one per specialist (3) + a status Lambda | Baseline |
| **Bedrock** (`converse()`) | each specialist calls Claude | Baseline |
| **API Gateway (HTTP API)** | submit document + poll status | Baseline |
| **IAM** | Lambda roles: Bedrock + S3 + DynamoDB | Baseline |
| **CDK** | one-command deploy | Baseline |
| **DynamoDB** | job status + audit log | Baseline |
| **Step Functions** | chain the three specialists | **Baseline (this project)** |
| **S3** | receive uploaded documents + host `index.html` | Baseline |
| **SES** | email the finished breakdown | Baseline |
| **EventBridge** | — | Not used |

**Model ID:** `us.anthropic.claude-sonnet-4-6` · **Region:** `us-east-1`.

> **SES note:** sandbox mode — verify your own address for the demo.

---

## 6. Thin UI

**Form fields the user fills:** paste box (or file upload), email.

- [ ] **Sync:** not suitable — the pipeline exceeds the 29s API Gateway limit.
- [x] **Async:** submit starts Step Functions; page polls a status endpoint (status Lambda reads DynamoDB) and renders when done; email also sent.

> Unauthenticated demo; contract documents can be sensitive — state this is a demo only.

---

## 7. Exit Check

- [ ] Three specialist Lambdas, each with its own focused system prompt
- [ ] Step Functions chains extract → flag → rewrite with `Retry`/`Catch`
- [ ] All four Day-4 reliability patterns demonstrated
- [ ] "Not legal advice" + no-fabrication guardrail enforced
- [ ] `cdk deploy` stands up the whole stack (incl. state machine)
- [ ] Lambdas call Claude via Bedrock `converse()` (no API key in code)
- [ ] Submit → poll → breakdown renders; email arrives
- [ ] README with architecture diagram + deploy steps
- [ ] Code pushed to GitHub

---

## 8. Submission

- [ ] GitHub repo (CDK + 4 Lambdas + `index.html`)
- [ ] README as above
- [ ] Screenshot/recording of a rendered breakdown
- [ ] Audit log from one real run (all three stages)

---

*Infinitra Studio · Week 6 · Mini-Project Spec*
