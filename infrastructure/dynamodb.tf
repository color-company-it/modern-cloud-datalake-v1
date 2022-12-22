resource "aws_dynamodb_table" "jdbc-extract-tracking-table" {
  name      = "jdbc-extract-tracking-table"
  hash_key  = "source"
  range_key = "updated_at"
  attribute {
    name = "source"
    type = "S"
  }
  attribute {
    name = "updated_at"
    type = "S"
  }
  billing_mode   = "PROVISIONED"
  read_capacity  = 5
  write_capacity = 5
}
