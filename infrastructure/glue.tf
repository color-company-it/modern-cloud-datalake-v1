# JDBC      ------------------------------------------------------------------------------------------------------------
module "jdbc-glue-job-v1" {
  for_each = toset(local.etl-stages)
  source   = "./modules/glue_jdbc_job"

  business-name = var.business-name
  etl-stage     = each.value
  sdlc-stage    = var.sdlc-stage
  role-arn      = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${var.business-name}-${each.value}-${var.sdlc-stage}-glue-job-role"

  max-concurrent-runs = 1
  script-location     = "s3://${aws_s3_bucket.scripts-bucket.bucket}/spark/jdbc/pipeline_${each.value}_${var.sdlc-stage}_jdbc_1.py"
  codebase            = module.codebase-archive.object_uri
  connections         = []
  depends_on          = [module.jdbc-glue-iam-roles]
}
