# Upload BuildSpec
resource "aws_s3_bucket_object" "buildspec-docker" {
  bucket = var.bucket-id
  key    = var.bucket-buildspec-path

  content = templatefile(
    "${path.module}/buildspec.yml.tpl",
    {
      region     = var.region
      account-id = var.account-id
      docker-tag = var.project-name
    }
  )
}

# Create Codebuild
resource "aws_codebuild_project" "codebuild-docker" {
  name          = var.project-name
  description   = "Docker Deployment Project for ${var.project-name}"
  service_role  = var.codebuild-iam-role-arn
  build_timeout = 60

  artifacts {
    type = "NO_ARTIFACTS"
  }

  environment {
    compute_type = var.compute-type
    image        = var.image
    type         = "LINUX_CONTAINER"

    # DinD Runs
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
    location = "s3://${var.bucket-id}/${var.bucket-docker-image-path}"
  }

  vpc_config {
    security_group_ids = var.security-group-ids
    subnets            = var.subnets
    vpc_id             = var.vpc-id
  }
}

# Listen to s3 and build on changes
data "archive_file" "lambda-code" {
  type             = "zip"
  source_file      = "${path.module}/lambda_function.py"
  output_path      = "${path.module}/lambda_function.zip"
  output_file_mode = "0666"
}

resource "aws_lambda_function" "lambda-function" {
  function_name    = var.project-name
  role             = var.lambda-role
  filename         = data.archive_file.lambda-code.output_path
  source_code_hash = data.archive_file.lambda-code.output_base64sha256
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.8"
  timeout          = 120
  memory_size      = 128

  environment {
    variables = {
      codebuild_project_name = var.project-name
    }
  }

  layers = var.lambda-layers
}

# Handle event for multiple uploads
resource "aws_s3_bucket_notification" "put-event" {
  bucket = var.bucket-id
  dynamic "lambda_function" {
    for_each = fileset(var.local-docker-dir, "**/*")
    content {
      lambda_function_arn = aws_lambda_function.lambda-function.arn
      events              = ["s3:ObjectCreated:*"]
      filter_prefix       = var.filter-prefix
    }
  }
}
