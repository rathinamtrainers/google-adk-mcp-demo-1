variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "region" {
  description = "The GCP region for resources"
  type        = string
  default     = "us-central1"
}

variable "mcp_server_name" {
  description = "Name of the MCP server Cloud Run service"
  type        = string
  default     = "mcp-calculator-server"
}

variable "mcp_server_image" {
  description = "Docker image for MCP server (will be built and pushed to Artifact Registry)"
  type        = string
  default     = ""
}

variable "artifact_registry_repo" {
  description = "Name of the Artifact Registry repository"
  type        = string
  default     = "mcp-servers"
}

variable "vertex_ai_agent_name" {
  description = "Name of the Vertex AI agent"
  type        = string
  default     = "customer-support-agent"
}

variable "vertex_ai_location" {
  description = "Location for Vertex AI resources"
  type        = string
  default     = "us-central1"
}

variable "agent_display_name" {
  description = "Display name for the Vertex AI agent"
  type        = string
  default     = "Customer Support Agent"
}

variable "enable_public_access" {
  description = "Whether to enable public access to the MCP server"
  type        = bool
  default     = false
}

variable "allowed_service_accounts" {
  description = "Service accounts allowed to invoke the MCP server"
  type        = list(string)
  default     = []
}

variable "labels" {
  description = "Labels to apply to all resources"
  type        = map(string)
  default = {
    environment = "production"
    managed-by  = "terraform"
  }
}
