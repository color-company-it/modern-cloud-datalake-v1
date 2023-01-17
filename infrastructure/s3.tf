module "etl_buckets" {
  for_each = toset(local.etl_stages)

  source     = "./modules/s3_bucket"
  name       = "${var.project_name}-${each.value}"
  kms_arn    = aws_kms_key.default.arn
  use_case   = "etl"
  sdlc_stage = var.sdlc_stage
}