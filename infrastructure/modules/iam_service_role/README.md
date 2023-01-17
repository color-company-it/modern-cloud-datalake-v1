# IAM Service Role Terraform Module

This module creates an IAM role that can be assumed by a service, and attaches a default policy that provides read-only
access to various AWS resources.

## Inputs

- aws_resource_name: The name of the AWS resource this role is being created for.
- name: The name of the solution this role is being created for.
- sdlc_stage: The SDLC stage this role is being created for (e.g. dev, test, prod).
- kms_arns
- region_name

## Outputs

- role_name: The name of the IAM role created by this module.
- role_arn: The ARN of the IAM role created by this module.

## Usage

```terraform
module "default_codebuild_service_role" {
  source            = "./modules/iam_service_role"
  name              = var.business_name
  sdlc_stage        = var.sdlc_stage
  aws_resource_name = "codebuild"
}
```