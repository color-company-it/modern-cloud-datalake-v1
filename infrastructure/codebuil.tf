resource "aws_security_group" "codebuild-egress" {
  name   = "${var.business-name}-${var.sdlc-stage}-codebuild-sg"
  vpc_id = aws_vpc.datalake.id

  egress {
    description = "Allows all outbound traffic to allow dependency installations"
    from_port   = 0
    to_port     = 0
    protocol    = -1
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    sdlc-stage   = var.sdlc-stage
    company-name = var.business-name
  }

}

module "codebuild-base-pyspark" {
  source       = "./modules/codebuild_docker"
  project-name = "${var.business-name}-${var.sdlc-stage}-base-pyspark"

  account-id = data.aws_caller_identity.current.account_id
  region     = var.region-name

  bucket-id                = aws_s3_bucket.scripts-bucket.id
  bucket-buildspec-path    = "docker/base_pyspark"
  bucket-docker-image-path = "docker/base_pyspark"
  local-docker-dir         = "${local.repository-layers.scripts}docker/base_pyspark"
  filter-prefix            = "docker/base_pyspark"

  lambda-layers          = [aws_lambda_layer_version.datalake-layer.arn, aws_lambda_layer_version.codebase-layer.arn]
  lambda-role            = aws_iam_role.lambda-role.arn
  codebuild-iam-role-arn = aws_iam_role.codebuild-role.arn
  security-group-ids     = [aws_security_group.codebuild-egress.id, aws_security_group.datalake.id]
  subnets                = [aws_subnet.datalake.id]
  vpc-id                 = aws_vpc.datalake.id
}

module "codebuild-etl-jdbc" {
  source       = "./modules/codebuild_docker"
  project-name = "${var.business-name}-${var.sdlc-stage}-etl-jdbc"

  account-id = data.aws_caller_identity.current.account_id
  region     = var.region-name

  bucket-id                = aws_s3_bucket.scripts-bucket.id
  bucket-buildspec-path    = "docker/etl_jdbc"
  bucket-docker-image-path = "docker/etl_jdbc"
  local-docker-dir         = "${local.repository-layers.scripts}docker/etl_jdbc"
  filter-prefix            = "docker/etl_jdbc"

  lambda-layers          = [aws_lambda_layer_version.datalake-layer.arn, aws_lambda_layer_version.codebase-layer.arn]
  lambda-role            = aws_iam_role.lambda-role.arn
  codebuild-iam-role-arn = aws_iam_role.codebuild-role.arn
  security-group-ids     = [aws_security_group.codebuild-egress.id, aws_security_group.datalake.id]
  subnets                = [aws_subnet.datalake.id]
  vpc-id                 = aws_vpc.datalake.id
}
