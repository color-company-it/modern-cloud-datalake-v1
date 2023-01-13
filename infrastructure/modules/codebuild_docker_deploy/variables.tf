variable "region-name" {
  description = "The name of the region where the resources should be created."
  type        = string
}

variable "s3-bucket" {
  description = "The S3 bucket where the buildspec.yml file is stored and the source code is located."
  type = object({
    id     = string
    bucket = string
  })
}

variable "s3-prefix" {
  description = "The prefix of the S3 bucket object containing the buildspec.yml and source code files."
  type        = string
}

variable "docker-tag" {
  description = "The tag of the Docker image that will be deployed."
  type        = string
}

variable "project-name" {
  description = "The name of the project."
  type        = string
}

variable "iam-role-arn" {
  description = "The ARN of the IAM role that will be used by CodeBuild."
  type        = string
}

variable "compute-type" {
  description = "The type of compute to use for the CodeBuild project."
  type        = string
  default     = "BUILD_GENERAL1_SMALL"
}

variable "build-image" {
  description = "The image to use for the CodeBuild project."
  type        = string
  default     = "aws/codebuild/standard:5.0"
}

variable "environment-type" {
  description = "The type of environment to use for the CodeBuild project."
  type        = string
  default     = "LINUX_CONTAINER"
}

variable "environment-variables" {
  description = "A list of environment variables to be passed to the CodeBuild project."
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
  description = "List of tags for the Lambda resource"
  type        = map(string)
  default     = {}
}

variable "lambda-role" {
  description = "The role for the S3 put event Lambda that will trigger the Codebuild pipeline"
  type        = string
}

variable "lambda-layers" {
  description = "Additional dependencies for the Lambda that might be required"
  type        = list(string)
  default     = []
}
