#!/usr/bin/env python3
"""
Deploy Google ADK Agent to Vertex AI Agent Engine

This script deploys the customer support agent with MCP calculator tools
to Vertex AI Agent Engine.
"""
import argparse
import json
import os
import sys
import requests
from typing import Dict, List, Any

try:
    from google.cloud import aiplatform
    from google.oauth2 import service_account
    import yaml
except ImportError:
    print("Error: Required packages not installed.")
    print("Please install: pip install google-cloud-aiplatform pyyaml requests")
    sys.exit(1)


def load_config(config_path: str) -> Dict[str, Any]:
    """Load agent configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def load_system_prompt(prompt_path: str) -> str:
    """Load system prompt from file."""
    with open(prompt_path, 'r') as f:
        return f.read().strip()


def fetch_mcp_tools(mcp_server_url: str) -> List[Dict[str, Any]]:
    """Fetch available tools from MCP server."""
    try:
        response = requests.get(f"{mcp_server_url}/tools", timeout=10)
        response.raise_for_status()
        tools_data = response.json()
        return tools_data.get('tools', [])
    except Exception as e:
        print(f"Warning: Could not fetch tools from MCP server: {e}")
        print("Using placeholder tool definitions...")
        return get_placeholder_tools()


def get_placeholder_tools() -> List[Dict[str, Any]]:
    """Return placeholder tool definitions if MCP server is not accessible."""
    return [
        {
            "name": "add",
            "description": "Add two numbers together",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "First number"},
                    "b": {"type": "number", "description": "Second number"}
                },
                "required": ["a", "b"]
            }
        },
        {
            "name": "subtract",
            "description": "Subtract second number from first number",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "First number"},
                    "b": {"type": "number", "description": "Second number"}
                },
                "required": ["a", "b"]
            }
        },
        {
            "name": "multiply",
            "description": "Multiply two numbers together",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "First number"},
                    "b": {"type": "number", "description": "Second number"}
                },
                "required": ["a", "b"]
            }
        },
        {
            "name": "percentage",
            "description": "Calculate percentage of a number",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "number": {"type": "number", "description": "Base number"},
                    "percent": {"type": "number", "description": "Percentage"}
                },
                "required": ["number", "percent"]
            }
        }
    ]


def convert_mcp_tools_to_vertex_format(mcp_tools: List[Dict[str, Any]],
                                       mcp_server_url: str) -> List[Dict[str, Any]]:
    """Convert MCP tool definitions to Vertex AI function calling format."""
    vertex_tools = []

    for tool in mcp_tools:
        vertex_tool = {
            "function_declarations": [{
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["inputSchema"]
            }]
        }
        vertex_tools.append(vertex_tool)

    return vertex_tools


def create_agent(
    project_id: str,
    location: str,
    agent_name: str,
    display_name: str,
    system_prompt: str,
    mcp_server_url: str,
    service_account: str,
    model_name: str = "gemini-2.0-flash-exp"
) -> None:
    """Create and deploy Vertex AI agent."""

    # Initialize Vertex AI
    aiplatform.init(project=project_id, location=location)

    print(f"Initializing Vertex AI in {project_id}/{location}...")
    print(f"Agent: {display_name}")
    print(f"MCP Server: {mcp_server_url}")

    # Fetch MCP tools
    print("\nFetching tools from MCP server...")
    mcp_tools = fetch_mcp_tools(mcp_server_url)
    print(f"Found {len(mcp_tools)} tools: {[t['name'] for t in mcp_tools]}")

    # Convert tools to Vertex AI format
    vertex_tools = convert_mcp_tools_to_vertex_format(mcp_tools, mcp_server_url)

    print("\nAgent configuration:")
    print(f"  Model: {model_name}")
    print(f"  Tools: {len(vertex_tools)} function declarations")
    print(f"  Service Account: {service_account}")

    print("\n" + "="*60)
    print("IMPORTANT: Vertex AI Agent Engine Deployment")
    print("="*60)
    print("\nVertex AI Agent Engine is currently in preview and requires")
    print("manual configuration through the Google Cloud Console or gcloud CLI.")
    print("\nTo complete the agent deployment, use the following gcloud command:")
    print("\n" + "-"*60)

    # Generate gcloud command for agent creation
    tools_json = json.dumps(mcp_tools, indent=2)
    print(f"""
# 1. Create a tools configuration file
cat > /tmp/agent_tools.json <<'EOF'
{tools_json}
EOF

# 2. Deploy the agent using gcloud (when available) or Console
# Note: Replace with actual gcloud command when Agent Engine CLI is available

# 3. Configure the agent to call your MCP server:
#    MCP Server URL: {mcp_server_url}
#    Service Account: {service_account}

# 4. Set the system instruction:
cat > /tmp/system_prompt.txt <<'EOF'
{system_prompt}
EOF
""")
    print("-"*60)

    print("\nAgent configuration saved. Please follow the manual steps above.")
    print("\nFor more information, visit:")
    print("https://cloud.google.com/vertex-ai/docs/generative-ai/agent-builder")


def main():
    parser = argparse.ArgumentParser(
        description="Deploy Google ADK Agent to Vertex AI Agent Engine"
    )
    parser.add_argument("--project-id", required=True, help="GCP Project ID")
    parser.add_argument("--location", default="us-central1", help="GCP region")
    parser.add_argument("--agent-name", default="customer-support-agent",
                       help="Agent name")
    parser.add_argument("--display-name", default="Customer Support Agent",
                       help="Agent display name")
    parser.add_argument("--mcp-server-url", required=True,
                       help="URL of deployed MCP server")
    parser.add_argument("--service-account", required=True,
                       help="Service account email for the agent")
    parser.add_argument("--config", default="agent_config.yaml",
                       help="Path to agent configuration file")
    parser.add_argument("--system-prompt", default="prompts/system_prompt.txt",
                       help="Path to system prompt file")

    args = parser.parse_args()

    # Load configuration
    if os.path.exists(args.config):
        config = load_config(args.config)
        print(f"Loaded configuration from {args.config}")
    else:
        print(f"Warning: Config file {args.config} not found, using defaults")
        config = {}

    # Load system prompt
    if os.path.exists(args.system_prompt):
        system_prompt = load_system_prompt(args.system_prompt)
    else:
        print(f"Warning: System prompt file {args.system_prompt} not found")
        system_prompt = config.get('agent', {}).get('system_instruction', '')

    # Deploy agent
    create_agent(
        project_id=args.project_id,
        location=args.location,
        agent_name=args.agent_name,
        display_name=args.display_name,
        system_prompt=system_prompt,
        mcp_server_url=args.mcp_server_url,
        service_account=args.service_account
    )


if __name__ == "__main__":
    main()
