data "aws_iam_policy_document" "codebuild-role-document" {
  statement {
    actions = ["sts:AssumeRole"]
    effect  = "Allow"
    principals {
      type        = "Service"
      identifiers = ["codebuild.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "codebuild-role" {
  name               = "${var.business-name}-${var.sdlc-stage}-codebuild-role"
  assume_role_policy = data.aws_iam_policy_document.codebuild-role-document.json
}

data "aws_iam_policy_document" "codebuild-role-policy" {
  statement {
    sid = "AllowEC2"
    actions = [
      "ec2:Describe*",
      "ec2:Create*",
      "ec2:Delete*"
    ]
    effect    = "Allow"
    resources = ["*"]
  }

  statement {
    sid = "AllowLogs"
    actions = [
      "logs:PutLogEvents",
      "logs:CreateLogStream",
      "logs:CreateLogGroup"
    ]
    effect    = "Allow"
    resources = ["*"]
  }

  statement {
    sid = "AllowECR"
    actions = [
      "ecr:Upload*",
      "ecr:Put*",
      "ecr:List*",
      "ecr:Get*",
      "ecr:Describe",
      "ecr:Batch*",
      "ecr:CompleteLayerUpload"
    ]
    effect    = "Allow"
    resources = ["*"]
  }

  statement {
    sid = "S3Allow"
    actions = [
      "s3:List*",
      "s3:Get*"
    ]
    effect = "Allow"
    resources = [
      "arn:aws:s3:::${aws_s3_bucket.scripts-bucket.bucket}",
      "arn:aws:s3:::${aws_s3_bucket.scripts-bucket.bucket}/*",
    ]
  }
}

resource "aws_iam_policy" "codebuild-policy" {
  name        = "${var.business-name}-${var.sdlc-stage}-codebuild-policy"
  description = "Policy for ${var.sdlc-stage} codebuilds"
  policy      = data.aws_iam_policy_document.codebuild-role-policy.json
}

resource "aws_iam_role_policy_attachment" "codebuild-policy-attachment" {
  role       = aws_iam_role.codebuild-role.name
  policy_arn = aws_iam_policy.codebuild-policy.arn
}