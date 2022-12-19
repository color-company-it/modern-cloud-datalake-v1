resource "aws_cloudwatch_log_group" "aws-glue-log-group" {
  name = "aws-${var.sdlc-stage}-glue-log-group"

  tags = {
    sdlc-stage  = var.sdlc-stage
    Application = "${var.business-name}-${var.sdlc-stage}-datalake"
  }
}