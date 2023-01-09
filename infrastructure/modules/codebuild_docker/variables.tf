variable "region" {
  description = "The AWS region where the resources will be created."
  type        = string
}

variable "account-id" {
  description = "The AWS account ID."
  type        = string
}

variable "bucket-id" {
  description = "The name of the S3 bucket."
  type        = string
}

variable "bucket-buildspec-path" {
  description = "The path to the buildspec file in the S3 bucket."
  type        = string
}

variable "project-name" {
  description = "The name of the CodeBuild project."
  type        = string
}

variable "codebuild-iam-role-arn" {
  description = "The IAM role ARN for the CodeBuild project."
  type        = string
}

variable "compute-type" {
  description = "The type of compute to use for the build environment."
  type        = string
  default     = "BUILD_GENERAL1_SMALL"
}

variable "image" {
  description = "The name or ARN of the Docker image to use for the build environment."
  type        = string
  default     = "aws/codebuild/standard:5.0"
}

variable "environment-variables" {
  description = "A map of environment variables to set in the build environment."
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

variable "bucket-docker-image-path" {
  description = "The path to the Docker image in the S3 bucket."
  type        = string
}

variable "security-group-ids" {
  description = "A list of security group IDs to attach to the CodeBuild project's VPC configuration."
  type        = list(string)
}

variable "subnets" {
  description = "A list of subnet IDs to attach to the CodeBuild project's VPC configuration."
  type        = list(string)
}

variable "vpc-id" {
  description = "The ID of the VPC to attach to the CodeBuild project's VPC configuration."
  type        = string
}

variable "lambda-role" {
  description = "The IAM role for the Lambda function."
  type        = string
}

variable "local-docker-dir" {
  description = "The local path to the directory containing the Docker image."
  type        = string
}

variable "lambda-layers" {
  description = "A list of Lambda layer ARNs to attach to the function."
  type        = list(string)
}

variable "filter-prefix" {
  description = "The filter for the rules within the bucket to apply Put Event to."
  type        = string
}