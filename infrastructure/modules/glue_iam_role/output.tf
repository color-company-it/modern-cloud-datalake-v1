output "glue_job_role_arn" {
  value       = aws_iam_role.glue-job-role.arn
  description = "The ARN of the IAM role for the Glue job"
}

output "glue_job_policy_arn" {
  value       = aws_iam_policy.glue-job-policy.arn
  description = "The ARN of the IAM policy for the Glue job"
}