output "extract_glue_job_name" {
  value = aws_glue_job.extract_job[*].name
}

#output "transform_glue_job_name" {
#  value = aws_glue_job.transform_job.name
#}
#
#output "load_glue_job_name" {
#  value = aws_glue_job.load_job.name
#}

output "extract_glue_crawler_name" {
  value = aws_glue_crawler.extract_crawler[*].name
}

#output "transform_glue_crawler_name" {
#  value = aws_glue_crawler.transform_crawler.name
#}
#
#output "load_glue_crawler_name" {
#  value = aws_glue_crawler.load_crawler.name
#}
