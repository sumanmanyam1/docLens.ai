# Document-Explainer Pipeline (backend)

The main README, with the architecture diagram and full deploy steps, is `../README.md`.

Turns a lease or policy into a plain-English, clause-by-clause breakdown with flagged risks.
Flow: paste text -> Step Functions (3 Python Lambdas + Bedrock) -> poll -> result.

Decisions: see `../docs/decisions/` (ADR-001 to ADR-006, ADR-008).

Architecture diagram: open `../docs/architecture.html` in a browser.

## Layout (this folder is `backend/`)
- `src/`      Lambda code: `agents/` (3 AI agents, each with a `prompt.md`), `api/`, `shared/`
- `infra/`    CDK recipe, one file per part; entry point is `app.py`
- `tests/`    pytest with mocks (free, no AWS login), same shape as `src/`
- sample documents for manual testing: `../test_docs/input/`, answers in `../test_docs/result/`

The web page lives in `../frontend/`.

## Run locally (no AWS needed). Run these from inside `backend/`
```
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
pytest
source deploy.env && python app.py   # builds the template only; nothing is deployed
```

## Deploy
See `../README.md` (Deploy section).
