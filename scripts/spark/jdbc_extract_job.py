"""
JDBC Extract

A PySpark job for extracting data from a JDBC source and saving it to a DynamoDB table using
non-parallel methods.

The job supports full extracts and partial extracts, and can be used to continue with the
extract on the next run, or reingest or rerun based on the success of the pipeline.

The job supports the following JDBC engines: postgres and mysql.
"""
import argparse
import datetime
import difflib
import json
import logging
from decimal import Decimal
from typing import Dict, Any, Tuple

import boto3
import mysql.connector
import psycopg2
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, current_timestamp, max, date_format
from pyspark.sql.types import *

JDBC_ENGINES: list = ["postgres", "mysql"]

JDBC_DRIVERS: dict = {
    "postgres": "org.postgresql.Driver",
    "mysql": "com.mysql.cj.jdbc.Driver",
}

SCHEMA_QUERY_MAPPING = {
    "postgres": 'SELECT column_name, data_type FROM information_schema.columns WHERE table_name = "{db_table}"',
    "mysql": "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = `{db_table}` AND table_schema = DATABASE()",
}

MIN_VALUES = {
    "IntegerType": -2147483648,
    "LongType": -9223372036854775808,
    "FloatType": -3.4028234663852886e38,
    "DoubleType": -1.7976931348623157e308,
    "DecimalType": Decimal("-999999999999999999999999999999999.9999999999999999"),
    "DateType": datetime.date(1, 1, 1),
    "TimestampType": datetime.datetime(1, 1, 1, 0, 0, 0),
}

# db_engine.source_dtype : spark_dtype
DATA_TYPE_MAPPING = {
    "postgres": {
        "bigint": LongType(),
        "boolean": BooleanType(),
        "integer": IntegerType(),
        "real": FloatType(),
        "timestamp without time zone": TimestampType(),
        "character varying": StringType(),
        "double precision": DoubleType(),
        "numeric": DecimalType(),
        "smallint": IntegerType(),
        "text": StringType(),
        "timestamp": TimestampType(),
        "date": DateType(),
        "time": StringType(),
        "timetz": StringType(),
        "timestamptz": TimestampType(),
        "interval": StringType(),
        "char": StringType(),
        "varchar": StringType(),
        "bytea": BinaryType(),
        "json": StringType(),
        "jsonb": StringType(),
        "uuid": StringType(),
        "inet": StringType(),
        "cidr": StringType(),
        "macaddr": StringType(),
        "bit": BinaryType(),
        "bit varying": BinaryType(),
        "xml": StringType(),
        "point": StringType(),
        "line": StringType(),
        "lseg": StringType(),
        "box": StringType(),
        "path": StringType(),
        "polygon": StringType(),
        "circle": StringType(),
    },
    "mysql": {
        "bigint": LongType(),
        "bit": BinaryType(),
        "boolean": BooleanType(),
        "char": StringType(),
        "date": DateType(),
        "datetime": TimestampType(),
        "decimal": DecimalType(),
        "double": DoubleType(),
        "enum": StringType(),
        "float": FloatType(),
        "int": IntegerType(),
        "integer": IntegerType(),
        "json": StringType(),
        "longblob": BinaryType(),
        "longtext": StringType(),
        "mediumblob": BinaryType(),
        "mediumint": IntegerType(),
        "mediumtext": StringType(),
        "numeric": DecimalType(),
        "real": FloatType(),
        "smallint": IntegerType(),
        "text": StringType(),
        "time": StringType(),
        "timestamp": TimestampType(),
        "tinyblob": BinaryType(),
        "tinyint": ByteType(),
        "tinytext": StringType(),
        "varbinary": BinaryType(),
        "varchar": StringType(),
        "year": IntegerType(),
    },
}

SECRETS = boto3.client("secretsmanager")
DDB = boto3.client("dynamodb")


