.PHONY: help init plan apply deploy build test clean destroy

# Default target
help:
	@echo "Available commands:"
	@echo "  make init       - Initialize Terraform"
	@echo "  make plan       - Run Terraform plan"
	@echo "  make apply      - Apply Terraform configuration"
	@echo "  make build      - Build and push Docker image"
	@echo "  make deploy     - Full deployment (Terraform + Docker + Agent)"
	@echo "  make test       - Test MCP server endpoints"
	@echo "  make clean      - Clean up temporary files"
	@echo "  make destroy    - Destroy all infrastructure (use with caution!)"
	@echo ""
	@echo "Quick start:"
	@echo "  1. cp terraform/terraform.tfvars.example terraform/terraform.tfvars"
	@echo "  2. Edit terraform/terraform.tfvars with your project details"
	@echo "  3. make deploy"

# Initialize Terraform
init:
	@echo "Initializing Terraform..."
	cd terraform && terraform init

# Terraform plan
plan:
	@echo "Running Terraform plan..."
	cd terraform && terraform plan

# Apply Terraform configuration
apply:
	@echo "Applying Terraform configuration..."
	cd terraform && terraform apply

# Build and push Docker image
build:
	@echo "Building and pushing Docker image..."
	@if [ -z "$(PROJECT_ID)" ]; then \
		echo "Error: PROJECT_ID not set. Export it or run 'make deploy'"; \
		exit 1; \
	fi
	cd mcp-server && gcloud builds submit \
		--tag $(shell cd terraform && terraform output -raw docker_image_name) \
		--project $(PROJECT_ID)

# Full deployment
deploy:
	@echo "Running full deployment..."
	@chmod +x scripts/deploy.sh
	cd scripts && ./deploy.sh

# Test MCP server
test:
	@echo "Testing MCP server..."
	@MCP_URL=$(shell cd terraform && terraform output -raw mcp_server_url 2>/dev/null || echo ""); \
	if [ -z "$$MCP_URL" ]; then \
		echo "Error: MCP server not deployed. Run 'make deploy' first."; \
		exit 1; \
	fi; \
	echo "Testing health endpoint..."; \
	curl -s $$MCP_URL/health | jq .; \
	echo ""; \
	echo "Testing tools endpoint..."; \
	curl -s $$MCP_URL/tools | jq '.tools[] | {name, description}'

# Clean temporary files
clean:
	@echo "Cleaning temporary files..."
	rm -rf terraform/.terraform
	rm -f terraform/tfplan
	rm -f terraform/*.tfstate.backup
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

# Destroy infrastructure
destroy:
	@echo "WARNING: This will destroy all infrastructure!"
	@read -p "Are you sure? Type 'yes' to confirm: " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		cd terraform && terraform destroy; \
	else \
		echo "Destruction cancelled."; \
	fi

# Local development server
dev:
	@echo "Starting local MCP server for development..."
	cd mcp-server && python -m pip install -r requirements.txt
	cd mcp-server/src && python http_server.py

# Format Terraform files
fmt:
	@echo "Formatting Terraform files..."
	cd terraform && terraform fmt -recursive

# Validate Terraform configuration
validate:
	@echo "Validating Terraform configuration..."
	cd terraform && terraform validate
