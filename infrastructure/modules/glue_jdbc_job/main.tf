resource "aws_glue_job" "glue-jdbc-job" {
  name              = "${var.business-name}-${var.etl-stage}-${var.sdlc-stage}-jdbc-job"
  role_arn          = var.role-arn
  glue_version      = "4.0"
  max_retries       = 0
  worker_type       = "G.1X"
  number_of_workers = 2

  execution_property {
    max_concurrent_runs = var.max-concurrent-runs
  }

  command {
    name            = "glueetl"
    script_location = var.script-location
    python_version  = "3"
  }

  default_arguments = {
    # Args for Hudi 0.12.0
    #"--datalake-formats" : "hudi"
    #"--conf" : "SPARK.serializer=org.apache.SPARK.serializer.KryoSerializer --conf SPARK.sql.hive.convertMetastoreParquet=false"
    "--additional-python-modules" = var.codebase
    "--enable-continuous-cloudwatch-log" : "true",
    "--enable-metrics" : "true"
  }

  connections = var.connections

  tags = {
    etl-stage    = var.etl-stage
    sdlc-stage   = var.sdlc-stage
    company-name = var.business-name
    script       = var.script-location
  }
}