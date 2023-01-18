data "archive_file" "codebase_layer" {
  output_path      = "${path.module}/lambda_layers/codebase.zip"
  type             = "zip"
  source_dir       = "${path.module}/lambda_layers/codebase/"
  output_file_mode = "0666"
}

resource "aws_lambda_layer_version" "codebase_layer" {
  layer_name          = "${var.project_name}_${var.sdlc_stage}_codebase_layer"
  filename            = data.archive_file.codebase_layer.output_path
  compatible_runtimes = ["python3.8"]

  description = "Data Lake CodeBase Layer"
}

resource "aws_lambda_layer_version" "datalake_layer" {
  layer_name          = "${var.project_name}_${var.sdlc_stage}_datalake_layer"
  filename            = data.archive_file.codebase_layer.output_path
  compatible_runtimes = ["python3.8"]

  description = "Data Lake Additional Layer with tools like requests and pyyaml"
}

data "archive_file" "lambda_functions" {
  for_each         = fileset("${path.root}/../scripts/lambdas/", "*.py")
  source_file      = "${path.root}/../scripts/lambdas/${each.value}"
  output_path      = "${path.root}/../scripts/lambdas/${replace(each.value, ".py", "")}.zip"
  type             = "zip"
  output_file_mode = "0666"
}

resource "aws_lambda_function" "lambda_functions" {
  for_each         = fileset("${path.root}/../scripts/lambdas/", "*.zip")
  function_name    = "${var.project_name}_${var.sdlc_stage}_${replace(each.value, ".zip", "")}"
  role             = module.lambda_service_role.role_arn
  handler          = "${replace(each.value, ".zip", "")}.lambda_handler"
  runtime          = "python3.8"
  timeout          = 30
  filename         = "${path.root}/../scripts/lambdas/${each.value}"
  source_code_hash = filebase64sha256("${path.root}/../scripts/lambdas/${each.value}")

  environment {
    variables = {
      region_name              = var.region_name
      sdlc_stage               = var.sdlc_stage
      account_id               = data.aws_caller_identity.current.account_id
      config_s3_bucket         = module.config_bucket.bucket
      extract_s3_bucket        = module.etl_buckets["extract"].bucket
      transform_s3_bucket      = module.etl_buckets["transform"].bucket
      load_s3_bucket           = module.etl_buckets["load"].bucket
      extract_tracking_table   = aws_dynamodb_table.tracking_table["extract"].name
      transform_tracking_table = aws_dynamodb_table.tracking_table["transform"].name
      load_tracking_table      = aws_dynamodb_table.tracking_table["load"].name
    }
  }

  layers = [
    aws_lambda_layer_version.codebase_layer.arn, aws_lambda_layer_version.datalake_layer.arn
  ]
}