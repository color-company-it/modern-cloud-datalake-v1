resource "aws_s3_bucket" "self" {
  bucket = "${var.name}-${var.use_case}-${var.sdlc_stage}"
  acl    = "private"

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        kms_master_key_id = var.kms_arn
        sse_algorithm     = "aws:kms"
      }
    }
  }

  tags = {
    bucket_name = "${var.name}-${var.use_case}-${var.sdlc_stage}"
    use_case    = var.use_case
    sdlc_stage  = var.sdlc_stage
  }
}
