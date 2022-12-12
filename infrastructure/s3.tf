resource "aws_s3_bucket" "enterprise-datalake-poc-2022" {
  bucket = "enterprise-datalake-poc-2022"
  acl    = "private"
}