"""
JDBC Extract

A Glue Job using PySpark for extracting data from a JDBC source and saving it to a DynamoDB table using
non-parallel methods.

The job supports full extracts and partial extracts, and can be used to continue with the
extract on the next run, or reingest or rerun based on the success of the pipeline.

The job supports the following JDBC engines: postgres and mysql.
"""
import argparse
import datetime
import json
import sys

if "glue" in sys.modules:
    from awsglue.context import GlueContext
    from awsglue.transforms import *

from pyspark.context import SparkContext
from pyspark.sql import SparkSession

from codebase.etl import (
    get_spark_logger,
    add_url_safe_current_time,
)
from codebase.etl.contexts import get_hudi_options, set_spark_for_hudi
from codebase.etl.transform import create_partition_key, generate_schema

NOW = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")


def main():
    hudi_options = get_hudi_options(
        table_name=_hudi_table,
        record_key=_record_key,
        partition_path="jdbc_extract_time",
        precombine_filed="partition_key",
    )

    # if schema object is provided, apply it, else do nothing
    if _schema:
        table_schema = generate_schema(schema_dict=_schema, db_engine=_db_engine)
        data_frame = SPARK.read.schema(table_schema).parquet(_extract_s3_uri)
    else:
        data_frame = SPARK.read.parquet(_extract_s3_uri)

    data_frame = create_partition_key(data_frame=data_frame, columns=data_frame.columns)

    # Add transform date
    data_frame, job_partition_key = add_url_safe_current_time(
        data_frame=data_frame, etl_stage="transform"
    )

    # clean up all column names
    data_frame = data_frame.toDF(*[column.lower() for column in data_frame.columns])

    # Write Hudi Current View
    _transform_s3_uri_hudi = f"{_transform_s3_uri}/hudi/"
    LOGGER.info(f"Writing Current View to {_transform_s3_uri_hudi}")
    data_frame.write.format("hudi").options(**hudi_options).mode("append").save(
        _transform_s3_uri_hudi
    )

    # Write Hudi Delta View
    _transform_s3_uri_delta = f"{_transform_s3_uri}/delta/"
    LOGGER.info(f"Writing Current View to {_transform_s3_uri_hudi}")
    data_frame.write.partitionBy(job_partition_key).mode("overwrite").save(
        _transform_s3_uri_hudi
    )


if __name__ == "__main__":
    LOGGER = get_spark_logger()
    parser = argparse.ArgumentParser()
    parser.add_argument("--job_name", type=str, help="Glue Job Name")
    parser.add_argument("--db_name", type=str, help="Database name")
    parser.add_argument("--db_table", type=str, help="DB table")
    parser.add_argument("--db_engine", type=str, help="Database engine")
    parser.add_argument("--record_key", type=str, help="DB Primary Key")
    parser.add_argument(
        "--partition_key", type=str, help="The precombined or single partition key"
    )
    parser.add_argument(
        "--schema", type=str, help="Key Value Pairs for DB Schema", default="{}"
    )
    parser.add_argument("--extract_s3_uri", type=str, help="Extract S3 URI")
    parser.add_argument("--transform_s3_uri", type=str, help="Transform S3 URI")

    args, _ = parser.parse_known_args()
    _job_name = args.job_name
    _db_name = args.db_name
    _db_table = args.extract_table
    _db_engine = args.db_engine
    _hudi_table = f"{_db_name}_{_db_table}".replace(".", "_").lower()
    _record_key = args.record_key
    _schema = json.loads(args.schema)
    _extract_s3_uri = args.extract_s3_uri
    _transform_s3_uri = args.transform_s3_uri

    sc = SparkContext()
    if "glue" in sys.modules:
        glueContext = GlueContext(sc)
        SPARK = glueContext.spark_session
    else:
        LOGGER.info("Glue libraries not found, continuing with the SparkContext")
        SPARK = SparkSession.builder.getOrCreate()

    SPARK = set_spark_for_hudi(spark=SPARK)

    LOGGER.info("Starting Extract Job")
    try:
        main()
    except Exception as error:
        # To log the error to the user console as reference
        LOGGER.info("An error was raised:", error)
        raise error from error
    LOGGER.info("Job Complete!")
