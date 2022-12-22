# IAM role for the Glue job
resource "aws_iam_role" "glue-job-role" {
  name = "${var.business-name}-${var.etl-stage}-${var.sdlc-stage}-glue-job-role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "glue.amazonaws.com"
      },
      "Effect": "Allow"
    }
  ]
}
EOF
}

data "aws_iam_policy_document" "glue-job-policy" {
  statement {
    sid    = "AllowCloudWatchMetrics"
    effect = "Allow"
    actions = [
      "cloudwatch:PutMetricData",
    ]
    resources = [
      "*",
    ]
  }

  statement {
    sid       = "AllowCloudWatchLogs"
    effect    = "Allow"
    actions   = ["*"]
    resources = ["*"]
  }

  statement {
    sid    = "AllowS3"
    effect = "Allow"
    actions = [
      "s3:PutObject",
      "s3:GetObject",
      "s3:ListBucket",
      "s3:DeleteObject",
      "s3:GetBucketAcl",
      "s3:GetBucketLocation"
    ]
    resources = [
      "arn:aws:s3:::${var.script-s3-bucket-name}/*",
      "arn:aws:s3:::${var.etl-s3-bucket-name}/*",
      "arn:aws:s3:::${var.codebase-s3-bucket-name}/*"
    ]
  }

  statement {
    sid    = "AllowGlue"
    effect = "Allow"
    actions = [
      "glue:GetConnection*",
      "glue:*Tag*",
      "glue:*Table*",
      "glue:*Partition*",
      "glue:*Database*"
    ]
    resources = [
      "arn:aws:glue:*:${var.account-id}:table/*/*",
      "arn:aws:glue:*:${var.account-id}:database/*/*",
      "arn:aws:glue:*:${var.account-id}:connection/*/*",
      "arn:aws:glue:*:${var.account-id}:catalog"
    ]
  }

  statement {
    sid    = "AllowGlueListAll"
    effect = "Allow"
    actions = [
      "glue:List*"
    ]
    resources = ["*"]
  }

  statement {
    sid    = "ListAllDDBTables"
    effect = "Allow"
    actions = [
      "dynamodb:ListTables"
    ]
    resources = ["*"]
  }

  statement {
    sid    = "ModifyDDBTrackingTable"
    effect = "Allow"
    actions = [
      "dynamodb:PutItem",
      "dynamodb:DeleteItem",
      "dynamodb:GetItem",
      "dynamodb:Scan",
      "dynamodb:Query",
      "dynamodb:UpdateItem",
      "dynamodb:ImportTable",
      "dynamodb:GetRecords"
    ]
    resources = var.tracking-table-names
  }
}


# IAM policy for the Glue job
resource "aws_iam_policy" "glue-job-policy" {
  name        = "${var.business-name}-${var.etl-stage}-${var.sdlc-stage}-glue-job-policy"
  description = "Policy for JDBC ${var.etl-stage} ${var.sdlc-stage} Glue job"

  policy = data.aws_iam_policy_document.glue-job-policy.json
}

# Attach the policy to the role
resource "aws_iam_role_policy_attachment" "glue-job-policy-attachment" {
  role       = aws_iam_role.glue-job-role.name
  policy_arn = aws_iam_policy.glue-job-policy.arn
}
