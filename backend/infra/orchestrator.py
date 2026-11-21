"""The orchestrator: a Step Functions state machine (ADR-002).

It runs the three agents in order and hands each one's output to the next:
  extract clauses -> flag risks -> rewrite in plain English -> save result
If an agent fails it is retried up to 3 times. If it still fails, the job is
saved as FAILED, so the page never waits forever.
"""
import aws_cdk as cdk
from aws_cdk import aws_stepfunctions as sfn
from aws_cdk import aws_stepfunctions_tasks as tasks

from infra.settings import PREFIX


def _agent_step(stack, name, fn):
    """One step: run an agent Lambda. Retry up to 3 times if it fails (NFR-4)."""
    step = tasks.LambdaInvoke(
        stack, name,
        lambda_function=fn,
        payload_response_only=True,            # hand the Lambda's output straight to the next step
        retry_on_service_exceptions=False,     # turn off CDK's extra default retry; we use our own below
    )
    step.add_retry(
        errors=["States.ALL"],
        max_attempts=3,
        interval=cdk.Duration.seconds(2),
        backoff_rate=2.0,                      # wait 2 s, then 4 s, then 8 s
    )
    return step


def create_pipeline(stack, fns, jobs_table):
    extract = _agent_step(stack, "Extract clauses", fns.extractor)
    flag = _agent_step(stack, "Flag risks", fns.flagger)
    rewrite = _agent_step(stack, "Rewrite in plain English", fns.rewriter)

    job_key = {"job_id": tasks.DynamoAttributeValue.from_string(sfn.JsonPath.string_at("$.job_id"))}

    # After agent 3: save SUCCEEDED and the result in the jobs table.
    save_success = tasks.DynamoUpdateItem(
        stack, "Save result",
        table=jobs_table,
        key=job_key,
        update_expression="SET #s = :s, result_json = :r",
        expression_attribute_names={"#s": "status"},
        expression_attribute_values={
            ":s": tasks.DynamoAttributeValue.from_string("SUCCEEDED"),
            ":r": tasks.DynamoAttributeValue.from_string(
                sfn.JsonPath.json_to_string(sfn.JsonPath.object_at("$.result"))),
        },
        result_path=sfn.JsonPath.DISCARD,
    )

    # If an agent still fails after its retries: save FAILED with a friendly message.
    save_failure = tasks.DynamoUpdateItem(
        stack, "Save failure",
        table=jobs_table,
        key=job_key,
        update_expression="SET #s = :s, #e = :e",
        expression_attribute_names={"#s": "status", "#e": "error"},
        expression_attribute_values={
            ":s": tasks.DynamoAttributeValue.from_string("FAILED"),
            ":e": tasks.DynamoAttributeValue.from_string("The analysis failed. Please try again."),
        },
        result_path=sfn.JsonPath.DISCARD,
    )
    for step in (extract, flag, rewrite):
        step.add_catch(save_failure, errors=["States.ALL"], result_path="$.error_info")
    save_failure.next(sfn.Fail(stack, "Job failed"))

    # The happy path, read it left to right.
    definition = extract.next(flag).next(rewrite).next(save_success).next(sfn.Succeed(stack, "Job done"))

    pipeline = sfn.StateMachine(
        stack, "Pipeline",
        state_machine_name=f"{PREFIX}-doc-explainer-pipeline",
        definition_body=sfn.DefinitionBody.from_chainable(definition),
        timeout=cdk.Duration.minutes(10),
    )

    # start_job needs the pipeline's address and permission to start it.
    fns.start.add_environment("STATE_MACHINE_ARN", pipeline.state_machine_arn)
    pipeline.grant_start_execution(fns.start)
    return pipeline