def update_tracking_table(
    source: str,
    hwm_value: Any,
    lwm_value: Any,
    hwm_col_name: str,
    hwm_column_type: str,
    extract_type: str,
    extract_metadata: dict,
    extract_successful: str,
    tracking_table_name: str,
) -> None:
    """
    Inserts or updates an item in a DynamoDB table.

    If an item with the same partition key (source) already exists in the table,
    the item is updated with the new values. If no such item exists, a new item
    is inserted with the specified values.

    :params source (str): The partition key for the item.
    :params hwm_value (int): The value for the "hwm_value" field of the item.
    :params lwm_value (int): The value for the "lwm_value" field of the item.
    :params hwm_col_name (str): The value for the "hwm_col_name" field of the item.
    :params extract_type (str): The value for the "extract_type" field of the item.
    :params extract_metadata (dict): A dictionary containing the values for the "extract_metadata" field of the item.
    :params extract_successful (str): A Y or N to determine if the extract is successful.
    :params tracking_table_name (str): DDB Tracking Table name.
    """
    # Define the item to be inserted or updated
    item = {
        "source": {"S": source},
        "hwm_value": {"S": str(hwm_value)},
        "lwm_value": {"S": str(lwm_value)},
        "hwm_col_name": {"S": hwm_col_name},
        "hwm_column_type": {"S": hwm_column_type},
        "extract_type": {"S": extract_type},
        "updated_at": {"S": str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))},
        "extract_successful": {"S": extract_successful},
        "extract_metadata": {"S": json.dumps(extract_metadata)},
    }

    # Use the `put_item` method to insert or update the item
    DDB.put_item(TableName=tracking_table_name, Item=item)


def get_tracking_table_item(source: str, tracking_table_name: str) -> dict:
    """
    Retrieves an item from a DynamoDB table based on its partition key.

    :params source (str): The partition key of the item to be retrieved.
    :params tracking_table_name (str): DDB Tracking Table name.
    :returns: The item, as a dictionary. If the item does not exist, returns False.
    """

    # Define the key of the item to be retrieved
    key = {"source": {"S": source}}

    # Use the `get_item` method to retrieve the item
    response = DDB.get_item(TableName=tracking_table_name, Key=key)

    # Return the item if it exists, or None if it doesn't
    return response.get("Item", False)


def get_spark_logger(level=logging.INFO) -> logging.Logger:
    """
    Sets up a logger with log formatting.
    :param level: The log level. Defaults to logging.INFO.
    :returns: The logger object.
    """
    root = logging.getLogger()
    if root.handlers:
        for handler in root.handlers:
            root.removeHandler(handler)
    logging.basicConfig(
        level=level,
        format="[%(filename)s:%(lineno)s] %(asctime)-15s %(message)s",
        datefmt="%Y-%m-%d:%H:%M:%S",
    )
    return logging.getLogger(__name__)


def get_db_secret(secret_name):
    LOGGER.info(f"Getting DBSecret: {secret_name}")
    response = SECRETS.get_secret_value(SecretId=secret_name)
    return json.loads(response["SecretString"])


def convert_db_namespaces(extract_table: str, db_name: str, db_engine: str) -> str:
    """
    Converts the database namespaces in the specified extract table based on the database engine.

    :params extract_table: a string representing the extract table whose namespaces are to be converted.
    :params db_name: a string representing the name of the database.
    :params db_engine: a string representing the database engine (e.g. "postgres", "mysql").

    :returns: A string representing the converted database namespaces for the specified extract table.
    """
    if db_engine == "postgres":
        result = '"."'.join(extract_table.split("."))
        db_namespaces = f'"{db_name}"."{result}"'
    elif db_engine == "mysql":
        result = "`.`".join(extract_table.split("."))
        db_namespaces = f"`{db_name}`.`{result}`"
    else:
        raise EnvironmentError(f"The db_engine: {db_engine} is not supported")

    LOGGER.info(
        f"Converted db_namespaces using extract_table: "
        f"{extract_table}, db_name: {db_name}, and db_engine: {db_engine}.\n"
        f"To db_namespaces: {db_namespaces}"
    )
    return db_namespaces


def get_sql_where_condition(
    extract_type, lwm_value, hwm_col_name, hwm_value, hwm_column_type, reingest
):
    if extract_type == "FE":
        sql_where_condition = ""
    elif extract_type == "PE":
        if reingest:
            LOGGER.warning(
                "Source is being reingested, all original data may be overwritten!"
            )
            sql_where_condition = (
                f"WHERE {hwm_col_name} > '{MIN_VALUES[hwm_column_type]}'"
            )
        else:
            # if hwm is -1 it means we need to pull in all newest data
            if hwm_value == "-1":
                sql_where_condition = f"WHERE {hwm_col_name} > '{lwm_value}'"
            else:
                sql_where_condition = f"WHERE {hwm_col_name} > '{lwm_value}' and {hwm_col_name} <= '{hwm_value}'"
    else:
        raise EnvironmentError(f"The _extract_type: {extract_type} is not supported")

    LOGGER.info(f"Got SQL WHERE condition: {sql_where_condition}")
    return sql_where_condition


