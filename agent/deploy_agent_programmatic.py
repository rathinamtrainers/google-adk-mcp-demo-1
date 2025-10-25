#!/usr/bin/env python3
"""
Deploy Customer Support Agent to Vertex AI Agent Engine
Uses Google Cloud Vertex AI Agent Development Kit (ADK)
"""

import os
import sys
import requests
from typing import Dict, Any

# Install required packages first:
# pip install google-cloud-aiplatform[agent_engines,langchain]>=1.112

try:
    import vertexai
    from vertexai import agent_engines
except ImportError:
    print("Error: Required packages not installed.")
    print("Please run: pip install google-cloud-aiplatform[agent_engines,langchain]>=1.112")
    sys.exit(1)


# Configuration
PROJECT_ID = "agentic-ai-batch-2025"
LOCATION = "us-central1"
MCP_SERVER_URL = "https://mcp-calculator-server-oyhyp5p3ua-uc.a.run.app"
AGENT_NAME = "customer-support-agent"


# Define calculator tool functions that call the MCP server
def add(a: float, b: float) -> str:
    """Add two numbers together.

    Args:
        a: First number
        b: Second number

    Returns:
        Result of addition
    """
    response = requests.post(
        f"{MCP_SERVER_URL}/tools/add",
        json={"arguments": {"a": a, "b": b}},
        timeout=10
    )
    result = response.json()
    return result["result"][0]["text"]


def subtract(a: float, b: float) -> str:
    """Subtract second number from first number.

    Args:
        a: First number (minuend)
        b: Second number (subtrahend)

    Returns:
        Result of subtraction
    """
    response = requests.post(
        f"{MCP_SERVER_URL}/tools/subtract",
        json={"arguments": {"a": a, "b": b}},
        timeout=10
    )
    result = response.json()
    return result["result"][0]["text"]


def multiply(a: float, b: float) -> str:
    """Multiply two numbers together.

    Args:
        a: First number
        b: Second number

    Returns:
        Result of multiplication
    """
    response = requests.post(
        f"{MCP_SERVER_URL}/tools/multiply",
        json={"arguments": {"a": a, "b": b}},
        timeout=10
    )
    result = response.json()
    return result["result"][0]["text"]


def divide(a: float, b: float) -> str:
    """Divide first number by second number.

    Args:
        a: Numerator
        b: Denominator (cannot be zero)

    Returns:
        Result of division
    """
    response = requests.post(
        f"{MCP_SERVER_URL}/tools/divide",
        json={"arguments": {"a": a, "b": b}},
        timeout=10
    )
    result = response.json()
    return result["result"][0]["text"]


def percentage(number: float, percent: float) -> str:
    """Calculate percentage of a number.

    Args:
        number: The number to calculate percentage of
        percent: The percentage value

    Returns:
        Result of percentage calculation
    """
    response = requests.post(
        f"{MCP_SERVER_URL}/tools/percentage",
        json={"arguments": {"number": number, "percent": percent}},
        timeout=10
    )
    result = response.json()
    return result["result"][0]["text"]


def sqrt(number: float) -> str:
    """Calculate square root of a number.

    Args:
        number: Number to calculate square root of (must be non-negative)

    Returns:
        Result of square root calculation
    """
    response = requests.post(
        f"{MCP_SERVER_URL}/tools/sqrt",
        json={"arguments": {"number": number}},
        timeout=10
    )
    result = response.json()
    return result["result"][0]["text"]


def power(base: float, exponent: float) -> str:
    """Raise first number to the power of second number.

    Args:
        base: Base number
        exponent: Exponent

    Returns:
        Result of exponentiation
    """
    response = requests.post(
        f"{MCP_SERVER_URL}/tools/power",
        json={"arguments": {"base": base, "exponent": exponent}},
        timeout=10
    )
    result = response.json()
    return result["result"][0]["text"]


# System instructions for the agent
SYSTEM_INSTRUCTION = """You are a helpful and friendly customer support agent for an e-commerce company.

Your responsibilities include:
- Answering customer questions about products, orders, and policies
- Helping customers with calculations (pricing, discounts, taxes, shipping costs)
- Providing clear and accurate information
- Being empathetic and understanding of customer concerns
- Escalating complex issues when necessary

You have access to calculator tools that can help you with:
- Addition, subtraction, multiplication, and division
- Percentage calculations (for discounts)
- Power and square root operations

Guidelines:
- Always be polite and professional
- Use the calculator tools when customers ask about pricing or need calculations
- Break down complex calculations step by step
- Confirm calculations with the customer
- If you don't know something, be honest and offer to find the information
- Never make up product information or policies

Remember: You are here to help customers have a positive experience!
"""


