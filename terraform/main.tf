# Configure GCP Provider
provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "run.googleapis.com",
    "artifactregistry.googleapis.com",
    "cloudbuild.googleapis.com",
    "aiplatform.googleapis.com",
    "iam.googleapis.com",
  ])

  project = var.project_id
  service = each.value

  disable_on_destroy = false
}

# Create Artifact Registry Repository for Docker images
resource "google_artifact_registry_repository" "mcp_repo" {
  location      = var.region
  repository_id = var.artifact_registry_repo
  description   = "Docker repository for MCP servers"
  format        = "DOCKER"

  labels = var.labels

  depends_on = [google_project_service.required_apis]
}

# Service Account for Cloud Run MCP Server
resource "google_service_account" "mcp_server_sa" {
  account_id   = "${var.mcp_server_name}-sa"
  display_name = "Service Account for MCP Calculator Server"
  description  = "Used by Cloud Run service for MCP calculator server"

  depends_on = [google_project_service.required_apis]
}

# Cloud Run Service for MCP Server
resource "google_cloud_run_v2_service" "mcp_server" {
  name     = var.mcp_server_name
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  labels = var.labels

  template {
    service_account = google_service_account.mcp_server_sa.email

    containers {
      # Image will be updated after initial build
      image = var.mcp_server_image != "" ? var.mcp_server_image : "${var.region}-docker.pkg.dev/${var.project_id}/${var.artifact_registry_repo}/mcp-calculator:latest"

      ports {
        container_port = 8080
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
        cpu_idle = true
      }

      # Health check configuration
      startup_probe {
        http_get {
          path = "/health"
          port = 8080
        }
        initial_delay_seconds = 0
        timeout_seconds       = 1
        period_seconds        = 3
        failure_threshold     = 3
      }

      liveness_probe {
        http_get {
          path = "/health"
          port = 8080
        }
        initial_delay_seconds = 0
        timeout_seconds       = 1
        period_seconds        = 10
        failure_threshold     = 3
      }
    }

    scaling {
      min_instance_count = 0
      max_instance_count = 10
    }
  }

  depends_on = [
    google_project_service.required_apis,
    google_artifact_registry_repository.mcp_repo
  ]

  lifecycle {
    ignore_changes = [
      template[0].containers[0].image,
    ]
  }
}

# IAM policy for Cloud Run service
resource "google_cloud_run_v2_service_iam_member" "public_access" {
  count = var.enable_public_access ? 1 : 0

  name     = google_cloud_run_v2_service.mcp_server.name
  location = google_cloud_run_v2_service.mcp_server.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# IAM policy for specific service accounts
resource "google_cloud_run_v2_service_iam_member" "authorized_invokers" {
  for_each = toset(var.allowed_service_accounts)

  name     = google_cloud_run_v2_service.mcp_server.name
  location = google_cloud_run_v2_service.mcp_server.location
  role     = "roles/run.invoker"
  member   = "serviceAccount:${each.value}"
}

# Service Account for Vertex AI Agent
resource "google_service_account" "vertex_ai_agent_sa" {
  account_id   = "${var.vertex_ai_agent_name}-sa"
  display_name = "Service Account for Vertex AI Customer Support Agent"
  description  = "Used by Vertex AI agent to call MCP server"

  depends_on = [google_project_service.required_apis]
}

# Grant Vertex AI Agent permission to invoke MCP server
resource "google_cloud_run_v2_service_iam_member" "vertex_agent_invoker" {
  name     = google_cloud_run_v2_service.mcp_server.name
  location = google_cloud_run_v2_service.mcp_server.location
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.vertex_ai_agent_sa.email}"
}

# Grant Vertex AI Agent necessary permissions
resource "google_project_iam_member" "vertex_agent_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.vertex_ai_agent_sa.email}"
}

# Note: Vertex AI Agent Engine is in preview and may not have full Terraform support
# The agent configuration will be handled via gcloud commands in the deployment script
# This is a placeholder for when Vertex AI Agent Engine has full Terraform support

# Placeholder outputs for agent configuration
locals {
  mcp_server_url = google_cloud_run_v2_service.mcp_server.uri
  agent_config = {
    name               = var.vertex_ai_agent_name
    display_name       = var.agent_display_name
    service_account    = google_service_account.vertex_ai_agent_sa.email
    mcp_server_url     = local.mcp_server_url
    location           = var.vertex_ai_location
  }
}
