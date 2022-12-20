"""
PySpark JDBC Extract Job.

This job extracts data from a JDBC source by connecting to a JDBC URL and reading data from a table
using a SQL pushdown query. The job can be parameterized with options to customize the extract process,
such as specifying the type of extract, the database engine, the extract table, and the database host
and port. The job can also be configured to repartition the extracted dataframe and write the results
to a specified S3 URI.
"""
import argparse
import os

from pyspark import SparkContext
from pyspark.sql import SparkSession, DataFrame

from codebase import get_logger
from codebase.aws.secrets import SecretsManager
from codebase.etl import get_jdbc_url, repartition_dataframe
from codebase.etl.extract import (
    generate_sql_where_condition,
    generate_sql_pushdown_query,
    jdbc_read,
    add_jdbc_extract_time_field,
    parse_extract_table,
)

SC = SparkContext()
SPARK = SparkSession.builder.appName("ExtractJDBCSource").getOrCreate()
LOGGER = get_logger()
SECRETS: SecretsManager = SecretsManager(
    region_name=os.getenv("region_name", "eu-west-1")
)


def main():
    """
    Main entrypoint.
    """
    jdbc_url = get_jdbc_url(
        engine=_engine,
        jdbc_params={
            "host": _db_host,
            "port": _db_port,
            "database": _db_name,
            "user": _db_user,
            "password": _db_password,
        },
    )

    LOGGER.info("Construct SQL Where condition")
    sql_where_condition = generate_sql_where_condition(
        hwm_col_name=_hwm_col_name,
        hwm_value=_hwm_value,
        lwm_value=_lwm_value,
        extract_type=_extract_type,
    )
    LOGGER.info(f"sql_where_condition: {sql_where_condition}")

    LOGGER.info("Construct SQ Pushdown Query")
    sql_pushdown_query = generate_sql_pushdown_query(
        sql_where_condition=sql_where_condition, extract_table=_extract_table
    )
    LOGGER.info(f"sql_pushdown_query: {sql_pushdown_query}")

    data_frame: DataFrame = jdbc_read(
        jdbc_url=jdbc_url, sql_pushdown_query=sql_pushdown_query
    )
    data_frame = add_jdbc_extract_time_field(data_frame=data_frame)
    LOGGER.info(f"DataFrame Schema: {data_frame.printSchema()}")

    if _repartition_dataframe:
        data_frame, partition_num = repartition_dataframe(
            spark=SPARK, data_frame=data_frame
        )
        LOGGER.info(f"Repartitioned DataFrame with partition_num: {partition_num}")

    LOGGER.info(f"Writing DatFrame to: {_extract_s3_uri}")
    data_frame.write.mode("append").parquet(_extract_s3_uri)


if __name__ == "__main__":
    # Set up command-line arguments
    _parser = argparse.ArgumentParser()
    _parser.add_argument(
        "--extract_type",
        type=str,
        help="The type of extract to perform (e.g. FE, PE)",
    )
    _parser.add_argument(
        "--engine", type=str, help="The database engine to use (e.g. postgres, mysql)"
    )
    _parser.add_argument(
        "--extract_table",
        type=str,
        help="The table _namespace used in the SQL from clause (e.g. db.schema.table_name)",
    )
    _parser.add_argument(
        "--db_host", type=str, help="The hostname of the database server"
    )
    _parser.add_argument("--db_port", type=str, help="The port of the database server")
    _parser.add_argument(
        "--aws_secret_arn",
        type=str,
        help="The ARN of the AWS secret containing the database credentials",
    )
    _parser.add_argument("--db_name", type=str, help="The name of the database")
    _parser.add_argument(
        "--db_user",
        type=str,
        help="The username to use when connecting to the database",
    )
    _parser.add_argument(
        "--db_password",
        type=str,
        help="The password to use when connecting to the database",
    )
    _parser.add_argument(
        "--hwm_col_name",
        type=str,
        help="The name of the column to use as the high watermark",
    )
    _parser.add_argument("--hwm_value", type=str, help="The value of the high watermark")
    _parser.add_argument("--lwm_value", type=str, help="The value of the low watermark")
    _parser.add_argument("--partition_column", type=str, help="The column to partition on during extract")
    _parser.add_argument("--num_partitions", type=str)
    _parser.add_argument("--upper_bound", type=str, help="")
    _parser.add_argument("--lower_bound", type=str, help="")
    _parser.add_argument("--fetchsize", type=str)
    _parser.add_argument(
        "--repartition_dataframe",
        type=bool,
        help="Whether to repartition the dataframe",
    )
    _parser.add_argument(
        "--extract_s3_uri", type=str, help="The S3 URI to write the extracted data to"
    )

    # Parse the command-line arguments
    _namespace, _ = _parser.parse_known_args()
    _extract_type = _namespace.extract_type
    _engine = _namespace.engine
    _extract_table = _namespace.extract_table

    _db_name, _db_schema, _db_table = parse_extract_table(extract_table=_extract_table)
    _db_host = _namespace.db_host
    _db_port = _namespace.db_port
    _db_user, _db_password = SECRETS.get_secrets_dict(
        secrets_name=_namespace.aws_secret_arn
    )

    _hwm_col_name = _namespace.hwm_col_name
    _hwm_value = _namespace.hwm_value
    _lwm_value = _namespace.lwm_value

    _partition_column = _namespace.partition_column
    _num_partitions = _namespace.num_partitions

    _lower_bound = _namespace.lower_bound
    _upper_bound = _namespace.upper_bound
    _fetchsize = _namespace.fetchsize

    _repartition_dataframe = _namespace.repartition_dataframe
    _extract_s3_uri = _namespace.extract_s3_uri

    LOGGER.info("Starting PySpark Job.")
    try:
        main()
    except Exception as err:
        LOGGER.info(f"PySpark Job Failed with the error:\n{err}")
        raise err
    LOGGER.info("PySpark Job Succeeded.")
