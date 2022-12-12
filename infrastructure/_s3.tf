# codebase      --------------------------------------------------------------------------------------------------------
resource "aws_s3_bucket" "codebase-bucket" {
  bucket = "${var.business-name}-codebase"
  acl    = "private"
}

module "codebase-archive" {
  source = "./modules/utils/archive_directory"

  bucket_key  = "codebase/codebase.zip"
  bucket_name = aws_s3_bucket.codebase-bucket.bucket
  output_path = "${path.root}/../codebase.zip"
  source_dir  = "${path.root}/../codebase/"
}

# configuration     ----------------------------------------------------------------------------------------------------
resource "aws_s3_bucket" "configuration-bucket" {
  bucket = "${var.business-name}-configuration"
  acl    = "private"
}

resource "aws_s3_bucket_object" "configuration-uploads" {
  for_each = local.configuration-files
  bucket   = aws_s3_bucket.configuration-bucket.bucket
  key      = each.value
  source   = "${local.repository-layers.configuration}${each.value}"
}

# orchestration     ----------------------------------------------------------------------------------------------------
resource "aws_s3_bucket" "orchestration-bucket" {
  bucket = "${var.business-name}-orchestration"
  acl    = "private"
}

# ToDo: Upload all orchestration files.

# etl     --------------------------------------------------------------------------------------------------------------
resource "aws_s3_bucket" "etl-bucket" {
  bucket = "${var.business-name}-etl"
  acl    = "private"
}

# ToDo: Set up bucket for ETL pipeline

# scripts     ----------------------------------------------------------------------------------------------------------
resource "aws_s3_bucket" "scripts-bucket" {
  bucket = "${var.business-name}-scripts"
  acl    = "private"
}

resource "aws_s3_bucket_object" "scripts-docker-uploads" {
  for_each = local.docker-scripts
  bucket   = aws_s3_bucket.scripts-bucket.bucket
  key      = "docker/${each.value}"
  source   = "${local.repository-layers.scripts}docker/${each.value}"
}

resource "aws_s3_bucket_object" "scripts-spark-uploads" {
  for_each = local.spark-scripts
  bucket   = aws_s3_bucket.scripts-bucket.bucket
  key      = "spark/${each.value}"
  source   = "${local.repository-layers.scripts}spark/${each.value}"
}