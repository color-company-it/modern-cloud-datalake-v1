resource "aws_ecr_repository" "ecr_repo" {
  name = var.project-name
}

resource "aws_s3_bucket_object" "build-spec" {
  bucket = var.s3-bucket.id
  key    = "${var.s3-prefix}/buildspec.yml"

  content = templatefile("${path.module}/buildspec.yml.tpl",
    {
      docker_tag  = var.docker-tag
      ecr_repo    = aws_ecr_repository.ecr_repo.repository_url
      region_name = var.region-name
    }
  )
}

resource "aws_codebuild_project" "docker-deploy" {
  name          = var.project-name
  build_timeout = 60
  service_role  = var.iam-role-arn

  artifacts {
    type = "NO_ARTIFACTS"
  }

  environment {
    compute_type = var.compute-type
    image        = var.build-image
    type         = var.environment-type

    privileged_mode = true

    dynamic "environment_variable" {
      for_each = var.environment-variables
      content {
        name  = environment_variable.value.name
        value = environment_variable.value.value
      }
    }
  }

  source {
    type     = "S3"
    location = "${var.s3-bucket.bucket}/${var.s3-prefix}"
  }

  tags = var.tags
}

data "archive_file" "codebuild-lambda-script" {
  type             = "zip"
  source_file      = "lambda_function.py"
  output_path      = "lambda_function.zip"
  output_file_mode = "0666"
}

resource "aws_lambda_function" "codebuild-lambda" {
  function_name    = "${var.project-name}-codebuild"
  role             = var.lambda-role
  filename         = data.archive_file.codebuild-lambda-script.output_path
  source_code_hash = filebase64sha256(data.archive_file.codebuild-lambda-script.output_path)
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.8"
  timeout          = 120
  memory_size      = 128

  environment {
    variables = {
      PROJECT_NAME = var.project-name
    }
  }

  layers = var.lambda-layers
}

resource "aws_s3_bucket_notification" "put-event" {
  bucket = var.s3-bucket.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.codebuild-lambda.arn
    events              = ["s3:ObjectCreated:*", "s3:ObjectRemoved:*"]
    filter_prefix       = var.s3-prefix
  }
}