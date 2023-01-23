terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "3.0.1"
    }
  }
}

locals {
  docker_image_name = "${var.name}_${var.sdlc_stage}_${var.tag}"
}

resource "aws_ecr_repository" "ecr_repo" {
  name                 = local.docker_image_name
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    source            = var.name
    sdlc_stage        = var.sdlc_stage
    docker_image_name = "${local.docker_image_name}_extract"
  }
}

resource "aws_ecr_repository_policy" "ecr_repo_policy" {
  repository = aws_ecr_repository.ecr_repo.name
  policy     = <<EOF
  {
      "Version": "2008-10-17",
      "Statement": [
          {
              "Sid": "new policy",
              "Effect": "Allow",
              "Principal": "*",
              "Action": [
                  "ecr:GetAuthorizationToken",
                  "ecr:GetDownloadUrlForLayer",
                  "ecr:BatchGetImage",
                  "ecr:BatchCheckLayerAvailability",
                  "ecr:PutImage",
                  "ecr:InitiateLayerUpload",
                  "ecr:UploadLayerPart",
                  "ecr:CompleteLayerUpload",
                  "ecr:DescribeRepositories",
                  "ecr:GetRepositoryPolicy",
                  "ecr:ListImages",
                  "ecr:DeleteRepository",
                  "ecr:BatchDeleteImage",
                  "ecr:SetRepositoryPolicy",
                  "ecr:DeleteRepositoryPolicy"
              ]
          }
      ]
  }
  EOF
}

provider "docker" {
  registry_auth {
    address  = data.aws_ecr_authorization_token.container_registry_token.proxy_endpoint
    username = data.aws_ecr_authorization_token.container_registry_token.user_name
    password = data.aws_ecr_authorization_token.container_registry_token.password
  }
}

data "aws_ecr_authorization_token" "container_registry_token" {}
resource "time_static" "now" {}

resource "docker_image" "docker_image" {
  name = "${aws_ecr_repository.ecr_repo.repository_url}:build-${time_static.now.unix}"

  build {
    context   = var.dockerfile_directory
    build_arg = var.build_args
    label = {
      dir_sha1 = sha1(join("", [for f in fileset(var.dockerfile_directory, "*") : filesha1("${var.dockerfile_directory}/${f}")]))
    }
  }
}

resource "docker_registry_image" "docker_image" {
  name          = docker_image.docker_image.name
  keep_remotely = false
}
