# =============================================================================
# Nomen — Terraform Outputs
# =============================================================================

output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = aws_subnet.private[*].id
}

output "postgres_endpoint" {
  description = "RDS PostgreSQL connection endpoint"
  value       = aws_db_instance.postgres.endpoint
  sensitive   = false
}

output "postgres_database_url" {
  description = "Full PostgreSQL connection URL (without password)"
  value       = "postgresql+asyncpg://nomen_user:***@${aws_db_instance.postgres.endpoint}/nomen_db"
  sensitive   = false
}

output "redis_endpoint" {
  description = "ElastiCache Redis primary endpoint"
  value       = aws_elasticache_replication_group.redis.primary_endpoint_address
  sensitive   = false
}

output "secrets_manager_arn" {
  description = "ARN of the Secrets Manager secret containing app credentials"
  value       = aws_secretsmanager_secret.app_secrets.arn
}

output "s3_assets_bucket" {
  description = "S3 bucket name for assets"
  value       = aws_s3_bucket.assets.id
}

output "app_security_group_id" {
  description = "Security group ID for application containers"
  value       = aws_security_group.app.id
}

output "alb_security_group_id" {
  description = "Security group ID for the load balancer"
  value       = aws_security_group.alb.id
}

output "nat_gateway_ip" {
  description = "NAT Gateway public IP (whitelist this in external APIs)"
  value       = aws_eip.nat[0].public_ip
}