def deploy_agent():
    """Deploy the customer support agent to Vertex AI Agent Engine."""

    print("="*70)
    print("Deploying Customer Support Agent to Vertex AI Agent Engine")
    print("="*70)
    print(f"\nProject: {PROJECT_ID}")
    print(f"Location: {LOCATION}")
    print(f"MCP Server: {MCP_SERVER_URL}")
    print(f"Agent Name: {AGENT_NAME}\n")

    # Initialize Vertex AI
    print("1. Initializing Vertex AI client...")
    vertexai.init(
        project=PROJECT_ID,
        location=LOCATION,
        staging_bucket=f"gs://{PROJECT_ID}-staging"
    )

    # Test MCP server connectivity
    print("2. Testing MCP server connectivity...")
    try:
        response = requests.get(f"{MCP_SERVER_URL}/health", timeout=10)
        if response.status_code == 200:
            print(f"   ✅ MCP server is healthy: {response.json()}")
        else:
            print(f"   ⚠️  MCP server returned status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error connecting to MCP server: {e}")
        print("   Continuing anyway...")

    # Create agent with calculator tools
    print("3. Creating agent with calculator tools...")
    print("   Tools: add, subtract, multiply, divide, percentage, sqrt, power")

    agent = agent_engines.LangchainAgent(
        model="gemini-2.0-flash-exp",
        tools=[add, subtract, multiply, divide, percentage, sqrt, power],
        system_instruction=SYSTEM_INSTRUCTION,
        model_kwargs={
            "temperature": 0.7,
            "top_p": 0.95,
            "max_output_tokens": 2048,
        }
    )

    print("   ✅ Agent created locally")

    # Deploy to Vertex AI Agent Engine
    print("\n4. Deploying to Vertex AI Agent Engine...")
    print("   This may take a few minutes...")

    try:
        remote_agent = agent_engines.create(
            agent_engine=agent,
            requirements=[
                "google-cloud-aiplatform[agent_engines,langchain]>=1.112",
                "requests>=2.31.0"
            ],
            display_name=AGENT_NAME,
        )

        print(f"\n   ✅ Agent deployed successfully!")
        print(f"\n   Resource Name: {remote_agent.resource_name}")

        # Test the deployed agent
        print("\n5. Testing deployed agent...")
        test_query = "Hi! I'm buying 3 items at $29.99 each. What's the total?"
        print(f"   Query: {test_query}")

        response = remote_agent.query(input=test_query)
        print(f"   Response: {response}")

        print("\n" + "="*70)
        print("DEPLOYMENT COMPLETE!")
        print("="*70)
        print(f"\nAgent Resource Name:")
        print(f"  {remote_agent.resource_name}")
        print(f"\nYou can now interact with the agent in:")
        print(f"  - Vertex AI Console")
        print(f"  - Via API using the resource name")
        print(f"  - Programmatically with remote_agent.query()")

        return remote_agent

    except Exception as e:
        print(f"\n   ❌ Deployment failed: {e}")
        print("\nTroubleshooting:")
        print("  1. Ensure Vertex AI API is enabled")
        print("  2. Check IAM permissions (roles/aiplatform.user)")
        print("  3. Verify project and location are correct")
        print("  4. Check Cloud Storage permissions (roles/storage.admin)")
        raise


def test_local_agent():
    """Test the agent locally before deployment."""
    print("Testing agent locally...")

    vertexai.init(
        project=PROJECT_ID,
        location=LOCATION,
        staging_bucket=f"gs://{PROJECT_ID}-staging"
    )

    agent = agent_engines.LangchainAgent(
        model="gemini-2.0-flash-exp",
        tools=[add, subtract, multiply, divide, percentage, sqrt, power],
        system_instruction=SYSTEM_INSTRUCTION,
        model_kwargs={"temperature": 0.7}
    )

    # Test locally
    test_queries = [
        "What is 5 plus 3?",
        "Calculate 15% of 100",
        "I'm buying 3 items at $29.99 each. What's the total?"
    ]

    for query in test_queries:
        print(f"\nQuery: {query}")
        response = agent.query(input=query)
        print(f"Response: {response}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Deploy Customer Support Agent to Vertex AI"
    )
    parser.add_argument(
        "--test-local",
        action="store_true",
        help="Test agent locally before deployment"
    )
    parser.add_argument(
        "--project-id",
        default=PROJECT_ID,
        help="GCP Project ID"
    )
    parser.add_argument(
        "--location",
        default=LOCATION,
        help="GCP Location"
    )

    args = parser.parse_args()

    # Update globals
    PROJECT_ID = args.project_id
    LOCATION = args.location

    # Set credentials
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/agenticai/agentic-ai-batch-2025-bb06223e6daf.json"

    if args.test_local:
        test_local_agent()
    else:
        remote_agent = deploy_agent()
