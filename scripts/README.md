# Deploy scripts

Three scripts that run the CDK commands for you, safely and in the right order.
The CDK recipe itself is in `backend/infra/` and `backend/app.py`; these scripts only drive it.

Run them from the project's top folder:

| Script | When to use it | What it does |
|---|---|---|
| `./scripts/deploy.sh` | **First time only**, when the stack does not exist yet | checks → tests → `cdk bootstrap` if needed → `cdk deploy` → prints the addresses |
| `./scripts/update.sh` | **After you change code or the web page** | checks → tests → `cdk diff` (preview) → asks you → `cdk deploy` |
| `./scripts/destroy.sh` | **When you are done** (after the demo) | checks → lists what will be deleted → you type the stack name → `cdk destroy` |

## Checks every script does first
1. Loads `backend/.venv` and `backend/deploy.env` (stops if either is missing).
2. Checks the network is fast enough for CDK (stops if an AWS lookup takes over 5 seconds).
3. Checks you are logged in to the account in `deploy.env` (stops if the login expired or the account is different).
4. `deploy.sh` and `update.sh` also run all the tests and stop if any fail.

Nothing in AWS changes until you answer `y` (or, for destroy, type the stack name).

## Before the first run
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp deploy.env.example deploy.env        # then fill in your account and profile
aws sso login --profile <your-profile>  # if you use SSO
```

## If a script stops
| Message | Fix |
|---|---|
| `backend/deploy.env is missing` | `cp backend/deploy.env.example backend/deploy.env` and fill it in |
| `not logged in, or the login has expired` | `aws sso login --profile <your-profile>` |
| `Looking up AWS took ... ms` | use your phone's hotspot, or set DNS to 8.8.8.8 and 1.1.1.1 |
| `logged in to account ...` (wrong account) | log in to the right account, or fix `deploy.env` |
| `Some tests failed` | run `cd backend && pytest` and fix the failing test |
| `The stack ... already exists` | use `update.sh` instead of `deploy.sh` |
| `The stack is busy` | wait a few minutes, then try again |

## After destroy
- Lambda log groups (`/aws/lambda/suman-...`) stay, because AWS creates them, not CDK. The script lists them and shows how to delete them.
- `CDKToolkit` stays on purpose. It is shared by the whole account.
- CloudFront takes 5 to 15 minutes to delete. That is normal.
