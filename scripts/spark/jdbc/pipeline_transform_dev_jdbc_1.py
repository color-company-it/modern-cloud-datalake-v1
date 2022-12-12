"""
PySpark JDBC Transform Job.
"""
import argparse

from pyspark.sql import SparkSession, DataFrame

from codebase import get_logger

# Set up SparkContext
SPARK = SparkSession.builder.appName("Transform JDBC Source").getOrCreate()
LOGGER = get_logger()


def main():
    """
    Main entrypoint.
    """
    LOGGER.info(f"Read the data frame from s3_extract_uri: {_s3_extract_uri}")
    data_frame: DataFrame = SPARK.read.parquet(_s3_extract_uri)

    LOGGER.info(
        f"Write data to Hudi structure in s3_transform_uri: {_s3_transform_uri}/hudi"
    )
    hudi_options = {
        "hoodie.table.name": _table,
        "hoodie.datasource.write.recordkey.field": "uuid",
        "hoodie.datasource.write.partitionpath.field": "partitionpath",
        "hoodie.datasource.write.table.name": _table,
        "hoodie.datasource.write.operation": "upsert",
        "hoodie.datasource.write.precombine.field": "ts",
        "hoodie.upsert.shuffle.parallelism": 2,
        "hoodie.insert.shuffle.parallelism": 2,
    }
    data_frame.write.format("hudi").options(**hudi_options).mode("overwrite").save(
        f"{_s3_transform_uri}/hudi"
    )


if __name__ == "__main__":
    # Set up command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--s3_extract_uri",
        type=str,
        help="The S3 uri where the data will be written to.",
    )
    parser.add_argument(
        "--s3_transform_uri",
        type=str,
        help="The S3 uri where the transformed data will be written to.",
    )
    parser.add_argument("--table", type=str, help="Database Table")

    args = parser.parse_args()

    _s3_extract_uri = args["s3_extract_uri"]
    _s3_transform_uri = args["s3_transform_uri"]
    _table = args["table"]

    LOGGER.info("Starting PySpark Job.")
    try:
        main()
    except Exception as err:
        LOGGER.info(f"PySpark Job Failed with the error:\n{err}")
    LOGGER.info("PySpark Job Succeeded.")
