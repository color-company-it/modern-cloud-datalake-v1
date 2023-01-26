import logging
from typing import List

from pyspark.sql import DataFrame
from pyspark.sql.functions import col, concat_ws
from pyspark.sql.types import StructType, StructField

from codebase.etl import DATA_TYPE_MAPPING


def generate_schema(schema_dict: dict, db_engine: str) -> StructType:
    """
    Generates the schema of a given DataFrame with the provided schema mapping
    in the config.

    :return: StructType representing the schema of the input DataFrame
    """
    struct_list = []
    for column_name, column_type in schema_dict.items():
        spark_col_type = DATA_TYPE_MAPPING[db_engine][column_type]
        struct_list.append(StructField(column_name, spark_col_type, True))
    return StructType(struct_list)


def create_partition_key(data_frame: DataFrame, columns: List[str]) -> DataFrame:
    """
    This function creates a combined partition key by concatenating the values of specified columns of a DataFrame.
    :param data_frame: DataFrame on which the partition key is to be created
    :param columns: list of column names to be used for creating the partition key
    :return: DataFrame with new column 'partition_key'
    """
    logging.info("Creating the partition key")
    partition_key = concat_ws("_", *[col(column) for column in columns])
    logging.info("Adding the partition key to the DataFrame")
    return data_frame.withColumn("partition_key", partition_key)
