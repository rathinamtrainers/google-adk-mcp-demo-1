output "mcp_server_url" {
  description = "URL of the deployed MCP server on Cloud Run"
  value       = google_cloud_run_v2_service.mcp_server.uri
}

output "mcp_server_name" {
  description = "Name of the Cloud Run service"
  value       = google_cloud_run_v2_service.mcp_server.name
}

output "artifact_registry_repo_url" {
  description = "URL of the Artifact Registry repository"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${var.artifact_registry_repo}"
}

output "mcp_server_service_account" {
  description = "Email of the MCP server service account"
  value       = google_service_account.mcp_server_sa.email
}

output "vertex_ai_agent_service_account" {
  description = "Email of the Vertex AI agent service account"
  value       = google_service_account.vertex_ai_agent_sa.email
}

output "agent_configuration" {
  description = "Configuration details for Vertex AI agent"
  value = {
    name            = var.vertex_ai_agent_name
    display_name    = var.agent_display_name
    service_account = google_service_account.vertex_ai_agent_sa.email
    mcp_server_url  = google_cloud_run_v2_service.mcp_server.uri
    location        = var.vertex_ai_location
  }
}

output "docker_image_name" {
  description = "Full Docker image name for MCP server"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${var.artifact_registry_repo}/mcp-calculator:latest"
}

output "next_steps" {
  description = "Next steps after Terraform apply"
  value = <<-EOT

  Next Steps:
  ===========
  1. Build and push the Docker image:
     cd ../mcp-server
     gcloud builds submit --tag ${var.region}-docker.pkg.dev/${var.project_id}/${var.artifact_registry_repo}/mcp-calculator:latest

  2. Update Cloud Run service with the new image (Terraform lifecycle will handle this)

  3. Deploy the Vertex AI agent using the deployment script:
     cd ../scripts
     ./deploy-agent.sh

  4. Test the MCP server:
     curl ${google_cloud_run_v2_service.mcp_server.uri}/health
     curl ${google_cloud_run_v2_service.mcp_server.uri}/tools

  EOT
}
