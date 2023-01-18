module "etl_pipelines" {
  for_each = fileset("${path.root}/../configuration/", "*.yml")
  source   = "./modules/glue_etl_pipelines"

  name       = var.project_name
  sdlc_stage = var.sdlc_stage

  config_file        = "${path.root}/../configuration/${each.value}"
  glue_role_arn      = module.glue_service_role.role_arn
  script_dir         = "${path.root}/../scripts/etl/"
  script_bucket_name = module.scripts_bucket.bucket

  extra_py_files        = ""
  extract_job_timeout   = 60
  load_job_timeout      = 60
  transform_job_timeout = 60

  max_concurrent_runs = 2
  number_of_workers   = 2
}
