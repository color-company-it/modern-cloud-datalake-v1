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

resource "aws_s3_bucket_object" "configs" {
  for_each    = fileset("${path.root}/../configuration/", "*.yml")
  bucket      = module.config_bucket.bucket
  key         = each.key
  source      = "${path.root}/../configuration/${each.key}"
  source_hash = filemd5("${path.root}/../configuration/${each.key}")
}

module "scripts_bucket" {
  source = "./modules/s3_bucket"

  kms_arn    = aws_kms_key.default.arn
  name       = local.name_for_s3
  sdlc_stage = var.sdlc_stage
  use_case   = "scripts"
}

/* Archiving the codebase wheel for glue use */
resource "aws_s3_bucket_object" "codebase" {
  bucket      = module.scripts_bucket.bucket
  key         = "codebase-0.1-py3-none-any.whl"
  source      = "${path.module}/../dist/codebase-0.1-py3-none-any.whl"
  source_hash = filemd5("${path.module}/../dist/codebase-0.1-py3-none-any.whl")
}