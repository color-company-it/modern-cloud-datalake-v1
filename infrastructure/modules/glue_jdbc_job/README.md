# Glue JDBC Job Terraform Module

This Terraform module creates an AWS Glue job that can be used to perform ETL (extract, transform, and load) tasks using
a JDBC connection.

## Inputs

The following input variables are required:

- `business-name`: Specifies the name of the business for which the AWS Glue job is being created.
- `etl-stage`: Specifies the stage of the ETL process for which the Glue job is being created.
- `sdlc-stage`: Specifies the stage of the software development life cycle (SDLC) for which the Glue job is being
  created.
- `role-arn`: Specifies the Amazon Resource Name (ARN) of the IAM role that the Glue job will assume when it is
  executed.
- `max-concurrent-runs`: Specifies the maximum number of concurrent runs for the Glue job. This determines how many
  instances of the job can run simultaneously.
- `script-location`: Specifies the location of the script that the Glue job will execute.
- `connections`: Specifies the connections that the Glue job will use. A connection is a named resource that specifies
  the details of a connection to a data store, such as an Amazon RDS database.
- `job-language`: The programming language set up for the Glue Job (default to Python).
- `codebase`: The S3 ARN for the codebase.zip file for the glue job to use.

## Outputs

The following outputs are returned:

- `job-name`: The name of the Glue job.
- `execution-property`: The execution property of the Glue job, which includes the maximum number of concurrent runs.
- `default-arguments`: The default arguments for the Glue job.

## Example Usage

```terraform
module "glue-jdbc-job" {
  source = "./modules/glue_jdbc_job"

  business-name       = "example-business"
  etl-stage           = "staging"
  sdlc-stage          = "test"
  role-arn            = "arn:aws:iam::123456789012:role/GlueJobRole"
  max-concurrent-runs = 2
  script-location     = "s3://example-bucket/scripts/etl.py"
  connections         = ["connection1", "connection2"]
  codebase            = "s3://example-bucket/codebase.zip"
}
```
