variable "python-file-dir" {
  type        = string
  description = "The directory where the Python file is located."
}

variable "python-file-name" {
  type        = string
  description = "The name of the Python file."
}

variable "business-name" {
  type        = string
  description = "The name of the business or organization."
}

variable "sdlc-stage" {
  type        = string
  description = "The software development lifecycle stage (e.g. dev, int, qa, prd)."
}

variable "lambda-role" {
  type        = string
  description = "The ARN of the IAM role that the Lambda function will use."
}

variable "layers" {
  type        = list(string)
  description = "A list of layer ARN strings that the Lambda function can use."
}

variable "variables" {
  type        = map(string)
  description = "A map of environment variables to be passed to the Lambda function."
}