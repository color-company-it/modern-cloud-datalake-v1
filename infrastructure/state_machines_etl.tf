module "state_machine_etl_pipelines" {
  for_each = fileset("${path.root}/../configuration/", "*.yml")
  source   = "./modules/state_machine_etl_pipelines"

  name        = var.project_name
  sdlc_stage  = var.sdlc_stage
  config_file = "${path.root}/../configuration/${each.value}"


  glue_crawler_name                      = module.glue_etl_pipelines[each.value].extract_glue_crawler_name[0]
  glue_job_name                          = module.glue_etl_pipelines[each.value].extract_glue_job_name[0]
  glue_role_arn                          = module.glue_service_role.role_arn
  lambda_extract_config_manager_arn      = aws_lambda_function.lambda_functions["extract_config_manager.zip"].arn
  lambda_handle_step_function_status_arn = aws_lambda_function.lambda_functions["handle_step_function_status.zip"].arn
  lambda_role_arn                        = module.lambda_service_role.role_arn
  states_role_arn                        = module.state_machine_service_role.role_arn
}