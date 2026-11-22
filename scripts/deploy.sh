#!/usr/bin/env bash
# deploy.sh: build the whole DocLens stack in AWS for the first time.
#
# Run from anywhere:   ./scripts/deploy.sh
# Steps: load settings -> check network -> check account -> run tests
#        -> bootstrap CDK if needed -> cdk deploy -> show the addresses
# If the stack already exists, use ./scripts/update.sh instead.

source "$(dirname "$0")/_common.sh"

load_environment
check_network
check_account
run_tests

step "Checking that the stack does not exist yet"
status=$(stack_status)
[[ "$status" == "NONE" ]] || fail "The stack $STACK already exists ($status). Use ./scripts/update.sh to change it."
ok "No stack yet, so this is a first deploy"

step "Checking CDK's one-time setup (bootstrap) in this account and region"
if aws cloudformation describe-stacks --stack-name CDKToolkit >/dev/null 2>&1; then
  ok "Already set up (CDKToolkit exists)"
else
  warn "CDK has not been set up in this account and region yet."
  ask_yes "Run 'cdk bootstrap' now? It creates a small helper stack called CDKToolkit."
  $CDK bootstrap "aws://${APPROVED_ACCOUNT}/${AWS_REGION:-us-east-1}"
fi

step "Ready to create the stack $STACK"
echo "    It creates: 2 DynamoDB tables, 5 Lambdas, 1 Step Functions pipeline,"
echo "    1 HTTP API, and the website (S3 bucket + CloudFront). All named suman-..."
ask_yes "Create it now?"

# CDK will also show the new permissions and ask you to type y.
$CDK deploy --require-approval broadening

step "Checking the result"
status=$(stack_status)
[[ "$status" == "CREATE_COMPLETE" || "$status" == "UPDATE_COMPLETE" ]] || fail "The stack ended in state $status. Check CloudFormation in the AWS console."
ok "Stack created ($status)"

show_outputs
echo
echo "Done. Open the FrontendUrl in your browser. CloudFront can take a few minutes the first time."
