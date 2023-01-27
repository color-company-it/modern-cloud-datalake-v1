variable "name" {
  type        = string
  description = "Name of the ETL pipeline"
}

variable "sdlc_stage" {
  type        = string
  description = "The stage of the SDLC, e.g. dev, test, prod"
}

variable "config_file" {
  type        = string
  description = "The path to the configuration file containing the ETL pipeline details in YAML format"
}

variable "lambda_extract_config_manager_arn" {
  type        = string
  description = "The ARN of the Lambda function that extracts the configuration for the extract step"
}

variable "lambda_transform_config_manager_arn" {
  type        = string
  description = "The ARN of the Lambda function that extracts the configuration for the transform step"
}

variable "lambda_handle_step_function_status_arn" {
  type        = string
  description = "The ARN of the Lambda function that handles the status of the step function"
}

variable "lambda_role_arn" {
  type        = string
  description = "The ARN of the IAM role that the Lambda functions will assume"
}

variable "glue_job_name" {
  type        = string
  description = "The name of the Glue job for the extract step"
}

variable "glue_crawler_name" {
  type        = string
  description = "The name of the Glue Crawler for the extract step"
}

variable "glue_role_arn" {
  type        = string
  description = "The ARN of the IAM role that the Glue job and Crawler will assume"
}

variable "states_role_arn" {
  type        = string
  description = "The ARN of the IAM role that the step function will assume"
}
