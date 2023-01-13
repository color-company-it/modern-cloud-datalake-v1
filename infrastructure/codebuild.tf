/*
This Terraform module creates resources to deploy two Docker images to ECR registry,
one for "base-pyspark" and another for "etl-jdbc". It also triggers two CodeBuild
projects using a Lambda function, one for each image.

It utilizes the codebuild_docker_deploy module to create the CodeBuild projects and
the necessary resources for deployment. Additionally, it creates two S3 bucket objects
for additional source codebase and scripts for the "etl-jdbc" project.
ToDo: Consolidate all resources for the docker to access when required, as opposed to
      bringing them in with the aws_s3_bucket_object resource.
*/

module "codebuild-base-pyspark" {
  source       = "./modules/codebuild_docker_deploy"
  project-name = "${var.business-name}-${var.sdlc-stage}-base-pyspark"
  region-name  = var.region-name
  docker-tag   = "base-pyspark"
  iam-role-arn = aws_iam_role.codebuild-role.arn
  s3-bucket    = aws_s3_bucket.scripts-bucket
  s3-prefix    = "docker/base_pyspark/"
  lambda-role  = aws_iam_role.lambda-role
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
  lambda-role  = aws_iam_role.lambda-role
}
