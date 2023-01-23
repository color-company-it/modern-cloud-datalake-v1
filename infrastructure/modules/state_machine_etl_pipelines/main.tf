locals {
  configuration = yamldecode(file(var.config_file))
  source_name   = replace(local.configuration.source_name, ".yml", "")
  source_owners = toset(local.configuration.source_owners)
  job_name      = "${var.name}_${var.sdlc_stage}_${local.source_name}"

  # Validations to create the relevant resources based on the config
  bool_extract   = contains(keys(local.configuration), "extract") ? 1 : 0
  bool_transform = contains(keys(local.configuration), "transform") ? 1 : 0
  bool_load      = contains(keys(local.configuration), "load") ? 1 : 0
}

/*
Each ETL State Machine will have its own SNS Topic for the
Source Owners to Subscribe to, via emails which are provided
in the config file at root under the key: source_owners.
*/
resource "aws_sns_topic" "source_topic" {
  name = "${local.job_name}_topic"
}

resource "aws_sns_topic_subscription" "source_topic_subscription" {
  for_each  = local.source_owners
  endpoint  = each.value
  protocol  = "email"
  topic_arn = aws_sns_topic.source_topic.arn
}

resource "aws_sfn_state_machine" "extract" {
  count = local.bool_extract
  definition = templatefile("${path.module}/extract_definition.tmpl",
    {
      name                                   = "${local.job_name}_extract"
      lambda_extract_config_manager_arn      = var.lambda_extract_config_manager_arn
      lambda_handle_step_function_status_arn = var.lambda_handle_step_function_status_arn
      lambda_role_arn                        = var.lambda_role_arn
      glue_job_name                          = var.glue_job_name
      glue_crawler_name                      = var.glue_crawler_name
      glue_role_arn                          = var.glue_role_arn
      source_topic_arn                       = aws_sns_topic.source_topic.arn
      states_role_arn                        = var.states_role_arn
    }
  )
  name     = "${local.job_name}_extract"
  role_arn = var.states_role_arn
}