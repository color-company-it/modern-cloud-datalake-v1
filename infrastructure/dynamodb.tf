resource "aws_dynamodb_table" "tracking_table" {
  for_each = toset(local.etl_stages)
  hash_key = "source"
  name     = "${var.project_name}_${var.sdlc_stage}_${each.value}_tracking_table"
  attribute {
    name = "source"
    type = "S"
  }
  write_capacity = 5
  read_capacity  = 5
  billing_mode   = "PROVISIONED"
}
