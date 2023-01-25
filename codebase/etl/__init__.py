import datetime
import logging
from decimal import Decimal
from typing import List

from pyspark.sql import DataFrame
from pyspark.sql.functions import col, current_timestamp, date_format, sha2, concat
from pyspark.sql.types import *


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
    logging.info(f"Average rows per partition: {avg_rows_per_partition}")

    # Calculate the skew factor
    skew_factor = avg_rows_per_partition / rows_per_partition
    logging.info(f"Skew factor: {skew_factor}")

    # Adjust the number of repartitions based on the skew factor
    num_partitions = int(num_rows / (rows_per_partition * skew_factor))

    # Ensure that there is at least one partition
    if num_partitions == 0:
        num_partitions = 1

    logging.info(f"Num partitions to repartition by: {num_partitions}")

    return num_partitions


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


def add_hash_column(data_frame: DataFrame, columns_to_hash: List[str]) -> DataFrame:
    """
    Add a hash column to the DataFrame, containing the SHA-256 hash of the specified columns.
    :param data_frame: DataFrame to add the hash column to.
    :param columns_to_hash: List of column names to include in the hash.
    :return: DataFrame with the new hash column.
    """
    hash_col = sha2(concat(*[col(c) for c in columns_to_hash]), 256).alias("hash")
    return data_frame.withColumn("hash", hash_col)
