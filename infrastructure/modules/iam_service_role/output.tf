output "role_name" {
  value       = aws_iam_role.role.name
  description = "The name of the IAM role created by this module."
}

output "role_arn" {
  value       = aws_iam_role.role.arn
  description = "The ARN of the IAM role created by this module."
}