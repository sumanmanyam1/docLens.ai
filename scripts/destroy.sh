#!/usr/bin/env bash
# destroy.sh: delete the whole DocLens stack from AWS.
#
# Run from anywhere:   ./scripts/destroy.sh
# Steps: load settings -> check network -> check account -> show what will be deleted
#        -> you type the stack name -> cdk destroy -> check it is gone -> list leftovers
#
# This deletes the tables AND their data, the Lambdas, the pipeline, the API,
# and the website. It does NOT delete CDKToolkit (shared by the whole account).

source "$(dirname "$0")/_common.sh"

load_environment
check_network
check_account

step "Checking the stack"
status=$(stack_status)
[[ "$status" != "NONE" ]] || { ok "The stack $STACK does not exist. Nothing to delete."; exit 0; }
[[ "$status" != *_IN_PROGRESS ]] || fail "The stack is busy ($status). Wait a few minutes and try again."
ok "Found $STACK ($status)"

step "These resources will be DELETED"
aws cloudformation list-stack-resources --stack-name "$STACK" \
  --query "StackResourceSummaries[?ResourceType=='AWS::DynamoDB::Table' || ResourceType=='AWS::Lambda::Function' || ResourceType=='AWS::StepFunctions::StateMachine' || ResourceType=='AWS::ApiGatewayV2::Api' || ResourceType=='AWS::S3::Bucket' || ResourceType=='AWS::CloudFront::Distribution'].[ResourceType,PhysicalResourceId]" \
  --output text | sed 's/^/    /'
echo
warn "The jobs and audit-log data will be deleted too. Save any screenshots or the audit log first."

read -r -p "    To confirm, type the stack name ($STACK): " typed
[[ "$typed" == "$STACK" ]] || fail "The name did not match. Nothing was deleted."

# --force skips CDK's own y/n question, because you just confirmed by typing the name.
$CDK destroy --force

step "Checking it is gone"
status=$(stack_status)
[[ "$status" == "NONE" || "$status" == "DELETE_COMPLETE" ]] || fail "The stack is in state $status. Check CloudFormation in the AWS console."
ok "Stack $STACK deleted"

step "Leftovers (not errors)"
logs=$(aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/suman-" \
  --query "logGroups[].logGroupName" --output text 2>/dev/null || true)
if [[ -n "$logs" ]]; then
  warn "Lambda log groups are created by AWS, not by CDK, so they stay. They cost almost nothing."
  for g in $logs; do echo "      $g"; done
  echo "    To delete them too, run for each one:"
  echo "      aws logs delete-log-group --log-group-name <name>"
else
  ok "No leftover Lambda log groups"
fi
echo
echo "Done. CDKToolkit was left in place on purpose; it is shared by the whole account."
