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

from awsglue.context import GlueContext
from awsglue.transforms import *
from pyspark.context import SparkContext
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, max

from codebase.aws.ddb import get_tracking_table_item, update_extract_tracking_table
from codebase.aws.secrets import get_db_secret
from codebase.etl import (
    JDBC_DRIVERS,
    get_num_partitions,
    add_url_safe_current_time,
    get_spark_logger,
    MIN_VALUES,
)
from codebase.etl.extract import (
    determine_extract_plan,
    get_jdbc_url,
    get_sql_where_condition,
    convert_db_namespaces,
    get_pushdown_query,
    create_db_table_schema,
)

NOW = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")


def main():
    tracking_table = get_tracking_table_item(
        source=_source, tracking_table_name=_tracking_table_name
    )

    hwm_value, lwm_value = determine_extract_plan(
        provided_hwm_value=_hwm_value,
        provided_lwm_value=_lwm_value,
        extract_type=_extract_type,
        tracking_table=tracking_table,
    )

    # update the tracking table with new or existing data
    # if row_count is -1 it means the pipeline is running OR it failed
    # during the last run
    update_extract_tracking_table(
        source=_source,
        hwm_value=hwm_value,
        lwm_value=lwm_value,
        hwm_col_name=_hwm_col_name,
        hwm_column_type=_hwm_column_type,
        extract_type=_extract_type,
        extract_metadata={"row_count": -1},
        extract_successful="N",
        tracking_table_name=_tracking_table_name,
    )

    jdbc_url = get_jdbc_url(
        db_host=_db_host, db_port=_db_port, db_name=_db_name, db_engine=_db_engine
    )
    sql_where_condition = get_sql_where_condition(
        extract_type=_extract_type,
        hwm_col_name=_hwm_col_name,
        lwm_value=lwm_value,
        hwm_value=hwm_value,
        hwm_column_type=_hwm_column_type,
        reingest=_reingest,
    )
    extract_table_namespace = convert_db_namespaces(
        extract_table=_extract_table, db_name=_db_name, db_engine=_db_engine
    )
    pushdown_query = get_pushdown_query(
        extract_table=extract_table_namespace,
        sql_where_condition=sql_where_condition,
        db_name=_db_name,
    )

    _jdbc_params = {
        "url": jdbc_url,
        "properties": {
            "user": _db_user,
            "password": _db_password,
            "driver": JDBC_DRIVERS[_db_engine],
            "encrypt": "true",
            "trustServerCertificate": "true",
            "applicationIntent": "ReadOnly",
        },
        "table": pushdown_query,
    }

    source_schema = create_db_table_schema(
        db_engine=_db_engine,
        db_host=_db_host,
        db_port=_db_port,
        db_name=_db_name,
        db_user=_db_user,
        db_password=_db_password,
        extract_table=_extract_table,
    )

    # If the bounds are not set (-1) then do not use them.
    LOGGER.info("Extracting data from JDBC source")
    data_frame: DataFrame = (
        SPARK.read.option("partitionColumn", _partition_column)
        .option("lowerBound", _lower_bound)
        .option("upperBound", _upper_bound)
        .option("numPartitions", _num_partitions)
        .option("fetchsize", _fetchsize)
        .option("schema", source_schema)
        .jdbc(**_jdbc_params)
    )

    if data_frame.count() > 0:
        if _repartition_dataframe:
            num_partitions = get_num_partitions(data_frame=data_frame)
            LOGGER.info(f"Repartitioning DataFrame with {num_partitions} partitions")
            data_frame = data_frame.repartition(num_partitions)

        data_frame = add_url_safe_current_time(data_frame=data_frame)

        LOGGER.info("Printing Schema:")
        data_frame.printSchema()

        if _reingest or _extract_type == "FE":
            LOGGER.info(
                f"Overwriting the directory before the extract write to: {_extract_s3_uri}"
            )
            data_frame.write.mode("overwrite").partitionBy(
                _extract_s3_partitions
            ).parquet(_extract_s3_uri)
        else:
            LOGGER.info(f"Writing data to: {_extract_s3_uri}")
            data_frame.write.mode("append").partitionBy(_extract_s3_partitions).parquet(
                _extract_s3_uri
            )

        # Update the hwm and lwm value for the next run, since we want to move to the next
        # hwm and lwm values, the hwm_value is turned off and lwm value is set to the max
        if _extract_type == "PE":
            max_db_value = str(
                data_frame.select(max(col(_partition_column)).alias("max_col"))
                .first()
                .max_col
            )
            lwm_value = max_db_value
            hwm_value = "-1"
            LOGGER.info(
                f"Updating DBB watermarks hwm_value: {hwm_value} and lwm_value: {lwm_value}"
            )

        # Once the job completes without any issues, update the table with successful data
        LOGGER.info("Updating tracking table")
        update_extract_tracking_table(
            source=_source,
            hwm_value=hwm_value,
            lwm_value=lwm_value,
            hwm_col_name=_hwm_col_name,
            hwm_column_type=_hwm_column_type,
            extract_type=_extract_type,
            extract_metadata={"row_count": data_frame.count()},
            extract_successful="Y",
            tracking_table_name=_tracking_table_name,
        )
    else:
        # set to the original setup since there was no data to extract
        update_extract_tracking_table(
            source=_source,
            hwm_value=tracking_table["hwm_value"]["S"],
            lwm_value=tracking_table["lwm_value"]["S"],
            hwm_col_name=_hwm_col_name,
            hwm_column_type=_hwm_column_type,
            extract_type=_extract_type,
            extract_metadata={"row_count": data_frame.count()},
            extract_successful="Y",
            tracking_table_name=_tracking_table_name,
        )


