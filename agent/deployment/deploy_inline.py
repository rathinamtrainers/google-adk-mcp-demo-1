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

"""Deploy Calculator Support Agent to Vertex AI (inline version)."""

import argparse
import logging
import os

import vertexai
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams
from google.api_core.exceptions import NotFound
from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_PROJECT_ID = "agentic-ai-batch-2025"
DEFAULT_LOCATION = "us-central1"
DEFAULT_STAGING_BUCKET = f"gs://{DEFAULT_PROJECT_ID}-adk-staging"
MCP_SERVER_URL = os.getenv(
    "MCP_SERVER_URL",
    "https://mcp-calculator-server-oyhyp5p3ua-uc.a.run.app/mcp"
)

# Agent instruction
AGENT_INSTRUCTION = """You are a helpful and friendly customer support agent for an e-commerce company.

Your responsibilities include:
- Answering customer questions about products, orders, and policies
- Helping customers with calculations (pricing, discounts, taxes, shipping costs)
- Providing clear and accurate information
- Being empathetic and understanding of customer concerns

You have access to calculator tools that can help you with:
- Addition (add): Add two numbers together
- Subtraction (subtract): Subtract second number from first number
- Multiplication (multiply): Multiply two numbers together
- Division (divide): Divide first number by second number
- Percentage (percentage): Calculate percentage of a number (useful for discounts)
- Power (power): Raise a number to a power
- Square Root (sqrt): Calculate square root of a number

Guidelines:
- Always be polite and professional
- Use the calculator tools when customers ask about pricing or need calculations
- Break down complex calculations step by step
- Confirm calculations with the customer
- Show your work - explain what calculations you're performing
"""


# Create MCP toolset at module level (no file handles with streamable HTTP)
mcp_tools = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=MCP_SERVER_URL,
    ),
    tool_filter=[
        "add",
        "subtract",
        "multiply",
        "divide",
        "power",
        "sqrt",
        "percentage"
    ],
)


parser = argparse.ArgumentParser(
    description="Deploy Calculator Support Agent to Vertex AI"
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
    "--staging-bucket",
    default=DEFAULT_STAGING_BUCKET,
    help=f"Staging bucket for deployment (default: {DEFAULT_STAGING_BUCKET})"
)
parser.add_argument(
    "--delete",
    action="store_true",
    help="Delete deployed agent"
)
parser.add_argument(
    "--resource-id",
    help="Resource ID to delete"
)


def deploy_agent(project_id: str, location: str, staging_bucket: str):
    """Deploy the agent to Vertex AI Agent Engine."""

    logger.info("="*70)
    logger.info("Deploying Calculator Support Agent to Vertex AI")
    logger.info("="*70)
    logger.info(f"Project: {project_id}")
    logger.info(f"Location: {location}")
    logger.info(f"Staging Bucket: {staging_bucket}")

    # Initialize Vertex AI
    logger.info("\n1. Initializing Vertex AI...")
    vertexai.init(
        project=project_id,
        location=location,
        staging_bucket=staging_bucket
    )

    # Create agent inline
    logger.info("\n2. Creating agent...")
    root_agent = Agent(
        model="gemini-2.0-flash-001",
        name="calculator_support_agent",
        instruction=AGENT_INSTRUCTION,
        tools=[mcp_tools],
    )
    logger.info(f"   ✅ Agent created: {root_agent.name}")

    # Create AdkApp
    logger.info("\n3. Creating AdkApp from agent...")
    app = AdkApp(agent=root_agent, enable_tracing=False)
    logger.info(f"   ✅ AdkApp created")

    # Deploy to Agent Engine
    logger.info("\n4. Deploying to Vertex AI Agent Engine...")
    logger.info("   This may take a few minutes...")

    try:
        remote_app = agent_engines.create(
            app,
            requirements=[
                "google-adk>=0.1.0",
                "google-cloud-aiplatform>=1.70.0",
                "mcp>=1.0.0",
            ],
        )

        logger.info("\n   ✅ Agent deployed successfully!")
        logger.info(f"\n   Resource Name: {remote_app.resource_name}")

        # Save resource name
        resource_file = "agent_resource_name.txt"
        with open(resource_file, "w") as f:
            f.write(remote_app.resource_name)
        logger.info(f"\n✅ Resource name saved to {resource_file}")

        logger.info("\n" + "="*70)
        logger.info("DEPLOYMENT COMPLETE!")
        logger.info("="*70)
        logger.info(f"\nAgent Resource Name:")
        logger.info(f"  {remote_app.resource_name}")
        logger.info(f"\nYou can now test the agent:")
        logger.info(f"  python deployment/test_deployment.py")
        logger.info(f"\nOr access it via:")
        logger.info(f"  - Vertex AI Console: https://console.cloud.google.com/vertex-ai/agent-builder")

        return remote_app

    except Exception as e:
        logger.error(f"\n❌ Deployment failed: {e}")
        logger.error("\nTroubleshooting:")
        logger.error("  1. Ensure Vertex AI API is enabled:")
        logger.error("     gcloud services enable aiplatform.googleapis.com")
        logger.error("  2. Check IAM permissions (roles/aiplatform.user)")
        logger.error("  3. Verify project and location are correct")
        logger.error("  4. Ensure staging bucket exists and is accessible:")
        logger.error(f"     gsutil ls {staging_bucket} || gsutil mb {staging_bucket}")
        logger.error(f"  5. Check logs: https://console.cloud.google.com/logs/query?project={project_id}")
        raise


def delete_agent(project_id: str, location: str, resource_id: str):
    """Delete a deployed agent."""
    logger.info(f"Deleting agent: {resource_id}")

    vertexai.init(project=project_id, location=location)

    try:
        agent_engines.get(resource_name=resource_id)
        agent_engines.delete(resource_name=resource_id)
        logger.info(f"✅ Agent {resource_id} deleted successfully")
    except NotFound:
        logger.error(f"❌ Agent {resource_id} not found")
    except Exception as e:
        logger.error(f"❌ Error deleting agent: {e}")
        raise


def main():
    args = parser.parse_args()

    if args.delete:
        if not args.resource_id:
            logger.error("--resource-id is required when using --delete")
            return
        delete_agent(args.project_id, args.location, args.resource_id)
    else:
        deploy_agent(
            project_id=args.project_id,
            location=args.location,
            staging_bucket=args.staging_bucket
        )


if __name__ == "__main__":
    main()
