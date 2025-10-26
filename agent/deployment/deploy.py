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

"""Deploy Calculator Support Agent to Vertex AI Agent Engine."""

import argparse
import logging
import os
import sys

import vertexai
from google.api_core.exceptions import NotFound
from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp

# Add parent directory to path to import calculator_agent
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from calculator_agent.agent import root_agent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_PROJECT_ID = "agentic-ai-batch-2025"
DEFAULT_LOCATION = "us-central1"
DEFAULT_STAGING_BUCKET = f"gs://{DEFAULT_PROJECT_ID}-adk-staging"

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
    required="--delete" in sys.argv,
    help="Resource ID to delete (format: projects/PROJECT_ID/locations/LOCATION/reasoningEngines/ENGINE_ID)"
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

    # Create AdkApp from root agent
    logger.info("\n2. Creating AdkApp from agent...")
    app = AdkApp(agent=root_agent, enable_tracing=False)
    logger.info(f"   ✅ AdkApp created for agent: {root_agent.name}")

    # Deploy to Agent Engine
    logger.info("\n3. Deploying to Vertex AI Agent Engine...")
    logger.info("   This may take a few minutes...")

    try:
        # Change to parent directory to use relative path for extra_packages
        original_dir = os.getcwd()
        agent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        os.chdir(agent_dir)
        logger.info(f"   Working directory: {os.getcwd()}")
        logger.info(f"   Including calculator_agent package")

        remote_app = agent_engines.create(
            app,
            requirements=[
                "google-adk>=0.1.0",
                "google-cloud-aiplatform>=1.70.0",
                "mcp>=1.0.0",
            ],
            extra_packages=["./calculator_agent"],
        )

        # Restore original directory
        os.chdir(original_dir)

        logger.info("\n   ✅ Agent deployed successfully!")
        logger.info(f"\n   Resource Name: {remote_app.resource_name}")

        # Test the deployed agent
        logger.info("\n4. Testing deployed agent...")
        test_query = "Hi! I'm buying 3 items at $29.99 each. What's the total?"
        logger.info(f"   Query: {test_query}")

        session = remote_app.create_session(user_id="test-user")
        logger.info(f"   Session created: {session['id']}")

        logger.info("   Sending query to agent...")
        for event in remote_app.stream_query(
            user_id="test-user",
            session_id=session["id"],
            message=test_query,
        ):
            if event.get("content"):
                logger.info(f"   Response: {event['content']}")

        logger.info("\n" + "="*70)
        logger.info("DEPLOYMENT COMPLETE!")
        logger.info("="*70)
        logger.info(f"\nAgent Resource Name:")
        logger.info(f"  {remote_app.resource_name}")
        logger.info(f"\nYou can now interact with the agent:")
        logger.info(f"  - Vertex AI Console: https://console.cloud.google.com/vertex-ai/agent-builder")
        logger.info(f"  - Via API using the resource name")
        logger.info(f"  - Programmatically with remote_app.query()")
        logger.info(f"\nTo save this resource name for later use:")
        logger.info(f"  echo '{remote_app.resource_name}' > agent_resource_name.txt")

        # Save resource name
        with open("agent_resource_name.txt", "w") as f:
            f.write(remote_app.resource_name)
        logger.info(f"\n✅ Resource name saved to agent_resource_name.txt")

        return remote_app

    except Exception as e:
        # Restore original directory on error
        if 'original_dir' in locals():
            os.chdir(original_dir)
        logger.error(f"\n❌ Deployment failed: {e}")
        logger.error("\nTroubleshooting:")
        logger.error("  1. Ensure Vertex AI API is enabled:")
        logger.error("     gcloud services enable aiplatform.googleapis.com")
        logger.error("  2. Check IAM permissions (roles/aiplatform.user)")
        logger.error("  3. Verify project and location are correct")
        logger.error("  4. Ensure staging bucket exists and is accessible:")
        logger.error(f"     gsutil ls {staging_bucket} || gsutil mb {staging_bucket}")
        raise


def delete_agent(resource_id: str):
    """Delete a deployed agent."""
    logger.info(f"Deleting agent: {resource_id}")

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
        delete_agent(args.resource_id)
    else:
        deploy_agent(
            project_id=args.project_id,
            location=args.location,
            staging_bucket=args.staging_bucket
        )


if __name__ == "__main__":
    main()
