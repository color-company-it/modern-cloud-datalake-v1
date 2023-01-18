variable "config_file" {
  description = "The path to the configuration file in YAML format."
}

variable "name" {
  description = "The name of the Glue job."
}

variable "sdlc_stage" {
  description = "The SDLC stage (e.g. 'dev', 'int', 'qa', 'prd')."
}

variable "glue_role_arn" {
  description = "The ARN of the Glue job's IAM role."
}

variable "extract_job_timeout" {
  description = "The timeout for the extract job in minutes."
}

variable "number_of_workers" {
  description = "The number of workers to use for the Glue jobs."
}

variable "max_concurrent_runs" {
  description = "The maximum number of concurrent runs for the Glue jobs."
}

variable "script_dir" {
  description = "The directory where the Glue job scripts are located."
}

variable "extra_py_files" {
  description = "Additional Python files to include in the Glue job execution."
}

variable "transform_job_timeout" {
  description = "The timeout for the transform job in minutes."
}

variable "load_job_timeout" {
  description = "The timeout for the load job in minutes."
}

variable "script_bucket_name" {
  description = "S3 bucket where the scripts are stored"
}