module "codebuild-base-pyspark" {
  source       = "./modules/codebuild_docker_deploy"
  project-name = "${var.business-name}-${var.sdlc-stage}-base-pyspark"
  region-name  = var.region-name
  docker-tag   = "base-pyspark"
  iam-role-arn = aws_iam_role.codebuild-role.arn
  s3-bucket    = aws_s3_bucket.scripts-bucket
  s3-prefix    = "docker/base_pyspark/"
  tags         = {}
}

resource "aws_s3_bucket_object" "codebuild-etl-jdbc-additional-source-codebase" {
  for_each = local.codebase-files
  bucket   = aws_s3_bucket.scripts-bucket.bucket
  key      = "docker/etl_jdbc/codebase/${each.value}"
  source   = "${local.repository-layers.codebase}${each.value}"
  etag     = filemd5("${local.repository-layers.codebase}${each.value}")
}

resource "aws_s3_bucket_object" "codebuild-etl-jdbc-additional-source-scripts-spark" {
  for_each = local.spark-jdbc-scripts
  bucket   = aws_s3_bucket.scripts-bucket.bucket
  key      = "docker/etl_jdbc/scripts/spark/${each.value}"
  source   = "${local.repository-layers.scripts}spark/${each.value}"
  etag     = filemd5("${local.repository-layers.scripts}spark/${each.value}")
}

module "codebuild-etl-jdbc" {
  source       = "./modules/codebuild_docker_deploy"
  project-name = "${var.business-name}-${var.sdlc-stage}-etl-jdbc"
  region-name  = var.region-name
  docker-tag   = "etl-jdbc"
  iam-role-arn = aws_iam_role.codebuild-role.arn
  s3-bucket    = aws_s3_bucket.scripts-bucket
  s3-prefix    = "docker/etl_jdbc/"
  tags         = {}
}