def get_jdbc_url(db_host: str, db_port: int, db_name: str, db_engine: str) -> str:
    """
    Returns a JDBC URL based on the specified database engine.

    :params db_host: a string representing the hostname of the database.
    :params db_port: an integer representing the port number of the database.
    :params db_name: a string representing the name of the database.
    :params db_engine: a string representing the database engine (e.g. "postgres", "mysql").
    :returns: A string representing the JDBC URL for the specified database.
    """
    if db_engine == "postgres":
        jdbc_url = f"jdbc:postgresql://{db_host}:{db_port}/{db_name}"
    elif db_engine == "mysql":
        jdbc_url = f"jdbc:mysql://{db_host}:{db_port}/{db_name}"
    else:
        raise EnvironmentError(f"The engine: {db_engine} is not supported")
    LOGGER.info(f"Got JDBC URL: {jdbc_url}")
    return jdbc_url


def get_pushdown_query(
    extract_table: str, sql_where_condition: str, db_name: str
) -> str:
    """
    Get a pushdown query to extract data from a database table.

    :params extract_table (str): The name of the table to extract data from.
    :params sql_where_condition (str): The WHERE clause to use in the SELECT statement.
    :params db_name (str): The name of the database.
    :returns: A string representing the pushdown query.
    """
    pushdown_query = (
        f"(SELECT * FROM {extract_table} {sql_where_condition}) {db_name}_alias"
    )
    LOGGER.info(f"Got pushdown query: {pushdown_query}")
    return pushdown_query


def get_num_partitions(data_frame: DataFrame, rows_per_partition: int = 1000) -> int:
    """
    Calculates the number of repartitions for a PySpark JDBC extract process, taking into account data skew.
    It is generally recommended to set the number of rows per partition to a value that is large enough
    to minimize the overhead of data shuffling and partitioning, but small enough to ensure that
    the data can be distributed evenly across the available resources.

    :param data_frame: A DataFrame containing a sample of the data to extract.
    :param rows_per_partition: The target number of rows per partition.

    :returns: The number of repartitions.
    """
    num_rows = data_frame.count()
    if num_rows == 0:
        return 1

    # Calculate the average number of rows per partition
    avg_rows_per_partition = num_rows / data_frame.rdd.getNumPartitions()
    LOGGER.info(f"Average rows per partition: {avg_rows_per_partition}")

    # Calculate the skew factor
    skew_factor = avg_rows_per_partition / rows_per_partition
    LOGGER.info(f"Skew factor: {skew_factor}")

    # Adjust the number of repartitions based on the skew factor
    num_partitions = int(num_rows / (rows_per_partition * skew_factor))

    # Ensure that there is at least one partition
    if num_partitions == 0:
        num_partitions = 1

    LOGGER.info(f"Num partitions to repartition by: {num_partitions}")

    return num_partitions


def get_column_data_types(
    engine: str,
    host: str,
    port: int,
    database: str,
    user: str,
    password: str,
    table_name: str,
) -> Dict[str, str]:
    """
    Get the data types of the columns in a database table.

    :params engine (str): The database engine.
    :params host (str): The hostname of the database server.
    :params port (int): The port number of the database server.
    :params database (str): The name of the database.
    :params user (str): The username to use for connecting to the database.
    :params password (str): The password to use for connecting to the database.
    :params table_name (str): The name of the table.
    :returns: A dictionary mapping column names to data types.
    """

    if engine == "postgres":
        conn = psycopg2.connect(
            host=host, port=port, database=database, user=user, password=password
        )
        query = f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table_name}'"
    elif engine == "mysql":
        conn = mysql.connector.connect(
            host=host, port=port, database=database, user=user, password=password
        )
        query = f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table_name}'"
    else:
        raise EnvironmentError(f"The engine: {engine} is not supported")

    cursor = conn.cursor()

    # Query the database to get the column names and data types
    cursor.execute(query)

    # Fetch the results of the query
    column_data_types = cursor.fetchall()

    # Create a dictionary to store the column names and data types
    column_data_type_dict = {}

    # Iterate through the column data types and add them to the dictionary
    for column_data_type in column_data_types:
        column_name, data_type = column_data_type
        column_data_type_dict[column_name] = data_type

    return column_data_type_dict


