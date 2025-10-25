# Setup Guide

Complete step-by-step guide for setting up the MCP Calculator Server and Vertex AI Agent.

## Prerequisites Installation

### 1. Install gcloud CLI

**macOS:**
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

**Linux:**
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

**Windows:**
Download and run the installer from: https://cloud.google.com/sdk/docs/install

### 2. Install Terraform

**macOS:**
```bash
brew tap hashicorp/tap
brew install hashicorp/tap/terraform
```

**Linux:**
```bash
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform
```

**Windows:**
Download from: https://www.terraform.io/downloads

### 3. Install Python 3.11+

**macOS:**
```bash
brew install python@3.11
```

**Linux:**
```bash
sudo apt update
sudo apt install python3.11 python3.11-pip
```

**Windows:**
Download from: https://www.python.org/downloads/

### 4. Install Docker (Optional, for local testing)

**macOS/Windows:**
Install Docker Desktop from: https://www.docker.com/products/docker-desktop

**Linux:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

### 5. Install jq (for testing)

**macOS:**
```bash
brew install jq
```

**Linux:**
```bash
sudo apt install jq
```

**Windows:**
Download from: https://jqlang.github.io/jq/download/

## Google Cloud Project Setup

### 1. Create a New Project (or use existing)

```bash
# Create new project
gcloud projects create YOUR_PROJECT_ID --name="MCP Calculator"

# Or list existing projects
gcloud projects list

# Set the project
gcloud config set project YOUR_PROJECT_ID
```

### 2. Enable Billing

```bash
# List billing accounts
gcloud billing accounts list

# Link project to billing account
gcloud billing projects link YOUR_PROJECT_ID \
  --billing-account=BILLING_ACCOUNT_ID
```

### 3. Enable Required APIs

The Terraform will enable these, but you can do it manually:

```bash
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  aiplatform.googleapis.com \
  iam.googleapis.com
```

### 4. Set Up Authentication

```bash
# Login to gcloud
gcloud auth login

# Set up application default credentials
gcloud auth application-default login

# Verify authentication
gcloud auth list
```

## Project Configuration

### 1. Clone/Navigate to Project

```bash
cd /home/agenticai/google-adk-mcp
```

### 2. Configure Terraform Variables

```bash
# Copy example file
cp terraform/terraform.tfvars.example terraform/terraform.tfvars

# Edit with your details
nano terraform/terraform.tfvars
```

Required changes in `terraform.tfvars`:
```hcl
project_id = "your-actual-project-id"  # REQUIRED
region     = "us-central1"              # Optional, change if needed
```

### 3. Verify Configuration

```bash
# Check your configuration
cat terraform/terraform.tfvars

# Verify gcloud configuration
gcloud config list
```

## Deployment Steps

### Option 1: Automated Deployment (Recommended)

```bash
# Make script executable
chmod +x scripts/deploy.sh

# Run deployment
cd scripts
./deploy.sh
```

This script will:
1. ✅ Check prerequisites
2. ✅ Initialize Terraform
3. ✅ Create infrastructure
4. ✅ Build Docker image
5. ✅ Deploy to Cloud Run
6. ✅ Test MCP server
7. ✅ Provide agent deployment instructions

### Option 2: Using Makefile

```bash
# From project root
make deploy
```

### Option 3: Manual Step-by-Step

#### Step 1: Initialize Terraform
```bash
cd terraform
terraform init
```

#### Step 2: Plan Infrastructure
```bash
terraform plan
```

Review the output. You should see:
- `google_artifact_registry_repository.mcp_repo` will be created
- `google_service_account.mcp_server_sa` will be created
- `google_service_account.vertex_ai_agent_sa` will be created
- `google_cloud_run_v2_service.mcp_server` will be created
- Various IAM bindings

#### Step 3: Apply Infrastructure
```bash
terraform apply
```

Type `yes` when prompted.

#### Step 4: Build Docker Image
```bash
# Get image name from Terraform
export DOCKER_IMAGE=$(terraform output -raw docker_image_name)

# Authenticate Docker
gcloud auth configure-docker us-central1-docker.pkg.dev

# Build and push
cd ../mcp-server
gcloud builds submit --tag $DOCKER_IMAGE
```

#### Step 5: Update Cloud Run
```bash
cd ../terraform
terraform apply -auto-approve
```

