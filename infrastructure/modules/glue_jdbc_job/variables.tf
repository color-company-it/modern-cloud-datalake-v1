variable "business-name" {
  type        = string
  description = "This variable specifies the name of the business for which the AWS Glue job is being created"
}

variable "etl-stage" {
  type        = string
  description = "This variable specifies the stage of the ETL (extract, transform, and load) process for which the Glue job is being created"
}

variable "sdlc-stage" {
  type        = string
  description = "This variable specifies the stage of the software development life cycle (SDLC) for which the Glue job is being created"
}

variable "role-arn" {
  type        = string
  description = "This variable specifies the Amazon Resource Name (ARN) of the IAM role that the Glue job will assume when it is executed"
}

variable "max-concurrent-runs" {
  type        = number
  description = "This variable specifies the maximum number of concurrent runs for the Glue job. This determines how many instances of the job can run simultaneously"
}

variable "script-location" {
  type        = string
  description = "This variable specifies the location of the script that the Glue job will execute"
}

variable "connections" {
  type        = list(string)
  description = "This variable specifies the connections that the Glue job will use. A connection is a named resource that specifies the details of a connection to a data store, such as an Amazon RDS database"
}

variable "job-language" {
  type        = string
  description = "The programming language set up for the Glue Job, default to Python"
  default     = "python"
}

variable "codebase" {
  type = string
  description = "The S3 ARN for the codebase.zip file for the glue job to use"
}