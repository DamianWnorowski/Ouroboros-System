# Ouroboros System - Terraform Configuration
# Infrastructure as Code

terraform {
  required_version = ">= 1.5.0"
  
  required_providers {
    # Add your cloud provider here
    # Example for AWS:
    # aws = {
    #   source  = "hashicorp/aws"
    #   version = "~> 5.0"
    # }
  }
  
  # Uncomment and configure for remote state
  # backend "s3" {
  #   bucket = "ouroboros-terraform-state"
  #   key    = "ouroboros/terraform.tfstate"
  #   region = "us-east-1"
  # }
}

# Variables
variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "region" {
  description = "AWS/GCP/Azure region"
  type        = string
  default     = "us-east-1"
}

# Outputs
output "orchestrator_endpoint" {
  description = "Orchestrator service endpoint"
  value       = "Configure based on your cloud provider"
}

