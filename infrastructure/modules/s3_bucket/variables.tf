variable "name" {
  description = "The name for the resources"
}

variable "use_case" {
  description = "The use case in the environment, such as `landing-data` or `scripts`"
}

variable "kms_arn" {
  description = "For server-side encryption"
}

variable "sdlc_stage" {
  type        = string
  description = "The SDLC stage this role is being created for (e.g. dev, test, prod)."
}