if __name__ == "__main__":
    LOGGER = get_spark_logger()
    parser = argparse.ArgumentParser()
    parser.add_argument("--job_name", type=str, help="Glue Job Name")
    parser.add_argument("--db_engine", type=str, help="Database engine")
    parser.add_argument("--db_secret", type=str, help="AWS SecretsManager name")
    parser.add_argument("--db_host", type=str, help="Database host")
    parser.add_argument("--db_port", type=str, help="Database port")
    parser.add_argument("--db_name", type=str, help="Database name")
    parser.add_argument("--partition_column", type=str, help="Partition column")
    parser.add_argument("--hwm_column_type", type=str, help="HWM column type")
    parser.add_argument("--lower_bound", type=str, help="Lower bound")
    parser.add_argument("--upper_bound", type=str, help="Upper bound")
    parser.add_argument("--num_partitions", type=str, help="Number of partitions")
    parser.add_argument("--fetchsize", type=str, help="Fetch size")
    parser.add_argument("--extract_table", type=str, help="Extract table")
    parser.add_argument("--extract_type", type=str, help="Extract type")
    parser.add_argument("--hwm_col_name", type=str, help="HWM column name")
    parser.add_argument("--lwm_value", type=str, help="LWM value")
    parser.add_argument("--hwm_value", type=str, default="1000", help="HWM value")
    parser.add_argument(
        "--repartition_dataframe", type=str, default=True, help="Repartition dataframe"
    )
    parser.add_argument("--extract_s3_uri", type=str, help="Extract S3 URI")
    parser.add_argument(
        "--extract_s3_partitions",
        type=str,
        help="Comma separated strings to partition by",
    )
    parser.add_argument("--reingest", type=str, default="false", help="Reingest flag")
    parser.add_argument(
        "--tracking_table_name", type=str, help="The DynamoDB tracking table name"
    )
    parser.add_argument("--jars", type=str, help="Add an external jar to the classpath")

    args, _ = parser.parse_known_args()
    _job_name = args.job_name
    _db_secret = get_db_secret(secret_name=args.db_secret)
    _db_engine = args.db_engine
    _db_user = _db_secret["db_user"]
    _db_password = _db_secret["db_password"]
    _db_host = _db_secret["db_host"]
    _db_port = args.db_port
    _db_name = args.db_name
    _partition_column = args.partition_column
    _hwm_column_type = args.hwm_column_type
    _lower_bound = args.lower_bound
    _upper_bound = args.upper_bound
    _num_partitions = args.num_partitions
    _fetchsize = args.fetchsize
    _extract_table = args.extract_table
    _extract_type = args.extract_type
    _hwm_col_name = args.hwm_col_name
    _lwm_value = args.lwm_value
    _hwm_value = args.hwm_value
    _repartition_dataframe = args.repartition_dataframe
    _extract_s3_uri = args.extract_s3_uri
    _extract_s3_partitions = args.extract_s3_partitions.split(",")
    _reingest = args.reingest
    _source = f"{_db_name}.{_extract_table}"
    _tracking_table_name = args.tracking_table_name
    _jars = args.jars

    # Ensure booleans are booleans, default to false
    _repartition_dataframe = bool(_repartition_dataframe.lower() in ["true", "y", "1"])
    _reingest = bool(_reingest.lower() in ["true", "y", "1"])

    sc = SparkContext()
    glueContext = GlueContext(sc)
    SPARK = glueContext.spark_session

    # make sure _hwm_column_type is supported
    if _hwm_column_type not in MIN_VALUES:
        raise EnvironmentError(
            f"The provided hwm_column_type: {_hwm_column_type} is not supported"
        )

    LOGGER.info("Starting Extract Job")
    try:
        main()
    except Exception as error:
        # To log the error to the user console as reference
        LOGGER.info("An error was raised:", error)
        raise error from error
    LOGGER.info("Job Complete!")
