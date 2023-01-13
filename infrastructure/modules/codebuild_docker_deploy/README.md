# AWS CodeBuild and Lambda Deployment

This solution is used to deploy a Docker image to an ECR registry and trigger a CodeBuild project using a Lambda
function.

## Resources created

- An ECR repository is created to store the Docker image.
- An S3 bucket and object are created to store the buildspec.yml file used by CodeBuild.
- A CodeBuild project is created to build and deploy the Docker image.
- A Lambda function is created to trigger the CodeBuild project.
- A S3 bucket notification is created to trigger the Lambda function when a new object is added or an existing object is
  removed from the S3 bucket.

## Variables

- region-name: The name of the region where the resources should be created.
- s3-bucket: The S3 bucket where the buildspec.yml file is stored and the source code is located.
- s3-prefix: The prefix of the S3 bucket object containing the buildspec.yml and source code files.
- docker-tag: The tag of the Docker image that will be deployed.
- project-name: The name of the project.
- iam-role-arn: The ARN of the IAM role that will be used by CodeBuild.
- compute-type: The type of compute to use for the CodeBuild project.
- build-image: The image to use for the CodeBuild project.
- environment-type: The type of environment to use for the CodeBuild project.
- environment-variables: A list of environment variables to be passed to the CodeBuild project.

```terraform
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
```

## Logging

Logging

Echo commands have been added to the buildspec.yml file and the lambda_function.py file to make it easier to understand
what's happening and debug issues if they arise.