#module "base_pyspark_container" {
#  source = "./modules/docker"
#
#  dockerfile_directory = "${path.root}/../scripts/containers/base_pyspark"
#  name                 = var.project_name
#  sdlc_stage           = var.sdlc_stage
#  tag                  = "base_pyspark"
#}
#
#module "base_etl_jdbc" {
#  source = "./modules/docker"
#
#  dockerfile_directory = "${path.root}/../scripts/containers/etl_jdbc"
#  name                 = var.project_name
#  sdlc_stage           = var.sdlc_stage
#  tag                  = "etl_jdbc"
#  build_args           = {
#    ACCOUNT_ID = data.aws_caller_identity.current.account_id
#    REGION     = var.region_name
#    DOCKER_TAG = module.base_pyspark_container.tag
#  }
#}
