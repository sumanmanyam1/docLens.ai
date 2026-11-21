"""Settings shared by every part of the CDK recipe."""
import os

# Every named resource we create in AWS starts with this prefix.
PREFIX = "suman"

# The AI model the agents call through Amazon Bedrock.
MODEL_ID = "us.anthropic.claude-sonnet-4-6"

# Folders, relative to this file.
HERE = os.path.dirname(__file__)
SRC_DIR = os.path.join(HERE, "..", "src")                    # code that runs in the Lambdas
FRONTEND_DIR = os.path.join(HERE, "..", "..", "frontend")    # the web page
