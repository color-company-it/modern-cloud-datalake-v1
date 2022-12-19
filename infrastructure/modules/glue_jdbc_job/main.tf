resource "aws_glue_job" "glue-jdbc-job" {
  name              = "${var.business-name}-${var.etl-stage}-${var.sdlc-stage}-jdbc-job"
  role_arn          = var.role-arn
  glue_version      = "3.0"
  max_retries       = 0
  worker_type       = "G.1X"
  number_of_workers = 2

  execution_property {
    max_concurrent_runs = var.max-concurrent-runs
  }

  command {
    name            = "glueetl"
    script_location = var.script-location
  }

  default_arguments = {
    # Args for Hudi 0.12.0
    "--datalake-formats" : "hudi"
    "--conf" : "spark.serializer=org.apache.spark.serializer.KryoSerializer --conf spark.sql.hive.convertMetastoreParquet=false"
    "--job-language"              = var.job-language
    "--additional-python-modules" = var.language-modules
    "--extra-py-files"            = var.codebase
  }

  connections = var.connections

  tags = {
    etl-stage    = var.etl-stage
    sdlc-stage   = var.sdlc-stage
    company-name = var.business-name
    script       = var.script-location
  }
}