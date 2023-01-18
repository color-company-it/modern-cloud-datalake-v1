output "extract_glue_job_name" {
  value = aws_glue_job.extract_job.*.name
}

output "transform_glue_job_name" {
  value = aws_glue_job.transform_job.*.name
}

output "load_glue_job_name" {
  value = aws_glue_job.load_job.*.name
}

output "extract_glue_job_id" {
  value = aws_glue_job.extract_job.*.id
}

output "transform_glue_job_id" {
  value = aws_glue_job.transform_job.*.id
}

output "load_glue_job_id" {
  value = aws_glue_job.load_job.*.id
}

output "extract_glue_job_arn" {
  value = aws_glue_job.extract_job.*.arn
}

output "transform_glue_job_arn" {
  value = aws_glue_job.transform_job.*.arn
}

output "load_glue_job_arn" {
  value = aws_glue_job.load_job.*.arn
}