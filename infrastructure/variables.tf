variable "business-name" {
  type        = string
  description = "The name of the business/group/department that is deploying this repository to AWS."
  default     = "color-it"
}

variable "sdlc-stage" {
  type        = string
  description = "The SDLC stage defines where and how this environment would be built and is one of `dev, int, qa, prod`"
  default     = "dev"
}