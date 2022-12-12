"""
PySpark JDBC Extract Job.
"""
import argparse

from pyspark import SparkContext
from pyspark.sql import SparkSession, DataFrame
from hudi import DataFrameWriter

from codebase import get_logger
from codebase.extract import get_jdbc_url, JDBC_DRIVERS
from extract.utils import repartition_dataframe

SC = SparkContext()
SPARK = SparkSession.builder.appName("ExtractJDBCSource").getOrCreate()
LOGGER = get_logger()

ataGen = SC._jvm.org.apache.hudi.DataFrameWriter()


def get_secrets(arn: str):
    return "", ""


def main():
    """
    Main entrypoint.
    """
    jdbc_url = get_jdbc_url(
        engine=_engine,
        jdbc_params={
            "host": _host,
            "port": _port,
            "database": _database,
            "user": _user,
            "password": _password,
        },
    )

    LOGGER.info(
        "Read data from the database using the JDBC driver and connection parameters"
    )
    data_frame: DataFrame = (
        SPARK.read.format("jdbc")
        .option("url", jdbc_url)
        .option("driver", JDBC_DRIVERS[_engine])
        .option("dbtable", _table)
        .option("partitionColumn", _partition_column)
        .option("lowerBound", _lower_bound)
        .option("upperBound", _upper_bound)
        .option("numPartitions", _num_partitions)
        .load()
    )

    LOGGER.info(
        "Use the repartition method on the data frame to calculate skew partitions"
    )
    data_frame, num_partitions = repartition_dataframe(
        spark=SPARK, data_frame=data_frame
    )
    LOGGER.info(f"DataFrame has been repartitioned to num_partitions: {num_partitions}")

    LOGGER.info(f"Writing data to S3: {_s3_extract_uri}")
    data_frame.write.parquet(_s3_extract_uri)


if __name__ == "__main__":
    # Set up command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--engine", type=str, help="Database Engine")
    parser.add_argument(
        "--jdbc_secret_arn", type=str, help="The ARN to the JDBC Credentials"
    )
    parser.add_argument("--host", type=str, help="Database Host")
    parser.add_argument("--port", type=str, help="Database Port")
    parser.add_argument("--database", type=str, help="Database Name")
    parser.add_argument("--table", type=str, help="Database Table")
    parser.add_argument(
        "--lower_bound", type=str, help="Database lower range of values to be fetched"
    )
    parser.add_argument(
        "--upper_bound", type=str, help="Database upper range of values to be fetched"
    )
    parser.add_argument(
        "--partition_column",
        type=str,
        help="Column which should be used to determine partitions",
    )
    parser.add_argument(
        "--num_partitions", type=str, help="Number of partitions to be created"
    )
    parser.add_argument(
        "--s3_extract_uri",
        type=str,
        help="The S3 uri where the data will be written to.",
    )

    args = parser.parse_args()

    _engine = args["engine"]
    _user, _password = get_secrets(args["jdbc_secret_arn"])
    _host = args["host"]
    _port = args["port"]
    _database = args["database"]
    _table = args["table"]
    _lower_bound = args["lower_bound"]
    _upper_bound = args["upper_bound"]
    _partition_column = args["partition_column"]
    _num_partitions = args["num_partitions"]
    _s3_extract_uri = args["s3_extract_uri"]

    LOGGER.info("Starting PySpark Job.")
    try:
        main()
    except Exception as err:
        LOGGER.info(f"PySpark Job Failed with the error:\n{err}")
    LOGGER.info("PySpark Job Succeeded.")
