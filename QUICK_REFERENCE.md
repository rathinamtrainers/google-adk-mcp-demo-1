# Quick Reference

Handy command reference for working with the MCP Calculator Server and Vertex AI Agent.

## Quick Deploy

```bash
# One-command deployment
cd scripts && ./deploy.sh

# Or with Make
make deploy
```

## Environment Setup

```bash
# Set your project
export PROJECT_ID="your-project-id"
gcloud config set project $PROJECT_ID

# Get MCP server URL
export MCP_URL=$(cd terraform && terraform output -raw mcp_server_url)

# Get service account
export SA_EMAIL=$(cd terraform && terraform output -raw vertex_ai_agent_service_account)
```

## Terraform Commands

```bash
cd terraform

# Initialize
terraform init

# Validate configuration
terraform validate

# Format files
terraform fmt

# Plan changes
terraform plan

# Apply changes
terraform apply

# Show outputs
terraform output

# Show specific output
terraform output mcp_server_url

# Destroy everything
terraform destroy

# List resources
terraform state list

# Remove specific resource from state
terraform state rm RESOURCE_NAME
```

## MCP Server Testing

```bash
# Health check
curl $MCP_URL/health | jq '.'

# List tools
curl $MCP_URL/tools | jq '.'

# Test addition (2 + 2)
curl -X POST $MCP_URL/tools/add \
  -H "Content-Type: application/json" \
  -d '{"arguments": {"a": 2, "b": 2}}' | jq '.'

# Test subtraction (10 - 3)
curl -X POST $MCP_URL/tools/subtract \
  -H "Content-Type: application/json" \
  -d '{"arguments": {"a": 10, "b": 3}}' | jq '.'

# Test multiplication (5 × 6)
curl -X POST $MCP_URL/tools/multiply \
  -H "Content-Type: application/json" \
  -d '{"arguments": {"a": 5, "b": 6}}' | jq '.'

# Test division (100 ÷ 4)
curl -X POST $MCP_URL/tools/divide \
  -H "Content-Type: application/json" \
  -d '{"arguments": {"a": 100, "b": 4}}' | jq '.'

# Test percentage (15% of 100)
curl -X POST $MCP_URL/tools/percentage \
  -H "Content-Type: application/json" \
  -d '{"arguments": {"number": 100, "percent": 15}}' | jq '.'

# Test power (2^8)
curl -X POST $MCP_URL/tools/power \
  -H "Content-Type: application/json" \
  -d '{"arguments": {"base": 2, "exponent": 8}}' | jq '.'

# Test square root (√64)
curl -X POST $MCP_URL/tools/sqrt \
  -H "Content-Type: application/json" \
  -d '{"arguments": {"number": 64}}' | jq '.'

# Run all tests
./scripts/test-mcp-server.sh
```

## Docker/Container Commands

```bash
# Get image name
export IMAGE=$(cd terraform && terraform output -raw docker_image_name)

# Build locally
cd mcp-server
docker build -t mcp-calculator:local .

# Run locally
docker run -p 8080:8080 mcp-calculator:local

# Build and push with Cloud Build
gcloud builds submit --tag $IMAGE

# List images in Artifact Registry
gcloud artifacts docker images list \
  us-central1-docker.pkg.dev/$PROJECT_ID/mcp-servers

# Configure Docker auth
gcloud auth configure-docker us-central1-docker.pkg.dev
```

## Cloud Run Commands

```bash
# List services
gcloud run services list --region us-central1

# Describe service
gcloud run services describe mcp-calculator-server \
  --region us-central1

# View logs (live)
gcloud run services logs tail mcp-calculator-server \
  --region us-central1

# View logs (recent 50)
gcloud run services logs read mcp-calculator-server \
  --region us-central1 \
  --limit=50

# Update service (manual)
gcloud run deploy mcp-calculator-server \
  --image $IMAGE \
  --region us-central1

# Delete service
gcloud run services delete mcp-calculator-server \
  --region us-central1
```

## Vertex AI Commands

```bash
# List agents
gcloud ai agents list --region us-central1

# Describe agent
gcloud ai agents describe AGENT_ID --region us-central1

# Deploy agent (using Python script)
cd agent
python3 deploy_agent.py \
  --project-id $PROJECT_ID \
  --location us-central1 \
  --mcp-server-url $MCP_URL \
  --service-account $SA_EMAIL

# View Vertex AI logs
gcloud logging read \
  "resource.type=aiplatform.googleapis.com" \
  --limit=50
```

## IAM Commands

```bash
# List service accounts
gcloud iam service-accounts list

# Describe service account
gcloud iam service-accounts describe $SA_EMAIL

# Grant Cloud Run invoker role
gcloud run services add-iam-policy-binding mcp-calculator-server \
  --region us-central1 \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/run.invoker"

# View IAM policy
gcloud projects get-iam-policy $PROJECT_ID
```

## Monitoring & Logs

