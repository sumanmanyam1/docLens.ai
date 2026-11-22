#!/usr/bin/env bash
# update.sh: apply your code or page changes to the stack that is already in AWS.
#
# Run from anywhere:   ./scripts/update.sh
# Steps: load settings -> check network -> check account -> check the stack is healthy
#        -> run tests -> show what will change (cdk diff) -> ask -> cdk deploy

source "$(dirname "$0")/_common.sh"

load_environment
check_network
check_account

step "Checking the stack"
require_healthy_stack

run_tests

step "What will change (preview only, nothing is changed yet)"
set +e
diff_output=$($CDK diff 2>&1)
set -e
echo "$diff_output" | sed 's/^/    /'
if grep -qE "Number of stacks with differences: 0|There were no differences" <<<"$diff_output"; then
  ok "No changes. AWS already matches your code."
  exit 0
elif ! grep -qE "Number of stacks with differences: [1-9]" <<<"$diff_output"; then
  fail "cdk diff did not finish (see the message above). Nothing was changed."
fi

echo
echo "    Read the list above:"
echo "      [~] = changed   [+] = new   [-] = deleted"
echo "    A normal update shows [~] for Lambdas or the website. Be careful with any [-] resource lines."
ask_yes "Apply these changes?"

$CDK deploy --require-approval broadening

step "Checking the result"
status=$(stack_status)
[[ "$status" == "UPDATE_COMPLETE" ]] || fail "The stack ended in state $status. Check CloudFormation in the AWS console."
ok "Stack updated ($status)"

show_outputs
echo
echo "Done. Refresh the website with Ctrl+Shift+R to see the newest page."
