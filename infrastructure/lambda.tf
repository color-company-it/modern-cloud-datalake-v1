resource "aws_lambda_layer_version" "codebase-layer" {
  filename            = module.codebase-layer-archive.archive_path
  layer_name          = "${var.business-name}-${var.sdlc-stage}-codebase"
  compatible_runtimes = ["python3.8"]
}

resource "aws_lambda_layer_version" "datalake-layer" {
  filename            = "${path.module}/lambda_layers/datalake_layer.zip"
  layer_name          = "${var.business-name}-${var.sdlc-stage}-datalake"
  compatible_runtimes = ["python3.8"]
}

data "archive_file" "archive-extract-manager" {
  source_file      = "${local.repository-layers.scripts}/lambda/extract_manager.py"
  output_path      = "extract_manager.zip"
  type             = "zip"
  output_file_mode = "0666"
}

resource "aws_lambda_function" "extract-manager" {
  filename         = data.archive_file.archive-extract-manager.output_path
  source_code_hash = data.archive_file.archive-extract-manager.output_base64sha256
  function_name    = "${var.business-name}-${var.sdlc-stage}-extract-manager"
  role             = aws_iam_role.lambda-role.arn
  handler          = "extract_manager.lambda_handler"
  runtime          = "python3.8"
  timeout          = 600

  layers = [
    aws_lambda_layer_version.codebase-layer.arn,
    aws_lambda_layer_version.datalake-layer.arn
  ]

  environment {
    variables = {
      config_s3_bucket    = aws_s3_bucket.configuration-bucket.bucket
      etl_s3_bucket       = aws_s3_bucket.etl-bucket.bucket
      tracking_table_name = aws_dynamodb_table.extract-tracking-table.name
    }
  }
}