```bash
# Cloud Run logs
gcloud logging read \
  "resource.type=cloud_run_revision" \
  --limit=50 \
  --format=json

# Cloud Build logs
gcloud builds list --limit=10
gcloud builds log BUILD_ID

# View errors only
gcloud logging read \
  "resource.type=cloud_run_revision AND severity>=ERROR" \
  --limit=20

# Stream logs
gcloud logging tail \
  "resource.type=cloud_run_revision"
```

## Cost Management

```bash
# View current month costs
gcloud billing accounts list

# Export billing data (if configured)
gcloud billing projects describe $PROJECT_ID

# Check quotas
gcloud compute project-info describe \
  --project $PROJECT_ID
```

## Local Development

```bash
# Install Python dependencies
cd mcp-server
pip install -r requirements.txt

# Run server locally
cd src
python http_server.py

# Run with auto-reload
uvicorn http_server:app --reload --host 0.0.0.0 --port 8080

# Test locally
curl http://localhost:8080/health
curl http://localhost:8080/tools
```

## Make Commands

```bash
make help        # Show all commands
make init        # Initialize Terraform
make plan        # Terraform plan
make apply       # Terraform apply
make build       # Build and push image
make deploy      # Full deployment
make test        # Test MCP server
make dev         # Run local dev server
make clean       # Clean temp files
make destroy     # Destroy infrastructure
make fmt         # Format Terraform files
make validate    # Validate Terraform
```

## Common Workflows

### Full Deployment from Scratch

```bash
# 1. Set up configuration
cp terraform/terraform.tfvars.example terraform/terraform.tfvars
nano terraform/terraform.tfvars  # Edit with your project_id

# 2. Authenticate
gcloud auth login
gcloud auth application-default login

# 3. Deploy everything
make deploy

# 4. Test
make test
```

### Update MCP Server Code

```bash
# 1. Make changes to mcp-server/src/

# 2. Rebuild and redeploy
make build

# 3. Update Cloud Run
cd terraform && terraform apply -auto-approve

# 4. Test
make test
```

### Update Terraform Configuration

```bash
# 1. Make changes to terraform/*.tf files

# 2. Plan changes
make plan

# 3. Apply changes
make apply
```

### Troubleshooting

```bash
# View all logs
gcloud run services logs read mcp-calculator-server --limit=100

# Check service health
curl $(cd terraform && terraform output -raw mcp_server_url)/health

# Rebuild from scratch
make destroy
make deploy

# Check Terraform state
cd terraform
terraform state list
terraform show
```

### Complete Cleanup

```bash
# Delete all resources
make destroy

# Clean local files
make clean

# Remove Terraform state (careful!)
rm -rf terraform/.terraform
rm -f terraform/*.tfstate*
```

## Environment Variables

```bash
# Set common variables
export PROJECT_ID=$(gcloud config get-value project)
export REGION="us-central1"
export MCP_URL=$(cd terraform && terraform output -raw mcp_server_url)
export SA_EMAIL=$(cd terraform && terraform output -raw vertex_ai_agent_service_account)
export IMAGE=$(cd terraform && terraform output -raw docker_image_name)

# Save to file
cat > .env <<EOF
PROJECT_ID=$PROJECT_ID
REGION=$REGION
MCP_URL=$MCP_URL
SA_EMAIL=$SA_EMAIL
IMAGE=$IMAGE
EOF

# Load from file
source .env
```

## Useful Aliases

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
alias tf='terraform'
alias tfa='terraform apply'
alias tfp='terraform plan'
alias tfo='terraform output'
alias gcr='gcloud run'
alias gcl='gcloud logging'
alias gca='gcloud ai'

# Project-specific
alias mcp-logs='gcloud run services logs read mcp-calculator-server --region us-central1'
alias mcp-health='curl $(cd terraform && terraform output -raw mcp_server_url)/health'
alias mcp-test='cd scripts && ./test-mcp-server.sh'
```

## API Endpoints Summary

| Endpoint | Method | Purpose | Example |
|----------|--------|---------|---------|
| `/health` | GET | Health check | `curl $MCP_URL/health` |
| `/` | GET | Service info | `curl $MCP_URL/` |
| `/tools` | GET | List all tools | `curl $MCP_URL/tools` |
| `/tools/{name}` | POST | Call specific tool | `curl -X POST $MCP_URL/tools/add -d '{...}'` |
| `/execute` | POST | Execute tool (MCP format) | `curl -X POST $MCP_URL/execute -d '{...}'` |

## Calculator Tools Summary

| Tool | Parameters | Example |
|------|------------|---------|
| `add` | a, b | `{"a": 5, "b": 3}` → 8 |
| `subtract` | a, b | `{"a": 10, "b": 3}` → 7 |
| `multiply` | a, b | `{"a": 6, "b": 7}` → 42 |
| `divide` | a, b | `{"a": 100, "b": 4}` → 25 |
| `power` | base, exponent | `{"base": 2, "exponent": 8}` → 256 |
| `sqrt` | number | `{"number": 64}` → 8 |
| `percentage` | number, percent | `{"number": 100, "percent": 15}` → 15 |

---

**Keep this handy for quick reference! 📌**
