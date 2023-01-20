module "lambda_service_role" {
  source            = "./modules/iam_service_role"
  name              = var.project_name
  region_name       = var.region_name
  aws_resource_name = "lambda"
  kms_arns          = [aws_kms_key.default.arn]
  sdlc_stage        = var.sdlc_stage
}

resource "aws_iam_policy" "custom_lambda_policy" {
  name        = "${var.project_name}_${var.sdlc_stage}_custom_lambda_policy"
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

module "state_machine_service_role" {
  source            = "./modules/iam_service_role"
  name              = var.project_name
  region_name       = var.region_name
  aws_resource_name = "states"
  kms_arns          = [aws_kms_key.default.arn]
  sdlc_stage        = var.sdlc_stage
}

resource "aws_iam_policy" "custom_state_machine_policy" {
  name        = "${var.project_name}_${var.sdlc_stage}_custom_state_machine_policy"
  description = "Policy for ${var.sdlc_stage} ${var.project_name}"
  policy      = data.aws_iam_policy_document.custom_step_function_policy.json
}

resource "aws_iam_role_policy_attachment" "custom_state_machine_policy" {
  role       = module.state_machine_service_role.role_name
  policy_arn = aws_iam_policy.custom_state_machine_policy.arn
}
