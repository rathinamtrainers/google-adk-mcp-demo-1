# Calculator Support Agent - Deployment Guide

This directory contains a Google ADK-based customer support agent that uses MCP calculator tools.

## Quick Start

### 1. Install Dependencies

```bash
cd /home/agenticai/google-adk-mcp-demo-1/agent

# Create a new virtual environment
python3 -m venv venv-deploy
source venv-deploy/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Deploy to Vertex AI

```bash
# Set your Google Cloud credentials
export GOOGLE_APPLICATION_CREDENTIALS="/home/agenticai/agentic-ai-batch-2025-bb06223e6daf.json"

# Run deployment script
python deployment/deploy.py

# Or with custom project settings:
python deployment/deploy.py \
  --project-id agentic-ai-batch-2025 \
  --location us-central1 \
  --staging-bucket gs://agentic-ai-batch-2025-adk-staging
```

The deployment will:
- Create an Ad kApp from the agent
- Deploy to Vertex AI Agent Engine
- Test with a sample query
- Save the resource name to `agent_resource_name.txt`

### 3. Test the Deployed Agent

```bash
# Test the deployed agent
python deployment/test_deployment.py

# Or specify resource ID manually:
python deployment/test_deployment.py --resource-id "projects/.../reasoningEngines/..."
```

## Architecture

```
calculator_agent/
├── __init__.py           # Package initialization
├── agent.py              # Main agent definition
├── prompt.py             # System instructions
└── tools.py              # MCP toolset configuration

deployment/
├── deploy.py            # Deployment script
└── test_deployment.py   # Testing script
```

## How It Works

### MCP Integration

The agent uses Google ADK's `MCPToolset` to connect to the FastMCP calculator server deployed on Cloud Run:

```python
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams

mcp_tools = MCPToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="https://mcp-calculator-server-oyhyp5p3ua-uc.a.run.app/mcp"
    ),
    tool_filter=[
        "add", "subtract", "multiply", "divide",
        "power", "sqrt", "percentage"
    ]
)
```

### Agent Definition

```python
from google.adk.agents import Agent

root_agent = Agent(
    model="gemini-2.5-flash",
    name="calculator_support_agent",
    instruction=agent_instruction,
    tools=[mcp_tools]
)
```

## Available Calculator Tools

The agent has access to 7 calculator tools from the MCP server:

1. **add** - Add two numbers
2. **subtract** - Subtract two numbers
3. **multiply** - Multiply two numbers
4. **divide** - Divide two numbers (with zero-check)
5. **power** - Raise to a power
6. **sqrt** - Square root (with negative-check)
7. **percentage** - Calculate percentage

## Example Queries

Try these queries with the deployed agent:

- "I'm buying 3 items at $29.99 each. What's the total?"
- "I have a 15% discount code. If my order is $120, what's my final price?"
- "What's the square root of 144?"
- "If I buy 5 items at $19.99 each and get 20% off, how much do I pay?"

## Configuration

### Environment Variables

- `GOOGLE_APPLICATION_CREDENTIALS` - Path to Google Cloud service account key
- `MCP_SERVER_URL` - URL of MCP calculator server (default: deployed Cloud Run URL)

### Project Settings

Default configuration in `deployment/deploy.py`:
- **Project ID**: `agentic-ai-batch-2025`
- **Location**: `us-central1`
- **Staging Bucket**: `gs://agentic-ai-batch-2025-adk-staging`
- **Model**: `gemini-2.5-flash`

## Troubleshooting

### Deployment Fails

1. **Ensure Vertex AI API is enabled**:
   ```bash
   gcloud services enable aiplatform.googleapis.com
   ```

2. **Check IAM permissions**:
   - Need `roles/aiplatform.user` role
   - Need access to staging bucket

3. **Verify staging bucket exists**:
   ```bash
   gsutil ls gs://agentic-ai-batch-2025-adk-staging || \
     gsutil mb -l us-central1 gs://agentic-ai-batch-2025-adk-staging
   ```

### MCP Connection Fails

1. **Check MCP server is running**:
   ```bash
   curl https://mcp-calculator-server-oyhyp5p3ua-uc.a.run.app/mcp
   ```

2. **Verify Cloud Run service is deployed**:
   ```bash
   gcloud run services describe mcp-calculator-server --region us-central1
   ```

## Next Steps

1. **Deploy the agent** following the Quick Start guide above
2. **Test the agent** with sample queries
3. **Integrate with Streamlit UI** (see `../ui/` directory)
4. **Monitor in Vertex AI Console**: https://console.cloud.google.com/vertex-ai/agent-builder

## Resources

- **MCP Server**: `https://mcp-calculator-server-oyhyp5p3ua-uc.a.run.app/mcp`
- **Google ADK Documentation**: https://cloud.google.com/vertex-ai/docs/agent-dev-kit
- **MCP Protocol**: https://modelcontextprotocol.io/
- **Vertex AI Agent Builder**: https://cloud.google.com/vertex-ai/docs/generative-ai/agent-builder
