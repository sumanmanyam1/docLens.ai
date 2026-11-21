# Project Directory Structure

Project files come first in each folder. Helper items (local only, not on GitHub) are listed last and marked *(local)*.

```text
doc_exp_pip_lne/
├── backend/
│   ├── infra/                          CDK recipe, one file per part
│   │   ├── agents.py                   the 5 Lambdas + permissions
│   │   ├── api.py                      API Gateway (POST /jobs, GET /jobs/{job_id})
│   │   ├── orchestrator.py             Step Functions with Retry and Catch
│   │   ├── settings.py                 prefix, model, folders
│   │   ├── stack.py                    joins the parts together
│   │   ├── storage.py                  DynamoDB tables (memory)
│   │   └── website.py                  S3 + CloudFront
│   ├── src/                            code that runs on AWS
│   │   ├── agents/                     the 3 AI specialists
│   │   │   ├── clause_extractor/
│   │   │   │   ├── handler.py
│   │   │   │   └── prompt.md
│   │   │   ├── plain_english_rewriter/
│   │   │   │   ├── handler.py
│   │   │   │   └── prompt.md
│   │   │   └── risk_flagger/
│   │   │       ├── handler.py
│   │   │       └── prompt.md
│   │   ├── api/                        the front desk
│   │   │   ├── get_status/
│   │   │   │   └── handler.py
│   │   │   └── start_job/
│   │   │       └── handler.py
│   │   └── shared/                     tools every agent uses
│   │       ├── config.py
│   │       ├── guardrails.py
│   │       ├── llm.py
│   │       └── memory.py
│   ├── tests/                          same shape as src/
│   │   ├── agents/
│   │   │   ├── test_clause_extractor.py
│   │   │   ├── test_pipeline_chain.py
│   │   │   ├── test_plain_english_rewriter.py
│   │   │   ├── test_prompts.py
│   │   │   └── test_risk_flagger.py
│   │   ├── api/
│   │   │   ├── test_get_status.py
│   │   │   └── test_start_job.py
│   │   ├── infra/
│   │   │   └── test_stack.py
│   │   ├── shared/
│   │   │   ├── test_guardrails.py
│   │   │   └── test_llm.py
│   │   └── conftest.py
│   ├── app.py                          CDK entry point
│   ├── cdk.json
│   ├── deploy.env.example              copy to deploy.env and fill in
│   ├── pytest.ini
│   ├── README.md
│   ├── requirements-dev.txt
│   ├── requirements.txt
│   ├── .gitignore
│   ├── deploy.env                      (local) your account settings
│   ├── .pytest_cache/                  (local) test leftovers
│   ├── .venv/                          (local) Python packages
│   └── cdk.out/                        (local) built template
├── docs/
│   ├── decisions/                      project brief, risks, ADRs
│   ├── architecture.html
│   └── audit-log-sample.json           audit log from one real run
├── frontend/
│   ├── index.html                      the web page
│   └── .gitkeep
├── test_docs/
│   ├── input/                          fake documents to upload
│   └── result/                         ans_ answer keys (never upload)
├── doc_exp_pip_lne-structure.md        this file
├── mini-project-05-document-explainer.md
├── README.md
├── .gitignore
└── .compass/                           (local) project notes
    ├── config.yml
    ├── context.json
    └── state.json
```
