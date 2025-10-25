#!/usr/bin/env python3
"""
Test the deployed Vertex AI agent with various queries
"""
import vertexai
from vertexai import agent_engines

# Configuration
PROJECT_ID = "agentic-ai-batch-2025"
LOCATION = "us-central1"
AGENT_RESOURCE_NAME = "projects/740202511174/locations/us-central1/reasoningEngines/8601228775440515072"

# Initialize Vertex AI
vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
    staging_bucket=f"gs://{PROJECT_ID}-staging"
)

# Load the deployed agent
print("Loading deployed agent...")
from vertexai.agent_engines import AgentEngine
remote_agent = AgentEngine(resource_name=AGENT_RESOURCE_NAME)
print(f"✅ Agent loaded: {AGENT_RESOURCE_NAME}\n")

# Test queries
test_queries = [
    "What is 5 plus 3?",
    "Calculate 15% of 100",
    "I have a $120 order with a 15% discount. What's my final price?",
    "What's the square root of 64?",
    "If I'm buying 4 items at $25.50 each, what's the total?"
]

print("="*70)
print("TESTING DEPLOYED AGENT")
print("="*70)

for i, query in enumerate(test_queries, 1):
    print(f"\nTest {i}:")
    print(f"Query: {query}")

    try:
        response = remote_agent.query(input=query)
        print(f"Response: {response['output']}")
    except Exception as e:
        print(f"Error: {e}")

print("\n" + "="*70)
print("TESTS COMPLETE!")
print("="*70)
