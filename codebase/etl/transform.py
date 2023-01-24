from typing import List

from pyspark.pandas import DataFrame
from pyspark.sql.functions import struct, col, concat, concat_ws
from pyspark.sql.types import StructType


def generate_schema(data_frame: DataFrame) -> StructType:
    """
    Generates the schema of a given DataFrame

    :param df: DataFrame to generate schema for
    :return: StructType representing the schema of the input DataFrame
    """
    return data_frame.select(
        *(struct(col(c).alias(c) for c in data_frame.columns)).schema().fields
    )


def create_partition_key(df: DataFrame, columns: List[str]) -> DataFrame:
    """
    This function creates a combined partition key by concatenating the values of specified columns of a DataFrame.
    :param df: DataFrame on which the partition key is to be created
    :param columns: list of column names to be used for creating the partition key
    :return: DataFrame with new column 'partition_key'
    """
    # Creating the partition key
    partition_key = concat_ws("_", *[col(column) for column in columns])
    # Adding the partition key to the DataFrame
    return df.withColumn("partition_key", partition_key)
