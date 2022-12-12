resource "aws_s3_bucket" "codebase-bucket" {
  bucket = "${var.business_name}-codebase"
  acl    = "private"
}

resource "aws_s3_bucket" "configuration-bucket" {
  bucket = "${var.business_name}-configuration"
  acl    = "private"
}

resource "aws_s3_bucket" "orchestration-bucket" {
  bucket = "${var.business_name}-orchestration"
  acl    = "private"
}

resource "aws_s3_bucket" "etl-bucket" {
  bucket = "${var.business_name}-etl"
  acl    = "private"
}

resource "aws_s3_bucket" "scripts-bucket" {
  bucket = "${var.business_name}-scripts"
  acl    = "private"
}