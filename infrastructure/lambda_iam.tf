data "aws_iam_policy_document" "lambda-role-document" {
  statement {
    actions = ["sts:AssumeRole"]
    effect  = "Allow"
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "lambda-role" {
  name               = "${var.business-name}-${var.sdlc-stage}-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.lambda-role-document.json
}

data "aws_iam_policy_document" "lambda-role-policy" {
  statement {
    sid    = "AllowLambdaInvoke"
    effect = "Allow"
    actions = [
      "lambda:InvokeAsync",
      "lambda:InvokeFunction"
    ]
    resources = [
      "*"
    ]
  }

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
    sid    = "AllowCloudWatchLogs"
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = [
      "arn:aws:logs:*:*:*"
    ]
  }

  statement {
    sid    = "AllowGetSecrets"
    effect = "Allow"
    actions = [
      "secretsmanager:GetSecretValue",
      "secretsmanager:ListSecretVersionIds",
      "secretsmanager:ListSecrets"
    ]
    resources = [
      "arn:aws:secretsmanager:*:${data.aws_caller_identity.current.account_id}:secret:*"
    ]
  }

  statement {
    sid    = "AllowS3"
    effect = "Allow"
    actions = [
      "s3:Put*",
      "s3:Get*",
      "s3:List*",
      "s3:Delete*",
    ]
    resources = ["*"]
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
      "arn:aws:glue:*:${data.aws_caller_identity.current.account_id}:table/*/*",
      "arn:aws:glue:*:${data.aws_caller_identity.current.account_id}:database/*/*",
      "arn:aws:glue:*:${data.aws_caller_identity.current.account_id}:connection/*/*",
      "arn:aws:glue:*:${data.aws_caller_identity.current.account_id}:catalog"
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
      "dynamodb:Scan",
      "dynamodb:Query",
      "dynamodb:Update*",
      "dynamodb:Create*",
      "dynamodb:Get*",
    ]
    resources = [
      aws_dynamodb_table.extract-tracking-table.arn
    ]
  }
}

resource "aws_iam_policy" "lambda-policy" {
  name        = "${var.business-name}-${var.sdlc-stage}-lambda-policy"
  description = "Policy for ${var.sdlc-stage} Lambdas"
  policy      = data.aws_iam_policy_document.lambda-role-policy.json
}

resource "aws_iam_role_policy_attachment" "lambda-policy-attachment" {
  role       = aws_iam_role.lambda-role.name
  policy_arn = aws_iam_policy.lambda-policy.arn
}
