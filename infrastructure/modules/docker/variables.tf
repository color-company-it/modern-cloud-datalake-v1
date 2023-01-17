variable "name" {
  type        = string
  description = "The name of the solution this role is being created for."
}

variable "sdlc_stage" {
  type        = string
  description = "The SDLC stage this role is being created for (e.g. dev, test, prod)."
}

variable "dockerfile_directory" {
  type        = string
  description = "Path to the Dockerfile in the local directory"
}

variable "tag" {
  type        = string
  description = "The docker tag that is also part of the ecr repo name"
}

variable "build_args" {
  type        = map(string)
  description = "Map of build arguments for the Docker build"
  default     = {}
}