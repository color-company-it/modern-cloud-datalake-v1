# JDBC      ------------------------------------------------------------------------------------------------------------
module "jdbc-glue-job-v1" {
  for_each = toset(local.etl-stages)
  source   = "./modules/glue_jdbc_job"

  business-name = var.business-name
  etl-stage     = each.value
  sdlc-stage    = var.sdlc-stage
  role-arn      = module.jdbc-glue-iam-roles[each.value].glue_job_policy_arn

  max-concurrent-runs = 1
  script-location     = "S3://${aws_s3_bucket.scripts-bucket.bucket}/spark/jdbc/pipeline_${each.value}_${var.sdlc-stage}_jdbc_1.py"

  connections = []
  depends_on  = [module.jdbc-glue-iam-roles]
}