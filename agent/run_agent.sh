#!/bin/bash
#
# Quick script to run and test the AI agent
#

echo "======================================================================="
echo "  AI AGENT - Customer Support Chatbot"
echo "======================================================================="
echo ""
echo "Choose an option:"
echo ""
echo "  1) Interactive Chat (talk to the agent)"
echo "  2) Run Automated Tests (5 test queries)"
echo "  3) Single Query (ask one question)"
echo "  4) Exit"
echo ""
read -p "Enter choice [1-4]: " choice

# Set credentials
export GOOGLE_APPLICATION_CREDENTIALS=/home/agenticai/agentic-ai-batch-2025-bb06223e6daf.json

case $choice in
    1)
        echo ""
        echo "Starting interactive chat..."
        echo ""
        .venv/bin/python3 chat_with_agent.py
        ;;
    2)
        echo ""
        echo "Running automated tests..."
        echo ""
        .venv/bin/python3 test_deployed_agent.py
        ;;
    3)
        echo ""
        read -p "Enter your question: " question
        echo ""
        echo "Asking agent..."
        echo ""
        .venv/bin/python3 -c "
from vertexai.agent_engines import AgentEngine
import vertexai

vertexai.init(
    project='agentic-ai-batch-2025',
    location='us-central1',
    staging_bucket='gs://agentic-ai-batch-2025-staging'
)

agent = AgentEngine(
    resource_name='projects/740202511174/locations/us-central1/reasoningEngines/8601228775440515072'
)

response = agent.query(input='$question')
print('Agent Response:')
print(response['output'])
"
        ;;
    4)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo "Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "======================================================================="
