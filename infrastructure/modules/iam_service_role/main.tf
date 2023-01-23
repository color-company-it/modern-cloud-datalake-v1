data "aws_caller_identity" "current" {}

data "aws_iam_policy_document" "assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    effect  = "Allow"
    principals {
      type        = "Service"
      identifiers = ["${var.aws_resource_name}.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "role" {
  name               = "${var.name}_${var.sdlc_stage}_${var.aws_resource_name}_role"
  assume_role_policy = data.aws_iam_policy_document.assume_role_policy.json
}

data "aws_iam_policy_document" "default_policy" {
  statement {
    sid       = "AllowS3ResourceAccess"
    effect    = "Allow"
    resources = ["*"]
    actions = [
      "s3:PutObject",
      "s3:ListBucket",
      "s3:GetBucketLocation",
      "s3:GetBucketAcl"
    ]
  }

  statement {
    sid       = "AllowGlueRead"
    effect    = "Allow"
    resources = ["*"]
    actions = [
      "glue:List*",
      "glue:GetSecurityConfiguration"
    ]
  }

  statement {
    sid    = "AllowGlueResources"
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
    sid    = "AllowEc2Actions"
    effect = "Allow"
    actions = [
      "ec2:Describe*",
      "ec2:*NetworkInterface"
    ]
    resources = ["*"]
  }

  statement {
    sid    = "LogAccess"
    effect = "Allow"
    actions = [
      "logs:PutLogEvents",
      "logs:CreateLogStream",
      "logs:CreateLogGroup",
      "logs:AssociateKmsKey"
    ]
    resources = [
      "arn:aws:logs:${var.region_name}:${data.aws_caller_identity.current.account_id}:*"
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
    sid    = "AllowKmsAccess"
    effect = "Allow"
    actions = [
      "kms:Encrypt",
      "kms:DecryptKey",
      "kms:Decrypt",
      "kms:GenerateDataKey"
    ]
    resources = var.kms_arns
  }

  statement {
    sid    = "AllowDdbRead"
    effect = "Allow"
    actions = [
      "dynamodb:Scan",
      "dynamodb:Query",
      "dynamodb:Get*",
      "dynamodb:ListTables"
    ]
    resources = ["*"]
  }
}

resource "aws_iam_policy" "default_policy" {
  name        = "${var.name}_${var.sdlc_stage}_${var.aws_resource_name}_policy"
  description = "Policy for ${var.sdlc_stage} ${var.aws_resource_name}"
  policy      = data.aws_iam_policy_document.default_policy.json
}

resource "aws_iam_role_policy_attachment" "default_policy_attachment" {
  role       = aws_iam_role.role.name
  policy_arn = aws_iam_policy.default_policy.arn
}
