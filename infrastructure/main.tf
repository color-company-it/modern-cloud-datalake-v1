terraform {
  backend "s3" {
    bucket = "terraflow-tf-states"
    key    = "modern_cloud_datalake_v1/state.tfstate"
    region = "eu-west-1"
  }
}

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "4.47.0"
    }
  }
  required_version = ">= 1.1.0"
}

provider "aws" {
  region                  = "eu-west-1"
  shared_credentials_file = "~/.aws/credentials"
  profile                 = "default"
}

module "environment" {
  source      = "./modules/environment"
  name        = var.project_name
  region_name = var.region_name
}