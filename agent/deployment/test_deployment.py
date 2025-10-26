#!/usr/bin/env python3
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Test deployed Calculator Support Agent."""

import argparse
import logging
import os
import sys

import vertexai
from vertexai import agent_engines

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_PROJECT_ID = "agentic-ai-batch-2025"
DEFAULT_LOCATION = "us-central1"

parser = argparse.ArgumentParser(
    description="Test deployed Calculator Support Agent"
)
parser.add_argument(
    "--project-id",
    default=DEFAULT_PROJECT_ID,
    help=f"GCP Project ID (default: {DEFAULT_PROJECT_ID})"
)
parser.add_argument(
    "--location",
    default=DEFAULT_LOCATION,
    help=f"GCP Location (default: {DEFAULT_LOCATION})"
)
parser.add_argument(
    "--resource-id",
    help="Agent resource ID (if not provided, will try to read from agent_resource_name.txt)"
)


def test_agent(project_id: str, location: str, resource_id: str):
    """Test the deployed agent with sample queries."""

    logger.info("="*70)
    logger.info("Testing Calculator Support Agent")
    logger.info("="*70)
    logger.info(f"Project: {project_id}")
    logger.info(f"Location: {location}")
    logger.info(f"Resource: {resource_id}")

    # Initialize Vertex AI
    logger.info("\n1. Initializing Vertex AI...")
    vertexai.init(project=project_id, location=location)

    # Get the deployed agent
    logger.info("\n2. Connecting to deployed agent...")
    try:
        remote_app = agent_engines.get(resource_name=resource_id)
        logger.info(f"   ✅ Connected to agent: {resource_id}")
    except Exception as e:
        logger.error(f"   ❌ Failed to connect to agent: {e}")
        logger.error("   Make sure the agent is deployed and the resource ID is correct")
        sys.exit(1)

    # Test queries
    test_queries = [
        "Hi! I'm buying 3 items at $29.99 each. What's the total?",
        "I have a 15% discount code. If my order is $120, what's my final price?",
        "What's the square root of 144?",
        "If I buy 5 items at $19.99 each and get 20% off, how much do I pay?",
    ]

    logger.info("\n3. Running test queries...\n")

    # Create a session
    session = remote_app.create_session(user_id="test-user")
    logger.info(f"Session created: {session['id']}\n")

    for i, query in enumerate(test_queries, 1):
        logger.info(f"--- Test {i}/{len(test_queries)} ---")
        logger.info(f"Query: {query}")
        logger.info("Agent response:")

        try:
            response_text = []
            for event in remote_app.stream_query(
                user_id="test-user",
                session_id=session["id"],
                message=query,
            ):
                # Print all event types for debugging
                logger.info(f"  Event: {event}")

                if event.get("content"):
                    response_text.append(event['content'])
                if event.get("tool_use"):
                    logger.info(f"  [Tool used: {event['tool_use']}]")

            # Print final response
            if response_text:
                logger.info(f"  Final response: {' '.join(str(t) for t in response_text)}")

        except Exception as e:
            logger.error(f"  ❌ Error: {e}")

        logger.info("")  # Blank line between tests

    logger.info("="*70)
    logger.info("Testing complete!")
    logger.info("="*70)


def main():
    args = parser.parse_args()

    # Try to get resource ID from file if not provided
    resource_id = args.resource_id
    if not resource_id:
        try:
            with open("agent_resource_name.txt", "r") as f:
                resource_id = f.read().strip()
            logger.info(f"Read resource ID from agent_resource_name.txt")
        except FileNotFoundError:
            logger.error("Error: --resource-id not provided and agent_resource_name.txt not found")
            logger.error("Please provide --resource-id or ensure agent_resource_name.txt exists")
            sys.exit(1)

    test_agent(
        project_id=args.project_id,
        location=args.location,
        resource_id=resource_id
    )


if __name__ == "__main__":
    main()
