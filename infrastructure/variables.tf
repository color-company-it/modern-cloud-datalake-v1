variable "region_name" {
  default = "eu-west-1"
}

variable "project_name" {
  default = "dirk_test"
}

variable "sdlc_stage" {
  default = "dev"
}

data "aws_caller_identity" "current" {}
