terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "3.26.0" # 4.47.0
    }
  }
  required_version = ">= 1.1.0"
}

provider "aws" {
  region                  = "eu-west-1"
  shared_credentials_file = "~/.aws/credentials"
  profile                 = "default"
}
