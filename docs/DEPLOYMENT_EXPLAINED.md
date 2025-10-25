# Deployment Explained

**Complete Deployment Process from Zero to Production**

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Deployment Overview](#deployment-overview)
3. [Step-by-Step Deployment](#step-by-step-deployment)
4. [Terraform Deep Dive](#terraform-deep-dive)
5. [Troubleshooting](#troubleshooting)
6. [Maintenance](#maintenance)

---

## Prerequisites

### Required Tools

```bash
# 1. Google Cloud SDK
gcloud --version

# 2. Terraform
terraform --version

# 3. Docker
docker --version

# 4. Python 3.10+
python3 --version

# 5. Git
git --version
```

### Required Access

```
✓ Google Cloud Project with billing enabled
✓ Service account with these roles:
  - roles/run.admin (Cloud Run)
  - roles/artifactregistry.admin (Artifact Registry)
  - roles/storage.admin (Cloud Storage)
  - roles/aiplatform.user (Vertex AI)
  - roles/iam.serviceAccountUser
✓ Service account JSON key file
```

---

## Deployment Overview

### Complete Deployment Flow

```
1. GCP Setup
   ├── Create project
   ├── Enable APIs
   ├── Create service account
   └── Download credentials

2. Infrastructure (Terraform)
   ├── Artifact Registry
   ├── Cloud Storage bucket
   ├── Service accounts
   ├── IAM bindings
   └── Cloud Run service (placeholder)

3. MCP Server (Docker)
   ├── Build Docker image
   ├── Push to Artifact Registry
   └── Deploy to Cloud Run

4. AI Agent (Vertex AI)
   ├── Create Python wrapper functions
   ├── Define system instructions
   ├── Deploy to Agent Engine
   └── Test deployment

5. UI (Streamlit)
   ├── Configure agent resource name
   ├── Install dependencies
   └── Launch locally
```

### Timeline

| Phase | Time | Can Fail? |
|-------|------|-----------|
| GCP Setup | 10 min | Yes (permissions) |
| Terraform | 5 min | Yes (API limits, quotas) |
| Docker Build | 3 min | Yes (build errors) |
| Cloud Run Deploy | 2 min | Auto (Terraform watches) |
| Agent Deploy | 5 min | Yes (config errors) |
| UI Setup | 2 min | Yes (dependencies) |
| **Total** | **~30 min** | |

---

## Step-by-Step Deployment

### Phase 1: GCP Project Setup

#### Step 1.1: Create Project

```bash
# Set project ID
export PROJECT_ID="your-project-id"

# Create project
gcloud projects create $PROJECT_ID

# Set as default
gcloud config set project $PROJECT_ID

# Link billing account
gcloud billing projects link $PROJECT_ID \
  --billing-account=YOUR-BILLING-ACCOUNT-ID
```

#### Step 1.2: Enable Required APIs

```bash
gcloud services enable \
  aiplatform.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  cloudresourcemanager.googleapis.com \
  compute.googleapis.com \
  iam.googleapis.com \
  run.googleapis.com \
  storage-api.googleapis.com \
  storage-component.googleapis.com
```

#### Step 1.3: Create Service Account

```bash
# Create service account
gcloud iam service-accounts create deployment-sa \
  --display-name="Deployment Service Account"

# Get service account email
SA_EMAIL=$(gcloud iam service-accounts list \
  --filter="displayName:Deployment Service Account" \
  --format='value(email)')

# Grant roles
for role in \
  "roles/run.admin" \
  "roles/artifactregistry.admin" \
  "roles/storage.admin" \
  "roles/aiplatform.user" \
  "roles/iam.serviceAccountUser" \
  "roles/cloudbuild.builds.editor"
do
  gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="$role"
done

# Download key
gcloud iam service-accounts keys create ~/deployment-key.json \
  --iam-account=$SA_EMAIL
```

#### Step 1.4: Authenticate

```bash
export GOOGLE_APPLICATION_CREDENTIALS=~/deployment-key.json

gcloud auth activate-service-account --key-file=$GOOGLE_APPLICATION_CREDENTIALS
gcloud auth application-default login
```

---

### Phase 2: Infrastructure Deployment (Terraform)

#### Step 2.1: Initialize Terraform

```bash
cd /home/agenticai/google-adk-mcp/terraform

# Initialize
terraform init
```

**What this does:**
- Downloads Google Cloud provider plugin
- Creates `.terraform/` directory
- Prepares backend for state management

#### Step 2.2: Create terraform.tfvars

```bash
cat > terraform.tfvars <<EOF
project_id = "$PROJECT_ID"
region = "us-central1"
vertex_ai_location = "us-central1"
mcp_server_name = "mcp-calculator-server"
artifact_registry_repository = "mcp-servers"
storage_bucket_name = "${PROJECT_ID}-staging"
EOF
```

#### Step 2.3: Plan Infrastructure

```bash
terraform plan
```

**Review output:**
```
Plan: 8 to add, 0 to change, 0 to destroy.

Resources to create:
- google_artifact_registry_repository
- google_storage_bucket
- google_service_account (MCP server)
- google_service_account (Vertex AI agent)
- google_project_iam_member (multiple)
- google_cloud_run_v2_service
```

#### Step 2.4: Apply Infrastructure

```bash
terraform apply

# Type: yes
```

**Expected output:**
```
Apply complete! Resources: 8 added, 0 changed, 0 destroyed.

Outputs:
artifact_registry_repository = "us-central1-docker.pkg.dev/PROJECT/mcp-servers"
mcp_server_url = "https://mcp-calculator-server-HASH-uc.a.run.app"
```

**Note:** Cloud Run service will fail initially (no image yet) - this is expected!

---

### Phase 3: MCP Server Deployment (Docker)

#### Step 3.1: Build Docker Image

```bash
cd /home/agenticai/google-adk-mcp/mcp-server

# Build and push using Cloud Build
gcloud builds submit \
  --tag us-central1-docker.pkg.dev/$PROJECT_ID/mcp-servers/mcp-calculator:latest
```

**What this does:**
1. Uploads source code to Cloud Storage
2. Builds Docker image using Dockerfile
3. Pushes image to Artifact Registry
4. Takes ~2-3 minutes

**Expected output:**
```
DONE
ID: xxx-xxx-xxx
CREATE_TIME: 2025-10-26T00:00:00+00:00
DURATION: 2M30S
SOURCE: ...
IMAGES:
- us-central1-docker.pkg.dev/PROJECT/mcp-servers/mcp-calculator:latest
STATUS: SUCCESS
```

#### Step 3.2: Update Cloud Run

Terraform is configured to watch for image changes. The service will automatically update.

**Verify deployment:**
```bash
# Check Cloud Run service
gcloud run services describe mcp-calculator-server \
  --region=us-central1 \
  --format='value(status.url)'

# Test health endpoint
MCP_URL=$(gcloud run services describe mcp-calculator-server \
  --region=us-central1 --format='value(status.url)')

curl $MCP_URL/health
# Expected: {"status":"healthy"}
```

#### Step 3.3: Enable Public Access (for testing)

```bash
gcloud run services add-iam-policy-binding mcp-calculator-server \
  --region=us-central1 \
  --member="allUsers" \
  --role="roles/run.invoker"
```

**⚠️ For production:** Remove public access and use IAM authentication

---

### Phase 4: AI Agent Deployment (Vertex AI)

#### Step 4.1: Prepare Environment

```bash
cd /home/agenticai/google-adk-mcp/agent

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install google-cloud-aiplatform[agent_engines,langchain]>=1.70.0 requests
```

#### Step 4.2: Update Configuration

Edit `agent/deploy_agent_programmatic.py`:

```python
PROJECT_ID = "your-project-id"
LOCATION = "us-central1"
MCP_SERVER_URL = "https://your-mcp-server-url"
```

#### Step 4.3: Deploy Agent

```bash
export GOOGLE_APPLICATION_CREDENTIALS=~/deployment-key.json

python deploy_agent_programmatic.py
```

**What happens:**
```
1. Testing MCP server connectivity...
   ✅ MCP server is healthy

2. Creating agent with calculator tools...
   ✅ Agent created locally

3. Deploying to Vertex AI Agent Engine...
   This may take a few minutes...
   ✅ Agent deployed successfully!

   Resource Name: projects/XXX/locations/us-central1/reasoningEngines/YYY

4. Testing deployed agent...
   Query: "Hi! I'm buying 3 items at $29.99 each. What's the total?"
   Response: {"output": "The total for 3 items at $29.99 each is $89.97."}

DEPLOYMENT COMPLETE!
```

**Save the resource name!** You'll need it for the UI.

---

### Phase 5: UI Setup (Streamlit)

#### Step 5.1: Configure UI

Edit `ui/config.py`:

```python
PROJECT_ID = "your-project-id"
LOCATION = "us-central1"
AGENT_RESOURCE_NAME = "projects/XXX/locations/us-central1/reasoningEngines/YYY"
GOOGLE_APPLICATION_CREDENTIALS = "~/deployment-key.json"
```

#### Step 5.2: Install Dependencies

```bash
cd /home/agenticai/google-adk-mcp/ui

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

#### Step 5.3: Launch UI

```bash
./run.sh
```

**Expected:**
```
Starting Streamlit UI...
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

---

## Terraform Deep Dive

### Resource: Artifact Registry

**File:** `terraform/main.tf:40-48`

```hcl
resource "google_artifact_registry_repository" "mcp_servers" {
  repository_id = var.artifact_registry_repository
  location      = var.region
  description   = "Docker images for MCP servers"
  format        = "DOCKER"
}
```

**Purpose:** Stores Docker images for MCP server

### Resource: Cloud Storage Bucket

**File:** `terraform/main.tf:50-66`

```hcl
resource "google_storage_bucket" "staging" {
  name          = var.storage_bucket_name
  location      = var.region
  force_destroy = false  # Protect against accidental deletion

  uniform_bucket_level_access = true  # Simplify IAM
  versioning { enabled = false }
}
```

**Purpose:** Stores Vertex AI agent artifacts

### Resource: Service Accounts

**MCP Server SA:**
```hcl
resource "google_service_account" "mcp_server_sa" {
  account_id   = "mcp-server-sa"
  display_name = "MCP Server Service Account"
}
```

**Vertex AI Agent SA:**
```hcl
resource "google_service_account" "vertex_ai_agent_sa" {
  account_id   = "vertex-ai-agent-sa"
  display_name = "Vertex AI Agent Service Account"
}
```

### Resource: Cloud Run Service

**File:** `terraform/main.tf:98-155`

```hcl
resource "google_cloud_run_v2_service" "mcp_server" {
  name     = var.mcp_server_name
  location = var.region

  template {
    service_account = google_service_account.mcp_server_sa.email

    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/${var.artifact_registry_repository}/mcp-calculator:latest"

      ports {
        container_port = 8080
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
        cpu_idle = true  # Scale to zero
      }
    }

    scaling {
      min_instance_count = 0   # Scale to zero
      max_instance_count = 10   # Max replicas
    }
  }

  lifecycle {
    ignore_changes = [
      template[0].containers[0].image  # Allow manual updates
    ]
  }
}
```

**Key configurations:**
- Scale to zero: `min_instance_count = 0`
- Auto-scaling: `max_instance_count = 10`
- Resource limits: 1 vCPU, 512MB RAM
- Lifecycle: Ignores image changes (allows manual Docker pushes)

---

## Troubleshooting

### Issue: Terraform apply fails - "Image not found"

**Cause:** Cloud Run expects Docker image that doesn't exist yet

**Solution:**
```bash
# 1. Build Docker image first
cd mcp-server
gcloud builds submit --tag IMAGE_URL

# 2. Re-run Terraform
cd ../terraform
terraform apply
```

### Issue: Agent deployment fails - "Missing staging bucket"

**Cause:** Vertex AI needs Cloud Storage bucket

**Solution:**
```bash
gsutil mb -p $PROJECT_ID -l us-central1 gs://${PROJECT_ID}-staging
```

### Issue: UI can't connect to agent

**Cause:** Wrong resource name or credentials

**Solution:**
```bash
# 1. Verify resource name
gcloud ai reasoning-engines list --region=us-central1

# 2. Check credentials
ls -l $GOOGLE_APPLICATION_CREDENTIALS

# 3. Test connection
python -c "
from vertexai.agent_engines import AgentEngine
import vertexai

vertexai.init(project='PROJECT_ID', location='us-central1')
agent = AgentEngine(resource_name='RESOURCE_NAME')
print(agent.query(input='test'))
"
```

---

## Maintenance

### Update MCP Server

```bash
cd mcp-server

# 1. Make code changes
vim src/calculator_server.py

# 2. Rebuild image
gcloud builds submit --tag IMAGE_URL

# 3. Cloud Run auto-updates (takes ~1 min)

# 4. Test
curl $MCP_URL/health
```

### Update AI Agent

```bash
cd agent

# 1. Make changes
vim deploy_agent_programmatic.py

# 2. Redeploy
python deploy_agent_programmatic.py

# 3. Update UI config with new resource name
vim ../ui/config.py
```

### Monitor Resources

```bash
# Cloud Run logs
gcloud run services logs read mcp-calculator-server \
  --region=us-central1 \
  --limit=50

# Vertex AI logs
gcloud logging read \
  "resource.type=aiplatform.googleapis.com/ReasoningEngine" \
  --limit=50

# View in Console
https://console.cloud.google.com/run
https://console.cloud.google.com/vertex-ai
```

### Cost Monitoring

```bash
# View billing
gcloud billing projects describe $PROJECT_ID

# Set budget alerts (in Console)
https://console.cloud.google.com/billing/budgets
```

---

## Summary

**Deployment checklist:**

- [ ] GCP project created and configured
- [ ] APIs enabled
- [ ] Service account created with roles
- [ ] Terraform applied successfully
- [ ] Docker image built and pushed
- [ ] Cloud Run service healthy
- [ ] Vertex AI agent deployed
- [ ] UI configured and tested

**Key files:**
- `terraform/main.tf` - Infrastructure definition
- `terraform/terraform.tfvars` - Your configuration
- `mcp-server/Dockerfile` - Container definition
- `agent/deploy_agent_programmatic.py` - Agent deployment
- `ui/config.py` - UI configuration

**Important URLs:**
- Cloud Run: https://console.cloud.google.com/run
- Vertex AI: https://console.cloud.google.com/vertex-ai
- Artifact Registry: https://console.cloud.google.com/artifacts

**Next steps:**
- Enable monitoring and alerting
- Set up CI/CD pipeline
- Configure production authentication
- Add rate limiting
- Implement caching
