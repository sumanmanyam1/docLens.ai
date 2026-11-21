"""CDK entry point. `python app.py` builds a template locally; it does NOT deploy.

The approved account is NOT written in the code, so it never ends up on GitHub.
Set it in backend/deploy.env (kept out of git), then run `source deploy.env`.
CDK will only target that account (ADR-008).
"""
import os
import sys

import aws_cdk as cdk

from infra.stack import DocExplainerStack

APPROVED_ACCOUNT = os.environ.get("APPROVED_ACCOUNT", "").strip()
REGION = "us-east-1"

if not APPROVED_ACCOUNT.isdigit() or len(APPROVED_ACCOUNT) != 12:
    sys.exit("APPROVED_ACCOUNT is not set. Run `source deploy.env` first (see deploy.env.example).")

app = cdk.App()
DocExplainerStack(
    app, "suman-doc-explainer",
    env=cdk.Environment(account=APPROVED_ACCOUNT, region=REGION),
)
app.synth()
