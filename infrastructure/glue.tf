# JDBC      ------------------------------------------------------------------------------------------------------------
module "jdbc-glue-job-v1" {
  for_each = toset(local.etl-stages)
  source   = "./modules/glue_jdbc_job"

  business-name = var.business-name
  etl-stage     = each.value
  sdlc-stage    = var.sdlc-stage
  role-arn      = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${var.business-name}-${each.value}-${var.sdlc-stage}-glue-job-role"

  max-concurrent-runs = 5
  script-location     = "s3://${aws_s3_bucket.scripts-bucket.bucket}/glue/jdbc_${var.sdlc-stage}_${each.value}_job.py"
  codebase            = "s3://${aws_s3_bucket_object.codebase-whl.bucket}/${aws_s3_bucket_object.codebase-whl.key}"
  tracking-table-name = aws_dynamodb_table.jdbc-extract-tracking-table.name
  connections         = []
  depends_on          = [module.jdbc-glue-iam-roles, aws_dynamodb_table.jdbc-extract-tracking-table]
}
