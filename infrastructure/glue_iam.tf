module "jdbc-glue-iam-roles" {
  for_each      = toset(local.etl-stages)
  source        = "./modules/glue_iam_role"
  business-name = var.business-name

  etl-s3-bucket-name      = aws_s3_bucket.etl-bucket.bucket
  script-s3-bucket-name   = aws_s3_bucket.scripts-bucket.bucket
  codebase-s3-bucket-name = aws_s3_bucket.codebase-bucket.bucket

  etl-stage   = each.value
  sdlc-stage  = var.sdlc-stage
  account-id  = data.aws_caller_identity.current.account_id
  region-name = var.region-name

  tracking-table-names = [
    aws_dynamodb_table.jdbc-extract-tracking-table.arn
  ]
}
