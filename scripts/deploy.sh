#!/bin/bash
#
# Deploy MCP Server and Vertex AI Agent to Google Cloud
#
# This script automates the deployment of:
# 1. MCP Calculator Server to Cloud Run
# 2. Vertex AI Customer Support Agent
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required commands are available
check_prerequisites() {
    log_info "Checking prerequisites..."

    local missing_deps=()

    command -v gcloud >/dev/null 2>&1 || missing_deps+=("gcloud")
    command -v terraform >/dev/null 2>&1 || missing_deps+=("terraform")
    command -v docker >/dev/null 2>&1 || missing_deps+=("docker")

    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_error "Missing required dependencies: ${missing_deps[*]}"
        echo "Please install missing dependencies and try again."
        exit 1
    fi

    log_success "All prerequisites met"
}

# Get project configuration
get_config() {
    log_info "Loading configuration..."

    # Check if terraform.tfvars exists
    if [ ! -f "../terraform/terraform.tfvars" ]; then
        log_error "terraform.tfvars not found!"
        log_info "Please copy terraform.tfvars.example to terraform.tfvars and fill in your values:"
        echo "  cp terraform/terraform.tfvars.example terraform/terraform.tfvars"
        exit 1
    fi

    # Extract project_id from terraform.tfvars
    PROJECT_ID=$(grep "^project_id" ../terraform/terraform.tfvars | cut -d'=' -f2 | tr -d ' "')
    REGION=$(grep "^region" ../terraform/terraform.tfvars | cut -d'=' -f2 | tr -d ' "' || echo "us-central1")

    if [ -z "$PROJECT_ID" ]; then
        log_error "project_id not set in terraform.tfvars"
        exit 1
    fi

    log_success "Configuration loaded: Project=$PROJECT_ID, Region=$REGION"
}

# Configure gcloud
configure_gcloud() {
    log_info "Configuring gcloud..."

    gcloud config set project "$PROJECT_ID"
    gcloud auth application-default login --quiet || log_warning "Already authenticated"

    log_success "gcloud configured for project: $PROJECT_ID"
}

# Initialize Terraform
init_terraform() {
    log_info "Initializing Terraform..."

    cd ../terraform
    terraform init

    log_success "Terraform initialized"
}

# Apply Terraform configuration
apply_terraform() {
    log_info "Applying Terraform configuration..."

    cd ../terraform
    terraform plan -out=tfplan

    echo ""
    read -p "Apply this Terraform plan? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        log_warning "Terraform apply cancelled"
        exit 0
    fi

    terraform apply tfplan
    rm tfplan

    log_success "Terraform applied successfully"

    # Export outputs
    export ARTIFACT_REGISTRY=$(terraform output -raw artifact_registry_repo_url)
    export MCP_SERVER_URL=$(terraform output -raw mcp_server_url)
    export VERTEX_AI_SA=$(terraform output -raw vertex_ai_agent_service_account)
    export DOCKER_IMAGE=$(terraform output -raw docker_image_name)

    cd ../scripts
}

# Build and push Docker image
build_and_push_image() {
    log_info "Building and pushing Docker image..."

    cd ../mcp-server

    # Configure Docker for Artifact Registry
    gcloud auth configure-docker "${REGION}-docker.pkg.dev" --quiet

    # Build and push using Cloud Build (recommended for production)
    log_info "Building image with Cloud Build..."
    gcloud builds submit \
        --tag "$DOCKER_IMAGE" \
        --project "$PROJECT_ID" \
        --timeout=10m

    log_success "Docker image built and pushed: $DOCKER_IMAGE"

    cd ../scripts
}

# Update Cloud Run service
update_cloud_run() {
    log_info "Updating Cloud Run service with new image..."

    cd ../terraform

    # Trigger Terraform to update the service with the new image
    terraform apply -auto-approve

    MCP_SERVER_URL=$(terraform output -raw mcp_server_url)

    cd ../scripts

    log_success "Cloud Run service updated"
}

# Test MCP server
test_mcp_server() {
    log_info "Testing MCP server..."

    echo ""
    log_info "Health check:"
    curl -s "${MCP_SERVER_URL}/health" | jq '.' || log_warning "Health check failed"

    echo ""
    log_info "Available tools:"
    curl -s "${MCP_SERVER_URL}/tools" | jq '.tools[] | {name, description}' || log_warning "Tools fetch failed"

    echo ""
    log_info "Testing calculator (2 + 2):"
    curl -s -X POST "${MCP_SERVER_URL}/tools/add" \
        -H "Content-Type: application/json" \
        -d '{"arguments": {"a": 2, "b": 2}}' | jq '.' || log_warning "Calculator test failed"

    log_success "MCP server tests completed"
}

# Deploy Vertex AI agent
deploy_agent() {
    log_info "Deploying Vertex AI agent..."

    cd ../agent

    # Install Python dependencies if needed
    if ! python3 -c "import google.cloud.aiplatform" 2>/dev/null; then
        log_info "Installing Python dependencies..."
        pip3 install --user google-cloud-aiplatform pyyaml requests
    fi

    # Run agent deployment script
    python3 deploy_agent.py \
        --project-id "$PROJECT_ID" \
        --location "$REGION" \
        --mcp-server-url "$MCP_SERVER_URL" \
        --service-account "$VERTEX_AI_SA"

    cd ../scripts

    log_success "Agent deployment instructions generated"
}

# Main deployment flow
main() {
    echo ""
    echo "=========================================="
    echo "  MCP + Vertex AI Agent Deployment"
    echo "=========================================="
    echo ""

    check_prerequisites
    get_config
    configure_gcloud

    # Deployment steps
    init_terraform
    apply_terraform
    build_and_push_image
    update_cloud_run
    test_mcp_server
    deploy_agent

    echo ""
    echo "=========================================="
    echo "  Deployment Complete!"
    echo "=========================================="
    echo ""
    echo "MCP Server URL: $MCP_SERVER_URL"
    echo "Vertex AI Agent Service Account: $VERTEX_AI_SA"
    echo ""
    echo "Next steps:"
    echo "1. Complete Vertex AI agent setup using the instructions above"
    echo "2. Test your agent in the Vertex AI Console"
    echo "3. Monitor logs in Cloud Logging"
    echo ""
    log_success "All done!"
}

# Run main function
main "$@"
