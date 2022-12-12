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

variable "script-s3-bucket-arn" {
  type        = string
  description = "The ARN of the S3 bucket where the Glue script is stored"
}

variable "etl-s3-bucket-arn" {
  type        = string
  description = "The ARN of the S3 bucket where the ETL data is stored"
}
