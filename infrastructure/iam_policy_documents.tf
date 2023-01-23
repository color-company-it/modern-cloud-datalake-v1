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

data "aws_iam_policy_document" "custom_glue_policy" {
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
      "${module.config_bucket.arn}/*",
      module.scripts_bucket.arn,
      "${module.scripts_bucket.arn}/*",
      module.etl_buckets["extract"].arn,
      "${module.etl_buckets["extract"].arn}/*"
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

  statement {
    sid    = "AllowSNSPublish"
    effect = "Allow"
    actions = [
      "sns:Publish",
    ]
    resources = [
      "*"
    ]
  }
}

data "aws_iam_policy_document" "custom_step_function_policy" {
  statement {
    sid    = "AllowGlueStart"
    effect = "Allow"
    actions = [
      "glue:StartJobRun",
      "glue:GetJobRun",
      "glue:GetJob",
      "glue:BatchStopJobRun",
      "glue:StartCrawler"
    ]
    resources = [
      "*"
    ]
  }

  statement {
    sid    = "AllowLambdaStart"
    effect = "Allow"
    actions = [
      "lambda:InvokeFunction"
    ]
    resources = [
      "*"
    ]
  }
}
