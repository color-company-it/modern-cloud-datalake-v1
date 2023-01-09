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
  assume_role_policy = data.aws_iam_policy_document.lambda-role-document.json
}

data "aws_iam_policy_document" "codebuild-policy-document" {
  statement {
    resources = ["*"]
    actions = [
      "ec2:Create*",
      "ec2:Describe*",
      "ecr:Delete*"
    ]
    effect = "Allow"
  }

  statement {
    resources = ["*"]
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    effect = "Allow"
  }

  statement {
    resources = ["*"]
    actions = [
      "ecr:*"
    ]
    effect = "Allow"
  }
}

resource "aws_iam_policy" "codebuild-default-access" {
  name   = "${var.business-name}-${var.sdlc-stage}-codebuild-default-access"
  policy = data.aws_iam_policy_document.codebuild-policy-document.json
}

resource "aws_iam_policy_attachment" "codebuild-default-access" {
  name       = "${var.business-name}-${var.sdlc-stage}-codebuild-default-access"
  policy_arn = aws_iam_policy.codebuild-default-access.arn
  roles = [
    aws_iam_role.codebuild-role.name
  ]
}
