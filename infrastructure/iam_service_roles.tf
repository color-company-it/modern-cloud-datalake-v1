module "lambda_service_role" {
  source            = "./modules/iam_service_role"
  name              = var.project_name
  region_name       = var.region_name
  aws_resource_name = "lambda"
  kms_arns          = [aws_kms_key.default.arn]
  sdlc_stage        = var.sdlc_stage
}

resource "aws_iam_policy" "custom_lambda_policy" {
  name        = "${var.project_name}-${var.sdlc_stage}-cutom-lambda-policy"
  description = "Policy for ${var.sdlc_stage} ${var.project_name}"
  policy      = data.aws_iam_policy_document.custom_lambda_policy.json
}

resource "aws_iam_role_policy_attachment" "custom_lambda_policy" {
  role       = module.lambda_service_role.role_name
  policy_arn = aws_iam_policy.custom_lambda_policy.arn
}

module "glue_service_role" {
  source            = "./modules/iam_service_role"
  name              = var.project_name
  region_name       = var.region_name
  aws_resource_name = "glue"
  kms_arns          = [aws_kms_key.default.arn]
  sdlc_stage        = var.sdlc_stage
}
