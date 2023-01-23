# Glue Job Terraform Module

This Terraform module creates Glue jobs on AWS based on a provided configuration file.
The module is designed to create extract, transform, and load jobs, each of which can be enabled
or disabled depending on the configuration file.

## Variables

- config_file: The path to the configuration file in YAML format.
- name: The name of the Glue job.
- sdlc_stage: The SDLC stage (e.g. "dev", "prod").
- glue_role_arn: The ARN of the Glue job's IAM role.
- extract_job_timeout: The timeout for the extract job in minutes.
- number_of_workers: The number of workers to use for the Glue jobs.
- max_concurrent_runs: The maximum number of concurrent runs for the Glue jobs.
- script_dir: The directory where the Glue job scripts are located.
- extra_py_files: Additional Python files to include in the Glue job execution.
- transform_job_timeout: The timeout for the transform job in minutes.
- load_job_timeout: The timeout for the load job in minutes.
- script_bucket_name: S3 bucket where the scripts are stored

## Usage

To use this module, you will need to provide the necessary input variables and include the module in your Terraform
code. Here is an example of how to use the module:

```terraform
module "glue_jobs" {
  source = "path/to/module"

  config_file           = "path/to/config.yaml"
  name                  = "example_job"
  sdlc_stage            = "dev"
  glue_role_arn         = "arn:aws:iam::123456789012:role/GlueJobRole"
  extract_job_timeout   = 30
  number_of_workers     = 2
  max_concurrent_runs   = 1
  script_dir            = "s3://path/to/scripts"
  extra_py_files        = "s3://path/to/extra_files.zip"
  transform_job_timeout = 60
  load_job_timeout      = 90
  script_bucket_name    = "script-bucket"
}
```

You can then run terraform init, terraform plan, and terraform apply to create the Glue jobs on your AWS account.

## Outputs

- glue_job_name: The concatenated name of the Glue job, including the name, sdlc_stage, and source_name from the
  configuration file.
- bool_glue_extract_job: A boolean value indicating whether the extract job should be created based on the configuration
  file.
- bool_glue_transform_job: A boolean value indicating whether the transform job should be created based on the
  configuration file.
- bool_glue_load_job: A boolean value indicating whether the load job should be created based on the configuration file.
- extract_job_name: The name of the extract job.
- transform_job_name: The name of the transform job.
- load_job_name: The name of the load job.
