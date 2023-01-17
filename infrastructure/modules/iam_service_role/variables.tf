variable "region_name" {}

variable "aws_resource_name" {
  type        = string
  description = "The name of the AWS resource this role is being created for."
}

variable "name" {
  type        = string
  description = "The name of the solution this role is being created for."
}

variable "sdlc_stage" {
  type        = string
  description = "The SDLC stage this role is being created for (e.g. dev, test, prod)."
}

variable "kms_arns" {
  type = list(string)
}