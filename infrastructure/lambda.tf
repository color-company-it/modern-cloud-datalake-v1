resource "aws_lambda_layer_version" "codebase-layer" {
  filename   = module.codebase-archive.archive_path
  layer_name = "codebase"

  compatible_runtimes = ["python3.8"]
}

module "extract-manager" {
  source = "./modules/lambda_function"

  business-name = var.business-name
  lambda-role   = ""

  python-file-dir  = "${local.repository-layers.scripts}/lambda/"
  python-file-name = "extract_manager.py"
  sdlc-stage       = var.sdlc-stage
  variables = {
    config-s3-bucket    = aws_s3_bucket.configuration-bucket.bucket
    etl-s3-bucket       = aws_s3_bucket.etl-bucket.bucket
    tracking-table_name = aws_dynamodb_table.extract-tracking-table.name
  }
  layers = [aws_lambda_layer_version.codebase-layer.arn]

  depends_on = [aws_lambda_layer_version.codebase-layer]
}