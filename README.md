# MCP Calculator Server + Google ADK Agent

A complete solution for deploying a Model Context Protocol (MCP) server with calculator tools to Google Cloud Run and integrating it with a Vertex AI customer support agent using Google's Agent Development Kit (ADK).

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Detailed Setup](#detailed-setup)
- [Deployment](#deployment)
- [Testing](#testing)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [Cost Estimation](#cost-estimation)
- [Security](#security)

## 🎯 Overview

This project demonstrates how to:

1. **Build an MCP Server** - A Python-based MCP server with calculator tools (add, subtract, multiply, divide, percentage, power, sqrt)
2. **Deploy to Cloud Run** - Containerize and deploy the MCP server to Google Cloud Run using Terraform
3. **Create an AI Agent** - Build a customer support chatbot using Google ADK with access to calculator tools
4. **Deploy to Vertex AI** - Deploy the agent to Vertex AI Agent Engine

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Vertex AI Agent Engine                   │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Customer Support Agent (Google ADK)                   │ │
│  │  - Gemini 2.0 Flash                                    │ │
│  │  - Customer support personality                        │ │
│  │  - Function calling enabled                            │ │
│  └────────────────┬───────────────────────────────────────┘ │
│                   │                                           │
└───────────────────┼───────────────────────────────────────────┘
                    │
                    │ HTTPS
                    │
┌───────────────────▼───────────────────────────────────────────┐
│               Google Cloud Run                                 │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  MCP Calculator Server                                   │ │
│  │  - FastAPI HTTP/SSE transport                            │ │
│  │  - Calculator tools (add, subtract, multiply, etc.)      │ │
│  │  - Auto-scaling                                          │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│                    Infrastructure (Terraform)                   │
│  - Artifact Registry                                            │
│  - IAM Service Accounts                                         │
│  - Cloud Run Services                                           │
│  - Vertex AI Resources                                          │
└────────────────────────────────────────────────────────────────┘
```

## ✨ Features

### MCP Server
- **7 Calculator Tools**: add, subtract, multiply, divide, power, sqrt, percentage
- **HTTP/SSE Transport**: Compatible with Cloud Run and Vertex AI
- **Error Handling**: Proper validation and error messages
- **Health Checks**: Built-in health check endpoints
- **Auto-scaling**: Scales to zero when not in use

### Vertex AI Agent
- **Customer Support Personality**: Friendly and helpful chatbot
- **Function Calling**: Uses MCP calculator tools
- **Gemini 2.0 Flash**: Fast and efficient model
- **Safety Settings**: Content filtering enabled
- **Example Conversations**: Pre-configured test scenarios

### Infrastructure
- **Terraform IaC**: All infrastructure defined as code
- **Artifact Registry**: Secure container image storage
- **Service Accounts**: Proper IAM and security
- **Automated Deployment**: One-command deployment

## 📦 Prerequisites

### Required Tools
- **Google Cloud Account** with billing enabled
- **gcloud CLI** (v450.0.0+) - [Install](https://cloud.google.com/sdk/docs/install)
- **Terraform** (v1.5.0+) - [Install](https://developer.hashicorp.com/terraform/install)
- **Docker** (optional, for local testing) - [Install](https://docs.docker.com/get-docker/)
- **Python 3.11+** - [Install](https://www.python.org/downloads/)
- **make** (optional, for convenience)
- **jq** (optional, for testing) - [Install](https://jqlang.github.io/jq/download/)

### Google Cloud APIs to Enable
The Terraform configuration will enable these automatically:
- Cloud Run API
- Artifact Registry API
- Cloud Build API
- Vertex AI API
- IAM API

### Permissions Required
Your GCP account needs these roles:
- `roles/owner` or:
  - `roles/run.admin`
  - `roles/artifactregistry.admin`
  - `roles/iam.serviceAccountAdmin`
  - `roles/cloudbuild.builds.builder`
  - `roles/aiplatform.admin`

## 🚀 Quick Start

### 1. Clone and Configure

```bash
# Clone the repository
cd /path/to/google-adk-mcp

# Copy and edit Terraform variables
cp terraform/terraform.tfvars.example terraform/terraform.tfvars
nano terraform/terraform.tfvars  # Add your project_id
```

### 2. Authenticate with Google Cloud

```bash
# Login to gcloud
gcloud auth login
gcloud auth application-default login

# Set your project
gcloud config set project YOUR_PROJECT_ID
```

### 3. Deploy Everything

```bash
# Option A: Using the deployment script (recommended)
chmod +x scripts/deploy.sh
cd scripts && ./deploy.sh

# Option B: Using Make
make deploy

# Option C: Manual step-by-step (see Detailed Setup below)
```

### 4. Test the MCP Server

```bash
# Using the test script
chmod +x scripts/test-mcp-server.sh
./scripts/test-mcp-server.sh

# Or manually
export MCP_URL=$(cd terraform && terraform output -raw mcp_server_url)
curl $MCP_URL/health
curl $MCP_URL/tools
```

## 📁 Project Structure

```
google-adk-mcp/
├── mcp-server/              # MCP Calculator Server
│   ├── src/
│   │   ├── calculator_server.py   # Core MCP server with tools
│   │   └── http_server.py         # FastAPI HTTP wrapper
│   ├── Dockerfile                 # Container image definition
│   ├── requirements.txt           # Python dependencies
│   └── .dockerignore
│
├── terraform/               # Infrastructure as Code
│   ├── main.tf                    # Main Terraform configuration
│   ├── variables.tf               # Input variables
│   ├── outputs.tf                 # Output values
│   ├── versions.tf                # Provider versions
│   └── terraform.tfvars.example   # Example configuration
│
├── agent/                   # Vertex AI Agent Configuration
│   ├── agent_config.yaml          # Agent configuration
│   ├── deploy_agent.py            # Agent deployment script
│   └── prompts/
│       └── system_prompt.txt      # System instructions
│
├── scripts/                 # Deployment Scripts
│   ├── deploy.sh                  # Main deployment script
│   └── test-mcp-server.sh         # Testing script
│
├── Makefile                 # Convenience commands
└── README.md               # This file
```

## 🔧 Detailed Setup

### Step 1: Configure Terraform Variables

Edit `terraform/terraform.tfvars`:

```hcl
project_id = "your-gcp-project-id"
region     = "us-central1"

# Optional customizations
mcp_server_name      = "mcp-calculator-server"
vertex_ai_agent_name = "customer-support-agent"
agent_display_name   = "Customer Support Agent"

# Security settings
enable_public_access = false  # Keep false for production

labels = {
  environment = "production"
  managed-by  = "terraform"
  project     = "mcp-calculator"
}
```

### Step 2: Initialize Terraform

```bash
cd terraform
terraform init
```

### Step 3: Plan Infrastructure

```bash
terraform plan
```

Review the planned changes. You should see:
- Artifact Registry repository
- 2 Service Accounts
- Cloud Run service
- IAM bindings

### Step 4: Apply Infrastructure

```bash
terraform apply
```

Type `yes` to confirm. This creates all the infrastructure.

### Step 5: Build and Deploy MCP Server

```bash
# Get the image name from Terraform
export DOCKER_IMAGE=$(terraform output -raw docker_image_name)

# Build and push using Cloud Build
cd ../mcp-server
gcloud builds submit --tag $DOCKER_IMAGE
```

### Step 6: Update Cloud Run Service

```bash
cd ../terraform
terraform apply -auto-approve
```

This updates the Cloud Run service with the newly built image.

### Step 7: Deploy Vertex AI Agent

```bash
cd ../agent

# Install Python dependencies
pip install google-cloud-aiplatform pyyaml requests

# Run deployment script
python3 deploy_agent.py \
  --project-id YOUR_PROJECT_ID \
  --location us-central1 \
  --mcp-server-url $(cd ../terraform && terraform output -raw mcp_server_url) \
  --service-account $(cd ../terraform && terraform output -raw vertex_ai_agent_service_account)
```

Follow the output instructions to complete agent setup in Vertex AI Console.

## 🧪 Testing

### Test MCP Server Endpoints

```bash
# Get MCP server URL
export MCP_URL=$(cd terraform && terraform output -raw mcp_server_url)

# Health check
curl $MCP_URL/health

# List available tools
curl $MCP_URL/tools | jq '.'

# Test addition
curl -X POST $MCP_URL/tools/add \
  -H "Content-Type: application/json" \
  -d '{"arguments": {"a": 5, "b": 3}}' | jq '.'

# Test percentage calculation
curl -X POST $MCP_URL/tools/percentage \
  -H "Content-Type: application/json" \
  -d '{"arguments": {"number": 100, "percent": 15}}' | jq '.'
```

### Automated Tests

```bash
# Run all tests
chmod +x scripts/test-mcp-server.sh
./scripts/test-mcp-server.sh
```

### Test Vertex AI Agent

1. Go to [Vertex AI Console](https://console.cloud.google.com/vertex-ai)
2. Navigate to Agent Builder
3. Find your "Customer Support Agent"
4. Use the chat interface to test:

Example conversations:
```
You: Hi! I need help calculating a discount.
Agent: I'd be happy to help with that calculation! What's the original price and discount percentage?

You: The item is $120 and I have a 15% discount code.
Agent: [Uses percentage tool] With a 15% discount on $120, you save $18. Your final price would be $102.
```

## 💻 Development

### Local Development

Run the MCP server locally:

```bash
cd mcp-server
pip install -r requirements.txt
cd src
python http_server.py
```

The server will be available at `http://localhost:8080`

### Make Commands

```bash
make help        # Show all available commands
make init        # Initialize Terraform
make plan        # Terraform plan
make apply       # Terraform apply
make build       # Build and push Docker image
make deploy      # Full deployment
make test        # Test MCP server
make dev         # Run local development server
make clean       # Clean temporary files
make destroy     # Destroy all infrastructure
```

## 🐛 Troubleshooting

### Common Issues

#### 1. "Permission denied" errors

```bash
# Grant necessary permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member=user:YOUR_EMAIL \
  --role=roles/owner
```

#### 2. Cloud Run service not accessible

```bash
# Check if public access is needed (not recommended for production)
# Edit terraform/terraform.tfvars:
enable_public_access = true

# Then apply
cd terraform && terraform apply
```

#### 3. Docker build fails

```bash
# Authenticate Docker with Artifact Registry
gcloud auth configure-docker us-central1-docker.pkg.dev

# Try building locally first
cd mcp-server
docker build -t test-mcp-server .
docker run -p 8080:8080 test-mcp-server
```

#### 4. Terraform state issues

```bash
# If you need to recreate a resource
cd terraform
terraform state rm google_cloud_run_v2_service.mcp_server
terraform apply
```

### Logs and Monitoring

```bash
# View Cloud Run logs
gcloud run services logs read mcp-calculator-server --region us-central1

# View Cloud Build logs
gcloud builds list --limit=10
gcloud builds log <BUILD_ID>

# View Vertex AI logs
gcloud logging read "resource.type=aiplatform.googleapis.com" --limit=50
```

## 💰 Cost Estimation

### Cloud Run
- **Free Tier**: 2 million requests/month
- **Compute**: ~$0.00002400 per vCPU-second
- **Memory**: ~$0.00000250 per GiB-second
- **Requests**: ~$0.40 per million requests
- **Estimated**: $0-10/month for low-moderate usage

### Artifact Registry
- **Storage**: $0.10 per GB/month
- **Estimated**: $0.10-1/month

### Vertex AI
- **Gemini 2.0 Flash**: ~$0.075 per 1M input tokens
- **Agent Engine**: Preview pricing (check latest)
- **Estimated**: $10-50/month depending on usage

### Total Estimated Cost
- **Low usage**: $10-20/month
- **Moderate usage**: $20-60/month
- **High usage**: $60-200/month

## 🔒 Security

### Best Practices Implemented

1. **No Public Access**: MCP server requires authentication by default
2. **Service Accounts**: Dedicated service accounts with minimal permissions
3. **IAM**: Proper role-based access control
4. **HTTPS Only**: All traffic encrypted
5. **Content Safety**: Vertex AI safety settings enabled
6. **Input Validation**: All calculator inputs validated

### Security Checklist

- [ ] Review IAM permissions
- [ ] Keep `enable_public_access = false`
- [ ] Use VPC Service Controls for production
- [ ] Enable Cloud Armor for DDoS protection
- [ ] Set up Cloud Logging and Monitoring
- [ ] Configure alerting for unusual activity
- [ ] Regularly update dependencies
- [ ] Use secret manager for sensitive data

## 📚 Additional Resources

- [MCP Documentation](https://modelcontextprotocol.io/)
- [Google Cloud Run Docs](https://cloud.google.com/run/docs)
- [Vertex AI Agent Builder](https://cloud.google.com/vertex-ai/docs/generative-ai/agent-builder)
- [Terraform Google Provider](https://registry.terraform.io/providers/hashicorp/google/latest/docs)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📄 License

This project is provided as-is for educational and demonstration purposes.

## ✅ Next Steps

After deployment:

1. ✅ Test the MCP server endpoints
2. ✅ Complete Vertex AI agent setup
3. ✅ Test the agent with sample conversations
4. ✅ Monitor costs in GCP Console
5. ✅ Set up alerts and monitoring
6. ✅ Customize agent personality and tools
7. ✅ Add more calculator tools as needed
8. ✅ Integrate with your application

---

**Built with ❤️ using Google Cloud, Vertex AI, and MCP**
