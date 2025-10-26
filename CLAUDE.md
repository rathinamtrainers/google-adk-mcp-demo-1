# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an MCP (Model Context Protocol) server with calculator tools deployed to Google Cloud Run, integrated with a Vertex AI customer support agent using Google's Agent Development Kit (ADK). The project includes RBAC (Role-Based Access Control), authentication, and a Streamlit UI for chatting with the deployed agent.

## Architecture

The system has three main components:

1. **MCP Calculator Server** (`mcp-server/`): FastAPI-based HTTP/SSE transport server exposing calculator tools via MCP protocol
2. **Vertex AI Agent** (`agent/`): Customer support chatbot using Gemini 2.0 Flash with function calling to MCP tools
3. **Streamlit UI** (`ui/`): Interactive web interface for chatting with the deployed agent
4. **Infrastructure** (`terraform/`): Terraform IaC for deploying to Cloud Run and Vertex AI

### Key Design Patterns

- **Dual Server Pattern**: `calculator_server.py` defines MCP tools with stdio transport; `http_server.py` wraps it with FastAPI for Cloud Run compatibility
- **RBAC System**: Authentication and authorization modules in `mcp-server/src/auth/` and `mcp-server/src/rbac/` using JWT tokens, API keys, and role-based permissions
- **Tool Registration**: MCP tools are defined as async functions with `@app.list_tools()` and `@app.call_tool()` decorators in `calculator_server.py`
- **HTTP Wrapper**: `http_server.py` creates FastAPI endpoints at `/tools`, `/tools/{tool_name}`, `/execute` that delegate to MCP handlers

## Development Commands

### Local Development

```bash
# Run MCP server locally
cd mcp-server
pip install -r requirements.txt
cd src
python http_server.py  # Runs on http://localhost:8080

# Run Streamlit UI locally
cd ui
./run.sh  # Creates venv, installs deps, launches on http://localhost:8501
# OR manually:
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

### Testing

```bash
# Test MCP server endpoints
./scripts/test-mcp-server.sh

# Test individual tools
export MCP_URL=$(cd terraform && terraform output -raw mcp_server_url)
curl $MCP_URL/health
curl $MCP_URL/tools | jq '.'
curl -X POST $MCP_URL/tools/add \
  -H "Content-Type: application/json" \
  -d '{"arguments": {"a": 5, "b": 3}}' | jq '.'
```

### Building and Deployment

```bash
# Full deployment (recommended)
make deploy  # Runs scripts/deploy.sh

# Step-by-step deployment
make init    # Initialize Terraform
make plan    # Preview infrastructure changes
make apply   # Apply infrastructure
make build   # Build and push Docker image

# Deploy Vertex AI agent
cd agent
python3 deploy_agent.py \
  --project-id YOUR_PROJECT_ID \
  --location us-central1 \
  --mcp-server-url $(cd ../terraform && terraform output -raw mcp_server_url) \
  --service-account $(cd ../terraform && terraform output -raw vertex_ai_agent_service_account)
```

### Cleanup

```bash
make destroy  # Destroy all infrastructure (requires confirmation)
make clean    # Remove temporary files, Terraform state backups, __pycache__
```

## File Structure

```
mcp-server/src/
├── calculator_server.py    # Core MCP server with 7 calculator tools
├── http_server.py          # FastAPI wrapper for Cloud Run
├── database.py             # SQLAlchemy database setup for RBAC
├── auth/                   # Authentication system
│   ├── models.py           # User, Role, Permission, AuditLog models
│   ├── jwt_handler.py      # JWT token generation/validation
│   ├── api_key_handler.py  # API key authentication
│   └── dependencies.py     # FastAPI dependency injection for auth
├── rbac/                   # Role-based access control
│   ├── roles.py            # Default roles (admin, user, viewer)
│   ├── permissions.py      # Permission checking decorators
│   └── ...
├── admin/                  # Admin endpoints
├── config/                 # Configuration management
└── security/               # Security utilities

agent/
├── deploy_agent.py         # Script to deploy agent to Vertex AI
├── agent_config.yaml       # Agent configuration
└── prompts/
    └── system_prompt.txt   # System instructions for agent

ui/
├── app.py                  # Main Streamlit application
├── config.py               # UI configuration (agent ID, project settings)
├── utils.py                # Helper functions
├── styles.css              # Custom CSS styling
└── run.sh                  # Launch script

