# Docker Deployment with CodeBuild and Lambda

This Terraform module deploys a Docker image to Amazon Elastic Container Registry (ECR) using CodeBuild and a Lambda
function.

## Prerequisites

- An AWS account
- A Docker image stored in an S3 bucket
- A build specification (buildspec.yml.tpl) for building and pushing the Docker image to ECR
- Terraform 0.13 or higher

## Components

The following resources are created by this module:

- An S3 bucket object containing the buildspec.yml file
- A CodeBuild project to build and push the Docker image to ECR
- A Lambda function to trigger the CodeBuild project when a new Docker image is uploaded to the S3 bucket
- An S3 bucket notification to invoke the Lambda function when an object is created in the bucket

## Usage

To use this module, add the following code to your Terraform configuration:

```terraform
module "docker-deployment" {
  source = "path/to/module"

  region                 = "aws-region"
  account-id             = "aws-account-id"
  bucket-id              = "s3-bucket-name"
  bucket-buildspec-path  = "path/to/buildspec.yml"
  project-name           = "codebuild-project-name"
  codebuild-iam-role-arn = "arn:aws:iam::1234567890:role/codebuild-role"
  compute-type           = "BUILD_GENERAL1_SMALL"
  image                  = "arn:aws:ecr:region:account-id:repository/image:tag"
  environment-variables  = {
    VAR1 = "value1"
    VAR2 = "value2"
  }
  bucket-docker-image-path = "path/to/docker-image"
  security-group-ids       = ["sg-123456"]
  subnets                  = ["subnet-123456"]
  vpc-id                   = "vpc-123456"
  lambda-role              = "arn:aws:iam::1234567890:role/lambda-role"
  local-docker-dir         = "path/to/local/docker/directory"
  lambda-layers            = ["arn:aws:lambda:region:account-id:layer:layer-name:version"]
}
```

| Name                     | Description                                                                          | Type         |
|--------------------------|--------------------------------------------------------------------------------------|--------------|
| region                   | The AWS region where the resources will be created.                                  | string       |
| account-id               | The AWS account ID.                                                                  | string       |
| bucket-id                | The name of the S3 bucket.                                                           | string       |
| bucket-buildspec-path    | The path to the buildspec file in the S3 bucket.                                     | string       |
| project-name             | The name of the CodeBuild project.                                                   | string       |
| codebuild-iam-role-arn   | The IAM role ARN for the CodeBuild project.                                          | string       |
| compute-type             | The type of compute to use for the build environment.                                | string       |
| image                    | The name or ARN of the Docker image to use for the build environment.                | string       |
| environment-variables    | A map of environment variables to set in the build environment.                      | map(string)  |
| bucket-docker-image-path | The path to the Docker image in the S3 bucket.                                       | string       |
| security-group-ids       | A list of security group IDs to attach to the CodeBuild project's VPC configuration. | list(string) |
| subnets                  | A list of subnet IDs to attach to the CodeBuild project's VPC configuration.         | list(string) |
| vpc-id                   | The ID of the VPC to attach to the CodeBuild project's VPC configuration.            | string       |
| lambda-role              | The IAM role for the Lambda function.                                                | string       |
| local-docker-dir         | The local path to the directory containing the Docker image.                         | string       |
| lambda-layers            | A list of Lambda layer ARNs to attach to the function.                               | list(string) |
