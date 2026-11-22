#!/usr/bin/env bash
# Shared helpers for deploy.sh, update.sh and destroy.sh.
# You do not run this file yourself; the other scripts load it.

set -euo pipefail          # stop at the first error, and treat unset variables as errors

STACK="suman-doc-explainer"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND="$ROOT/backend"

# ---------- pretty messages ----------
step() { printf "\n\033[1m==> %s\033[0m\n" "$*"; }
ok()   { printf "    \033[32mOK\033[0m  %s\n" "$*"; }
warn() { printf "    \033[33m!!\033[0m  %s\n" "$*"; }
fail() { printf "\n\033[31mSTOPPED:\033[0m %s\n" "$*" >&2; exit 1; }

ask_yes() {
  # ask_yes "Question?"  -> continues only if the answer is y or yes
  local answer
  read -r -p "    $1 (y/n) " answer
  [[ "$answer" =~ ^[Yy]([Ee][Ss])?$ ]] || fail "Cancelled. Nothing was changed."
}

# ---------- 1. go to backend/ and load the Python environment ----------
load_environment() {
  step "Loading the project environment"
  cd "$BACKEND"

  [[ -f .venv/bin/activate ]] || fail "No .venv found in backend/. Create it once:
    cd backend && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements-dev.txt"
  # shellcheck disable=SC1091
  source .venv/bin/activate
  ok "Python environment (.venv)"

  [[ -f deploy.env ]] || fail "backend/deploy.env is missing. Create it from the example:
    cp backend/deploy.env.example backend/deploy.env   (then fill in your account and profile)"
  set -a
  # shellcheck disable=SC1091
  source deploy.env       # sets APPROVED_ACCOUNT, AWS_PROFILE, AWS_REGION, ...
  set +a
  [[ "${APPROVED_ACCOUNT:-}" =~ ^[0-9]{12}$ ]] || fail "APPROVED_ACCOUNT in deploy.env must be a 12-digit AWS account ID."
  local profile="${AWS_PROFILE:-default}"
  ok "Settings from deploy.env (profile: ${profile//[0-9]/*}, region: ${AWS_REGION:-us-east-1})"

  if command -v cdk >/dev/null 2>&1; then
    CDK="cdk"
  else
    CDK="npx --yes aws-cdk"
    warn "cdk is not installed; using 'npx aws-cdk' instead (slower). Install once: npm install -g aws-cdk"
  fi
}

# ---------- 2. is the internet fast enough for CDK? ----------
check_network() {
  step "Checking the network"
  local host="sts.${AWS_REGION:-us-east-1}.amazonaws.com" start end ms
  start=$(date +%s%N)
  getent ahosts "$host" >/dev/null 2>&1 || fail "Cannot look up $host. Check your internet connection."
  end=$(date +%s%N)
  ms=$(( (end - start) / 1000000 ))
  # CDK gives up after 10 seconds, so a slow lookup shows up as "no credentials".
  if (( ms > 5000 )); then
    fail "Looking up AWS took ${ms} ms (should be under 1000). CDK will fail with 'no credentials'.
    Fix: use your phone's hotspot, or set DNS to 8.8.8.8 and 1.1.1.1 in the Wi-Fi settings."
  fi
  ok "AWS address lookup took ${ms} ms"
}

# ---------- 3. are we logged in to the RIGHT account? ----------
check_account() {
  step "Checking which AWS account you are logged in to"
  local account
  if ! account=$(aws sts get-caller-identity --query Account --output text 2>/dev/null); then
    fail "You are not logged in, or the login has expired. Run:
    aws sso login --profile ${AWS_PROFILE:-default}"
  fi
  if [[ "$account" != "$APPROVED_ACCOUNT" ]]; then
    fail "You are logged in to account ...${account: -4}, but deploy.env approves ...${APPROVED_ACCOUNT: -4}.
    Nothing was changed. Log in to the approved account, or fix deploy.env."
  fi
  ok "Logged in to the approved account (...${account: -4}), region ${AWS_REGION:-us-east-1}"
}

# ---------- 4. do the tests pass? ----------
run_tests() {
  step "Running the tests (free, no AWS)"
  if ! pytest -q; then
    fail "Some tests failed. Fix them before deploying."
  fi
  ok "All tests passed"
}

# ---------- 5. what state is the stack in? ----------
stack_status() {
  # Prints the stack status, or NONE if the stack does not exist.
  aws cloudformation describe-stacks --stack-name "$STACK" \
    --query "Stacks[0].StackStatus" --output text 2>/dev/null || echo "NONE"
}

require_healthy_stack() {
  local status
  status=$(stack_status)
  case "$status" in
    NONE)
      fail "The stack $STACK does not exist yet. Run ./scripts/deploy.sh first." ;;
    CREATE_COMPLETE | UPDATE_COMPLETE | UPDATE_ROLLBACK_COMPLETE)
      ok "Stack $STACK is in a healthy state ($status)" ;;
    ROLLBACK_COMPLETE)
      fail "The stack's first deploy failed (state ROLLBACK_COMPLETE). Run ./scripts/destroy.sh, then ./scripts/deploy.sh." ;;
    *_IN_PROGRESS)
      fail "The stack is busy ($status). Wait a few minutes and try again." ;;
    *)
      fail "The stack is in state $status. Open CloudFormation in the AWS console to see why, before changing it." ;;
  esac
}

# ---------- 6. show the addresses ----------
show_outputs() {
  step "Your addresses"
  aws cloudformation describe-stacks --stack-name "$STACK" \
    --query "Stacks[0].Outputs[].[OutputKey,OutputValue]" --output text | sed 's/^/    /'
}
