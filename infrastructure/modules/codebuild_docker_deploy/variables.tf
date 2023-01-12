variable "region-name" {}

variable "s3-bucket" {
}

variable "s3-prefix" {
  type = string
}

variable "docker-tag" {
  type = string
}

variable "project-name" {
  type = string
}

variable "iam-role-arn" {
  type = string
}

variable "compute-type" {
  type    = string
  default = "BUILD_GENERAL1_SMALL"
}

variable "build-image" {
  type    = string
  default = "aws/codebuild/standard:5.0"
}

variable "environment-type" {
  type    = string
  default = "LINUX_CONTAINER"
}

variable "environment-variables" {
  type = list(object({
    name  = string
    value = string
  }))

  default = [
    {
      name  = "NO_ADDITIONAL_BUILD_VARS"
      value = "TRUE"
    }
  ]
}

variable "tags" {
  type = map(string)
}
