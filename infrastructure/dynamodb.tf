resource "aws_dynamodb_table" "jdbc-extract-tracking-table" {
  name     = "jdbc-extract-tracking-table"
  hash_key = "source"

  attribute {
    name = "source"
    type = "S"
  }

  billing_mode   = "PROVISIONED"
  read_capacity  = 5
  write_capacity = 5
}
