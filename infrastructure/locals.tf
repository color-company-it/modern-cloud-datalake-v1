locals {
  etl_stages                = ["extract", "transform", "load"]
  additional_python_modules = "mysql-connector-python==8.0.31,psycopg2-binary==2.9.5"
}