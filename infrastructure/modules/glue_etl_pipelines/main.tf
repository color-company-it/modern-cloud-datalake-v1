locals {
  configuration = yamldecode(file(var.config_file))
  source_name   = replace(local.configuration.source_name, ".yml", "")
  glue_job_name = "${var.name}_${var.sdlc_stage}_${local.source_name}"

  # Validations to create the relevant resources based on the config
  bool_glue_extract_job   = contains(keys(local.configuration), "extract") ? 1 : 0
  bool_glue_transform_job = contains(keys(local.configuration), "transform") ? 1 : 0
  bool_glue_load_job      = contains(keys(local.configuration), "load") ? 1 : 0
}

resource "aws_s3_bucket_object" "extract_script" {
  count       = local.bool_glue_extract_job
  bucket      = var.script_bucket_name
  key         = "etl/${local.configuration.extract.script_name}"
  source      = "${var.script_dir}/${local.configuration.extract.script_name}"
  source_hash = filemd5("${var.script_dir}/${local.configuration.extract.script_name}")
}

resource "aws_glue_job" "extract_job" {
  count             = local.bool_glue_extract_job
  name              = "${local.glue_job_name}_extract"
  role_arn          = var.glue_role_arn
  max_retries       = 0
  timeout           = var.extract_job_timeout
  number_of_workers = var.number_of_workers
  worker_type       = "Standard"
  glue_version      = "4.0"

  execution_property {
    max_concurrent_runs = var.max_concurrent_runs
  }

  command {
    script_location = "s3:://${var.script_bucket_name}/${aws_s3_bucket_object.extract_script[count.index].key}"
  }

  default_arguments = merge({
    "--job_language"                     = "python"
    "--enable-continuous-cloudwatch-log" = "true"
    "--enable-continuous-log-filter"     = "true"
    "--extra-py-files"                   = var.extra_py_files
    },
    local.configuration.extract.arguments
  )

  tags = {
    source        = local.source_name
    sdlc_stage    = var.sdlc_stage
    glue_job_name = "${local.glue_job_name}_extract"
  }
}

resource "aws_s3_bucket_object" "transform_script" {
  count       = local.bool_glue_transform_job
  bucket      = var.script_bucket_name
  key         = "scripts/etl/${local.configuration.transform.script_name}"
  source      = "${var.script_dir}/${local.configuration.transform.script_name}"
  source_hash = filemd5("${var.script_dir}/${local.configuration.transform.script_name}")
}

resource "aws_glue_job" "transform_job" {
  count             = local.bool_glue_transform_job
  name              = "${local.glue_job_name}_transform"
  role_arn          = var.glue_role_arn
  max_retries       = 0
  timeout           = var.transform_job_timeout
  number_of_workers = var.number_of_workers
  worker_type       = "Standard"
  glue_version      = "4.0"

  execution_property {
    max_concurrent_runs = var.max_concurrent_runs
  }

  command {
    script_location = "s3:://${var.script_bucket_name}/${aws_s3_bucket_object.transform_script[count.index].key}"
  }

  default_arguments = merge({
    "--job_language"                     = "python"
    "--enable-continuous-cloudwatch-log" = "true"
    "--enable-continuous-log-filter"     = "true"
    "--extra-py-files"                   = var.extra_py_files
    },
    local.configuration.transform.arguments
  )

  tags = {
    source        = local.source_name
    sdlc_stage    = var.sdlc_stage
    glue_job_name = "${local.glue_job_name}_transform"
  }
}

resource "aws_s3_bucket_object" "load_script" {
  count       = local.bool_glue_load_job
  bucket      = var.script_bucket_name
  key         = "scripts/etl/${local.configuration.load.script_name}"
  source      = "${var.script_dir}/${local.configuration.load.script_name}"
  source_hash = filemd5("${var.script_dir}/${local.configuration.load.script_name}")
}

resource "aws_glue_job" "load_job" {
  count             = local.bool_glue_load_job
  name              = "${local.glue_job_name}_load"
  role_arn          = var.glue_role_arn
  max_retries       = 0
  timeout           = var.load_job_timeout
  number_of_workers = var.number_of_workers
  worker_type       = "Standard"
  glue_version      = "4.0"

  execution_property {
    max_concurrent_runs = var.max_concurrent_runs
  }

  command {
    script_location = "s3:://${var.script_bucket_name}/${aws_s3_bucket_object.load_script[count.index].key}"
  }

  default_arguments = merge({
    "--job_language"                     = "python"
    "--enable-continuous-cloudwatch-log" = "true"
    "--enable-continuous-log-filter"     = "true"
    "--extra-py-files"                   = var.extra_py_files
    },
    local.configuration.load.arguments
  )

  tags = {
    source        = local.source_name
    sdlc_stage    = var.sdlc_stage
    glue_job_name = "${local.glue_job_name}_load"
  }
}



