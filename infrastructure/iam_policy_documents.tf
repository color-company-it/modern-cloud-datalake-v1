data "aws_iam_policy_document" "custom_lambda_policy" {
  statement {
    sid    = "AllowS3"
    effect = "Allow"
    actions = [
      "s3:Put*",
      "s3:Delete*",
      "s3:Get*"
    ]
    resources = [
      module.config_bucket.arn,
      "${module.config_bucket.arn}/*"
    ]
  }

  statement {
    sid    = "ModifyDDBTrackingTable"
    effect = "Allow"
    actions = [
      "dynamodb:PutItem",
      "dynamodb:DeleteItem",
      "dynamodb:Scan",
      "dynamodb:Query",
      "dynamodb:Update*",
      "dynamodb:Create*",
      "dynamodb:Get*",
    ]
    resources = [
      aws_dynamodb_table.tracking_table[local.etl_stages[0]].arn,
      aws_dynamodb_table.tracking_table[local.etl_stages[1]].arn,
      aws_dynamodb_table.tracking_table[local.etl_stages[2]].arn,
    ]
  }
}
