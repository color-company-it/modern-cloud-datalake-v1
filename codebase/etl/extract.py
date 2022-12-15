"""
This module contains a collection of methods
used to dynamically allocate the ideal amount
of resources for an extract job.
"""
import math

from codebase.infrastructure_mappings import EXTRACT_TYPES
import time

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import lit


def generate_sql_where_condition(
    hwm_col_name: str, lwm_value: str, hwm_value: str, extract_type: str
) -> str:
    """
    Generate a SQL WHERE condition that filters records by a high watermark column.

    :param hwm_col_name: The name of the high watermark column.
    :param lwm_value: The low watermark value for the high watermark column.
    :param hwm_value: The high watermark value for the high watermark column.
    :param extract_type: Either `FE` for full extract, or `PE` for partial extract.
    :returns: A string containing the generated SQL WHERE condition.
    """

    if extract_type == "FE":
        return ""
    if extract_type == "PE":
        return f"""
    WHERE {hwm_col_name} > {lwm_value} and {hwm_col_name} <= {hwm_value}
    """.strip()

    raise ValueError(
        f"The provided extract_type: {extract_type} is not a supported one"
        f"of {EXTRACT_TYPES} for the generate_sql_where_condition method"
    )


def generate_sql_pushdown_query(extract_table: str, sql_where_condition: str) -> str:
    """
    Generate a SQL Pushdown query using a FROM clause, WHERE condition, and table name.

    :param extract_table: The namespace of the table being extracted, such as
                          db_name.db_schema.db_table or whatever other namespace is
                          applicable.
    :param sql_where_condition: SQL WHERE condition to be used in the query
    :returns: A string representing the generated SQL Pushdown query
    """
    return f"""
    (SELECT * FROM {extract_table} {sql_where_condition}) {extract_table.split('.')[-1]}_alias
    """.strip()


def parse_extract_table(extract_table: str) -> dict:
    """
    Parse the extract_table variable and return a dictionary containing the database name, schema, and table name.

    :param extract_table: A string representing the database, schema, and table to be extracted in the format of
    "<db_name>.<db_schema>.<db_table>" or "<db_name>.<db_table>" or "<db_table>"
    :returns: A dictionary containing the database name, schema, and table name
    :raises ValueError: If the extract_table variable does not have one of the three formats mentioned above
    """
    parts = extract_table.split(".")

    # Return a dictionary containing the database name, schema, and table name
    # The value of each key is set to None if not specified in the extract_table variable
    return {
        "db_name": parts[0] if len(parts) >= 1 else None,
        "db_schema": parts[1] if len(parts) >= 2 else None,
        "db_table": parts[2] if len(parts) >= 3 else None,
    }


def add_jdbc_extract_time_field(data_frame: DataFrame) -> DataFrame:
    """Returns the current ISO time in seconds"""
    return data_frame.withColumn("jdbc_extract_time", lit(int(time.time())))


def jdbc_read(
    spark: SparkSession,
    jdbc_url: str,
    sql_pushdown_query: str,
    driver: str,
    partition_column: str,
    lower_bound: int,
    upper_bound: int,
    num_partitions: int,
    fetchsize: int,
) -> DataFrame:
    """
    Reads data from a JDBC source using the specified JDBC URL and SQL pushdown query.
    The function can be parameterized with options to customize the JDBC read process, such
    as specifying a fetch size and partitioning options.
    """
    data_frame = (
        spark.read.format("jdbc")
        .option("url", jdbc_url)
        .option("driver", driver)
        .option("dbtable", sql_pushdown_query)
        .option("partitionColumn", partition_column)
        .option("lowerBound", lower_bound)
        .option("upperBound", upper_bound)
        .option("numPartitions", num_partitions)
    )
    if fetchsize:
        data_frame = data_frame.option("fetchsize", fetchsize)
    return data_frame.load()


def get_hwm_and_lwm_values(data_frame: DataFrame, field: str) -> tuple:
    """
    Get the hwm_value and lwm_value of a field in a PySpark data frame.

    :param data_frame: PySpark data frame
    :param field: Name of the field
    :returns: A tuple containing the hwm_value and lwm_value of the field in the data frame
    """

    # Calculate the hwm_value and lwm_value using the max() and min() functions
    hwm_value = data_frame.select(max(field)).first()[0]
    lwm_value = data_frame.select(min(field)).first()[0]

    # Return the hwm_value and lwm_value
    return hwm_value, lwm_value
