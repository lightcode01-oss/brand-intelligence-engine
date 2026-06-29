# =============================================================================
# Nomen — Terraform Variables
# =============================================================================

variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "us-east-1"
}

variable "aws_profile" {
  description = "AWS CLI profile name"
  type        = string
  default     = "default"
}

variable "project" {
  description = "Project name used for resource naming"
  type        = string
  default     = "nomen"
}

variable "environment" {
  description = "Deployment environment (production | staging | development)"
  type        = string

  validation {
    condition     = contains(["production", "staging", "development"], var.environment)
    error_message = "Environment must be one of: production, staging, development."
  }
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets (one per AZ)"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets (one per AZ)"
  type        = list(string)
  default     = ["10.0.10.0/24", "10.0.11.0/24"]
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.medium"
}

variable "db_allocated_storage" {
  description = "RDS allocated storage in GB"
  type        = number
  default     = 100
}

variable "redis_node_type" {
  description = "ElastiCache Redis node type"
  type        = string
  default     = "cache.t3.micro"
}

variable "api_image" {
  description = "Docker image for the API service (e.g. ghcr.io/org/nomen-api:v1.0.0)"
  type        = string
}

variable "web_image" {
  description = "Docker image for the Web service (e.g. ghcr.io/org/nomen-web:v1.0.0)"
  type        = string
}

variable "domain_name" {
  description = "Primary domain name for the application"
  type        = string
  default     = "nomen.ai"
}

variable "tags" {
  description = "Additional resource tags"
  type        = map(string)
  default     = {}
}
