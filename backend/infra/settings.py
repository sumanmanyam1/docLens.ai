"""Settings shared by every part of the CDK recipe."""
import os

# Every named resource we create in AWS starts with this prefix.
PREFIX = "suman"

# Demo switch for the 3 agents (see src/shared/fault_injection.py).
# "on": a document containing [[DEMO-FAIL:<agent>]] makes that agent fail on purpose,
# to demo Step Functions Retry and Catch. Set to "off" for real use.
DEMO_FAULTS = "on"

# The AI model the agents call through Amazon Bedrock.
MODEL_ID = "us.anthropic.claude-sonnet-4-6"

# Folders, relative to this file.
HERE = os.path.dirname(__file__)
SRC_DIR = os.path.join(HERE, "..", "src")                    # code that runs in the Lambdas
FRONTEND_DIR = os.path.join(HERE, "..", "..", "frontend")    # the web page
