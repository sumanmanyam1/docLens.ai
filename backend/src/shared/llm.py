"""Tool: talk to the AI model (Claude on Amazon Bedrock).

Every stage Lambda uses this. In tests we replace call_model() with a fake,
so the tests are free and need no AWS login.
"""
import json

import boto3

from shared.config import MODEL_ID, REGION


def strip_code_fences(text: str) -> str:
    """Remove a ```json ... ``` wrapper if the model added one. Otherwise return the text as is."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else ""   # drop the opening fence line
        if text.rstrip().endswith("```"):
            text = text.rstrip()[:-3]                            # drop the closing fence
    return text.strip()


def call_model(system_prompt: str, user_text: str) -> dict:
    """Send a prompt to Claude (via Bedrock converse) and return the JSON reply."""
    client = boto3.client("bedrock-runtime", region_name=REGION)
    response = client.converse(
        modelId=MODEL_ID,
        system=[{"text": system_prompt}],
        messages=[{"role": "user", "content": [{"text": user_text}]}],
        inferenceConfig={"maxTokens": 4000, "temperature": 0},
    )
    reply_text = response["output"]["message"]["content"][0]["text"]
    return json.loads(strip_code_fences(reply_text))
