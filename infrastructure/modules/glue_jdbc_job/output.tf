output "job-name" {
  value = aws_glue_job.glue-jdbc-job.name
}

output "execution-property" {
  value = aws_glue_job.glue-jdbc-job.execution_property
}

output "default-arguments" {
  value = aws_glue_job.glue-jdbc-job.default_arguments
}
