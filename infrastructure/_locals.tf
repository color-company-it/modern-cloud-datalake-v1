data "aws_caller_identity" "current" {}

locals {
  /*
  This Terraform code defines a map named repository-layers that contains
  the file paths of four directories: codebase, configuration, orchestration,
  and scripts. The file paths are relative to the root of the current directory.
  This map can be used to access the file paths of the four directories in
  your Terraform code. For example, you can use the codebase key to access
  the file path of the codebase directory.
  */
  repository-layers = {
    codebase      = "${path.root}/../codebase/"
    configuration = "${path.root}/../configuration/"
    orchestration = "${path.root}/../orchestration/"
    scripts       = "${path.root}/../scripts/"
  }


  /*
  Defines a local named configuration_files that contains a set of all .yaml
  files in the configuration directory, which is located at the root of the
  current directory.
  This local can be used to access the set of configuration files in the
  Terraform code.
  */
  configuration-files = fileset(local.repository-layers.configuration, "*.yaml")
  docker-scripts      = fileset("${local.repository-layers.scripts}/docker/", "*")
  spark-scripts       = fileset("${local.repository-layers.scripts}/spark/", "*")

  /*
  sdlc-stages is a local variable that specifies the different stages of the
  software development life cycle (SDLC). In this case, the variable is defined
  as an array containing the following values.
  */
  sdlc-stages = ["dev", "int", "qa", "prd"]

  /*
  etl-stages is a local variable that specifies the different stages of the ETL
  (extract, transform, and load) process. In this case, the variable is defined
  as an array containing the following values:
  */
  etl-stages = ["extract", "transform", "load"]
}

