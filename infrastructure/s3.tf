locals {
  name_for_s3 = replace(var.project_name, "_", "-")
}

module "etl_buckets" {
  for_each = toset(local.etl_stages)

  source     = "./modules/s3_bucket"
  name       = "${local.name_for_s3}-${each.value}"
  kms_arn    = aws_kms_key.default.arn
  use_case   = "etl"
  sdlc_stage = var.sdlc_stage
}

module "config_bucket" {
  source = "./modules/s3_bucket"

  kms_arn    = aws_kms_key.default.arn
  name       = local.name_for_s3
  sdlc_stage = var.sdlc_stage
  use_case   = "config"
}

module "scripts_bucket" {
  source = "./modules/s3_bucket"

  kms_arn    = aws_kms_key.default.arn
  name       = local.name_for_s3
  sdlc_stage = var.sdlc_stage
  use_case   = "scripts"
}