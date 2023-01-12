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

# ToDo create lambda put event trigger