def create_db_table_schema(
    db_engine: str,
    db_host: str,
    db_port: int,
    db_name: str,
    db_user: str,
    db_password: str,
    extract_table: str,
) -> StructType:
    """
    Create the schema for a database table by inferring the data types of the columns.

    :params db_engine (str): The database engine.
    :params db_host (str): The hostname of the database server.
    :params db_port (int): The port number of the database server.
    :params db_name (str): The name of the database.
    :params db_user (str): The username to use for connecting to the database.
    :params db_password (str): The password to use for connecting to the database.
    :params extract_table (str): The name of the table to extract.
    :returns: A StructType object representing the schema of the table.
    """
    LOGGER.info(f"Getting {extract_table} schema for inferring datatypes.")
    db_table = extract_table.split(".")[-1]

    # Convert the DataFrame to a dictionary
    source_schema: dict = get_column_data_types(
        engine=db_engine,
        host=db_host,
        port=db_port,
        database=db_name,
        user=db_user,
        password=db_password,
        table_name=db_table,
    )
    spark_schema: dict = DATA_TYPE_MAPPING[db_engine]
    LOGGER.info(f"Source Schema: {source_schema}")
    new_schema_struct = []
    for source_column, source_type in source_schema.items():
        closest_match = difflib.get_close_matches(source_type, spark_schema.keys())
        if closest_match:
            LOGGER.info(
                f"Casting column: {source_column} from {source_type} to {spark_schema[closest_match[0]]}"
            )
            new_schema_struct.append(
                StructField(source_column, spark_schema[closest_match[0]], True)
            )
        else:
            LOGGER.info(
                f"Casting column: {source_column} from {source_type} to StringType"
            )
            new_schema_struct.append(StructField(source_column, StringType(), True))

    return StructType(new_schema_struct)


def add_url_safe_current_time(data_frame: DataFrame) -> DataFrame:
    """
    Adds a column to the given data frame with the current timestamp in a format safe for use in URIs.
    """
    data_frame = data_frame.withColumn("jdbc_extract_time", current_timestamp())
    data_frame = data_frame.withColumn(
        "jdbc_extract_time",
        date_format(col("jdbc_extract_time"), "yyyy-MM-dd_hh-mm-ss"),
    )
    return data_frame


def determine_extract_plan(
    provided_hwm_value: Any,
    provided_lwm_value: Any,
    extract_type: str,
    tracking_table: Dict[str, Any],
) -> Tuple[Any, Any]:
    # return the provided values if FE and that's it
    if extract_type == "FE":
        return provided_hwm_value, provided_lwm_value

    # determine if this is a new run, then return the provided values or ddb values
    elif extract_type == "PE":
        if tracking_table:
            return tracking_table["hwm_value"]["S"], tracking_table["lwm_value"]["S"]
        return provided_hwm_value, provided_lwm_value

    else:
        raise ValueError(f"Extract type {extract_type} is not supported")


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
    update_tracking_table(
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
        update_tracking_table(
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
        update_tracking_table(
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
    parser.add_argument("--db_engine", type=str, help="Database engine")
    parser.add_argument("--db_secret", type=str, help="AWS SecretsManager name")
    parser.add_argument("--db_host", type=str, help="Database host")
    parser.add_argument("--db_port", type=int, help="Database port")
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
    parser.add_argument("--reingest", type=str, default=False, help="Reingest flag")
    parser.add_argument(
        "--tracking_table_name", type=str, help="The DynamoDB tracking table name"
    )
    parser.add_argument("--jars", type=str, help="Add an external jar to the classpath")

    args = parser.parse_args()
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

    SPARK = (
        SparkSession.builder.appName(f"ExtractJob.{_source}")
        .config("spark.jars", _jars)
        .getOrCreate()
    )

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
