"""Demo switch: make one agent fail on purpose, to show Step Functions Retry and Catch.

Normal documents never fail, so a demo needs a way to make a failure happen on
demand. If a document contains a marker such as

    [[DEMO-FAIL:risk_flagger]]

then that agent raises an error instead of doing its work. Step Functions retries
it 3 times, then Catch sends the job to "Save failure" and it ends as FAILED.

It only works when the Lambda setting DEMO_FAULTS is "on" (set in infra/settings.py).
With DEMO_FAULTS off, the marker is ignored and the document is processed normally.
"""
import os

MARKER = "[[DEMO-FAIL:{agent}]]"


class DemoFailure(Exception):
    """The error raised on purpose for the demo."""


def maybe_fail(agent_name, text):
    """Raise DemoFailure if demo faults are on and the document asks this agent to fail."""
    if os.environ.get("DEMO_FAULTS", "off") != "on":
        return
    if MARKER.format(agent=agent_name) in (text or ""):
        raise DemoFailure(f"Forced failure for demo in {agent_name} (marker found in the document)")
