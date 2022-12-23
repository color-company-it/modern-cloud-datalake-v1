variable "region-name" {}
variable "account-id" {}

variable "business-name" {
  type        = string
  description = "The name of the business"
}

variable "etl-stage" {
  type        = string
  description = "The stage of the ETL process"
}

variable "sdlc-stage" {
  type        = string
  description = "The stage of the software development lifecycle"
}

variable "script-s3-bucket-name" {
  type        = string
  description = "The Name of the S3 bucket where the Glue script is stored"
}

variable "etl-s3-bucket-name" {
  type        = string
  description = "The Name of the S3 bucket where the ETL data is stored"
}

variable "codebase-s3-bucket-name" {
  type        = string
  description = "The Name of the S3 bucket where the Codebase is stored"
}

variable "tracking-table-names" {
  type        = list(string)
  description = "The DDB extract tracking tables name to track ETL processes"
}
