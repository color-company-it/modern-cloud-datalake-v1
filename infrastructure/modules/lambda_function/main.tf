locals {
  python-file-dir  = var.python-file-dir
  python-file-name = replace(var.python-file-name, ".py", "")
}

resource "aws_lambda_function" "lambda-function" {
  filename      = "${local.python-file-dir}/${local.python-file-name}.py"
  function_name = "${var.business-name}-${var.sdlc-stage}-${local.python-file-name}"
  role          = var.lambda-role
  handler       = "${local.python-file-name}.lambda_handler"

  source_code_hash = filebase64sha256("${local.python-file-dir}/${local.python-file-name}.py")
  runtime          = "python3.8"
  timeout          = 300
  layers           = var.layers
  environment {
    variables = var.variables
  }

  tags = {
    sdlc-stage   = var.sdlc-stage
    company-name = var.business-name
  }
}