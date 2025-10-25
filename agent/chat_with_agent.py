#!/usr/bin/env python3
"""
Simple interactive chat with the deployed AI agent
"""
from vertexai.agent_engines import AgentEngine
import vertexai

# Initialize
vertexai.init(
    project="agentic-ai-batch-2025",
    location="us-central1",
    staging_bucket="gs://agentic-ai-batch-2025-staging"
)

# Load agent
agent = AgentEngine(
    resource_name="projects/740202511174/locations/us-central1/reasoningEngines/8601228775440515072"
)

print("="*70)
print("Customer Support Agent - Chat Interface")
print("="*70)
print("\nAgent loaded and ready!")
print("Type 'exit' or 'quit' to end the conversation.\n")

# Interactive chat loop
while True:
    try:
        # Get user input
        user_input = input("You: ").strip()

        # Check for exit
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("\nAgent: Goodbye! Have a great day!")
            break

        if not user_input:
            continue

        # Query the agent
        response = agent.query(input=user_input)

        # Display response
        print(f"\nAgent: {response['output']}\n")

    except KeyboardInterrupt:
        print("\n\nAgent: Goodbye!")
        break
    except Exception as e:
        print(f"\nError: {e}\n")
        continue

print("\n" + "="*70)