terraform/
├── main.tf                 # Main infrastructure: Artifact Registry, Cloud Run, IAM
├── variables.tf            # Input variables
├── outputs.tf              # Output values (URLs, service accounts)
└── terraform.tfvars        # Project-specific configuration (not in git)
```

## Working with MCP Tools

### Adding a New Calculator Tool

1. Add tool definition to `list_tools()` in `mcp-server/src/calculator_server.py`:
```python
Tool(
    name="your_tool",
    description="Description here",
    inputSchema={
        "type": "object",
        "properties": {
            "param": {"type": "number", "description": "..."}
        },
        "required": ["param"]
    }
)
```

2. Add handler to `call_tool()` in same file:
```python
elif name == "your_tool":
    result = your_calculation(arguments["param"])
    return [TextContent(type="text", text=f"Result: {result}")]
```

3. The HTTP wrapper in `http_server.py` automatically exposes it at `/tools/your_tool`

### Testing New Tools

After adding a tool:
```bash
# Rebuild and redeploy
cd mcp-server
gcloud builds submit --tag $(cd ../terraform && terraform output -raw docker_image_name)
cd ../terraform
terraform apply -auto-approve

# Test locally first
cd ../mcp-server/src
python http_server.py  # Terminal 1
curl -X POST http://localhost:8080/tools/your_tool \
  -H "Content-Type: application/json" \
  -d '{"arguments": {"param": 123}}'  # Terminal 2
```

## RBAC System

The project includes a comprehensive RBAC system with:
- **Authentication**: JWT tokens and API keys
- **Authorization**: Role-based permissions (admin, user, viewer)
- **Audit Logging**: Track all operations
- **IP Whitelisting**: Restrict access by IP
- **Rate Limiting**: Prevent abuse

Key files for RBAC:
- `mcp-server/src/auth/models.py`: Database models
- `mcp-server/src/rbac/permissions.py`: Permission decorators
- `mcp-server/src/rbac/roles.py`: Default role initialization

## Streamlit UI Configuration

Important configuration in `ui/config.py`:
- `AGENT_RESOURCE_NAME`: Your Vertex AI agent identifier
- `PROJECT_ID`, `LOCATION`: GCP project settings
- `QUICK_CALCULATIONS`: Pre-configured calculator buttons
- `SAMPLE_QUERIES`: Example customer support scenarios

To update agent connection:
1. Deploy new agent with `agent/deploy_agent.py`
2. Get agent ID from Vertex AI Console
3. Update `AGENT_RESOURCE_NAME` in `ui/config.py`

## Important Notes

### Port Configuration
- MCP server: Always uses port 8080 (Cloud Run requirement in `http_server.py:173`)
- Streamlit UI: Default port 8501 (configurable via `--server.port`)

### Environment Variables
- `PORT`: Cloud Run sets this to 8080 for the MCP server
- `GOOGLE_APPLICATION_CREDENTIALS`: Required for UI to access Vertex AI agent

### Terraform State
- State is stored locally in `terraform/terraform.tfstate` (not in git)
- Use `terraform.tfvars` for project-specific settings (copy from `terraform.tfvars.example`)

### Security
- MCP server requires authentication by default (`enable_public_access = false` in Terraform)
- Service accounts: One for Cloud Run MCP server, one for Vertex AI agent
- Agent calls MCP server with Cloud Run invoker permission

### Cloud Run Image Lifecycle
The image name is ignored after initial deployment (see `terraform/main.tf:112-115`). To update:
1. Build new image: `gcloud builds submit`
2. Apply Terraform: `terraform apply -auto-approve`

## Common Tasks

### Update MCP Server Code
```bash
cd mcp-server
# Make changes to src/calculator_server.py or src/http_server.py
gcloud builds submit --tag $(cd ../terraform && terraform output -raw docker_image_name)
cd ../terraform
terraform apply -auto-approve
```

### View Logs
```bash
# Cloud Run logs
gcloud run services logs read mcp-calculator-server --region us-central1

# Cloud Build logs
gcloud builds list --limit=10
gcloud builds log <BUILD_ID>

# Vertex AI logs
gcloud logging read "resource.type=aiplatform.googleapis.com" --limit=50
```

### Test Agent Integration
Use the Streamlit UI or Vertex AI Console to test agent conversations. The agent automatically calls MCP tools when users ask math questions.

## Project Configuration Files

- `terraform/terraform.tfvars`: GCP project ID, region, service names
- `agent/agent_config.yaml`: Agent model, safety settings
- `ui/config.py`: UI appearance, agent connection, sample queries
- `mcp-server/requirements.txt`: Python dependencies including RBAC libraries
- `Makefile`: Convenience commands for common operations
