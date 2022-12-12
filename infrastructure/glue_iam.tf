module "jdbc-glue-iam-roles" {
  for_each = toset(local.etl-stages)


  source               = "./modules/glue_iam_role"
  business-name        = var.business-name
  etl-s3-bucket-arn    = aws_s3_bucket.etl-bucket.arn
  etl-stage            = each.value
  script-s3-bucket-arn = aws_s3_bucket.scripts-bucket.arn
  sdlc-stage           = var.sdlc-stage
}