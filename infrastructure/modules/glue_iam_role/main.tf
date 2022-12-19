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

# IAM policy for the Glue job
resource "aws_iam_policy" "glue-job-policy" {
  name        = "${var.business-name}-${var.etl-stage}-${var.sdlc-stage}-glue-job-policy"
  description = "Policy for JDBC ${var.etl-stage} ${var.sdlc-stage} Glue job"

  policy = templatefile("${path.module}/iam_role.json", {
    "region-name": var.region-name,
    "account-id": var.account-id,
    "script-s3-bucket-name": var.script-s3-bucket-name,
    "etl-s3-bucket-name": var.etl-s3-bucket-name,
     "codebase-s3-bucket-name": var.codebase-s3-bucket-name,
    "etl-stage": var.etl-stage
  })
}

# Attach the policy to the role
resource "aws_iam_role_policy_attachment" "glue-job-policy-attachment" {
  role       = aws_iam_role.glue-job-role.name
  policy_arn = aws_iam_policy.glue-job-policy.arn
}