#### Step 6: Test MCP Server
```bash
export MCP_URL=$(terraform output -raw mcp_server_url)

# Health check
curl $MCP_URL/health

# List tools
curl $MCP_URL/tools | jq '.'

# Test calculator
curl -X POST $MCP_URL/tools/add \
  -H "Content-Type: application/json" \
  -d '{"arguments": {"a": 2, "b": 2}}' | jq '.'
```

#### Step 7: Deploy Vertex AI Agent
```bash
cd ../agent

# Install dependencies
pip3 install google-cloud-aiplatform pyyaml requests

# Deploy agent
python3 deploy_agent.py \
  --project-id $(gcloud config get-value project) \
  --location us-central1 \
  --mcp-server-url $MCP_URL \
  --service-account $(cd ../terraform && terraform output -raw vertex_ai_agent_service_account)
```

Follow the output instructions to complete setup in Vertex AI Console.

## Verification

### 1. Verify Infrastructure

```bash
cd terraform

# List all resources
terraform state list

# Check outputs
terraform output
```

Expected outputs:
- `mcp_server_url` - URL of your MCP server
- `vertex_ai_agent_service_account` - Service account email
- `docker_image_name` - Full Docker image path

### 2. Verify Cloud Run Service

```bash
gcloud run services list --region us-central1

gcloud run services describe mcp-calculator-server \
  --region us-central1 \
  --format yaml
```

### 3. Verify Artifact Registry

```bash
gcloud artifacts repositories list --location us-central1

gcloud artifacts docker images list \
  us-central1-docker.pkg.dev/YOUR_PROJECT_ID/mcp-servers
```

### 4. Test MCP Server

```bash
# Run comprehensive tests
chmod +x scripts/test-mcp-server.sh
./scripts/test-mcp-server.sh
```

### 5. Verify Vertex AI Agent

1. Go to: https://console.cloud.google.com/vertex-ai
2. Navigate to "Agent Builder"
3. Look for "customer-support-agent"
4. Test in the chat interface

## Troubleshooting

### Issue: API not enabled

```bash
# Check which APIs are enabled
gcloud services list --enabled

# Enable missing APIs
gcloud services enable SERVICE_NAME
```

### Issue: Permission denied

```bash
# Check your permissions
gcloud projects get-iam-policy YOUR_PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:user:YOUR_EMAIL"

# Grant yourself necessary roles
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member=user:YOUR_EMAIL \
  --role=roles/owner
```

### Issue: Terraform state locked

```bash
# Force unlock (use with caution)
cd terraform
terraform force-unlock LOCK_ID
```

### Issue: Cloud Build timeout

```bash
# Increase timeout
gcloud builds submit --tag $DOCKER_IMAGE --timeout=20m
```

### Issue: Can't access MCP server

```bash
# Check Cloud Run logs
gcloud run services logs read mcp-calculator-server \
  --region us-central1 \
  --limit=50

# Check service status
gcloud run services describe mcp-calculator-server \
  --region us-central1
```

## Next Steps

After successful deployment:

1. **Test the MCP Server**
   - Use the test script: `./scripts/test-mcp-server.sh`
   - Test each calculator tool
   - Verify error handling

2. **Set Up Vertex AI Agent**
   - Follow instructions from `deploy_agent.py` output
   - Configure in Vertex AI Console
   - Test with sample conversations

3. **Monitor and Optimize**
   - Set up Cloud Logging alerts
   - Monitor costs in Billing dashboard
   - Optimize Cloud Run settings

4. **Customize**
   - Add more calculator tools
   - Modify agent personality
   - Adjust resource limits

## Cleanup

To remove all resources and avoid charges:

```bash
# Using Makefile
make destroy

# Or manually
cd terraform
terraform destroy
```

Type `yes` to confirm deletion.

**Note:** This will delete:
- Cloud Run service
- Artifact Registry repository and images
- Service accounts
- All IAM bindings

Billing stops immediately after deletion.

## Support

- Review logs: `gcloud run services logs read SERVICE_NAME`
- Check quotas: `gcloud compute project-info describe --project YOUR_PROJECT_ID`
- GCP Status: https://status.cloud.google.com/
- Terraform docs: https://registry.terraform.io/providers/hashicorp/google/latest/docs

---

**Happy deploying! 🚀**
