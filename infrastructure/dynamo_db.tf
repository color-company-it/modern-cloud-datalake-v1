resource "aws_dynamodb_table" "extract-tracking-table" {
  hash_key = "source"
  name     = "${var.business-name}-${var.sdlc-stage}-extract-tracking-table"
  attribute {
    name = "source"
    type = "S"
  }
  write_capacity = 5
  read_capacity  = 5
  billing_mode   = "PROVISIONED"
}