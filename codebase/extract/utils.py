import time

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import lit


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


def repartition_dataframe(
    spark: SparkSession, data_frame: DataFrame
) -> [DataFrame, int]:
    """
    This method takes a dataframe as an input, calculates the ideal number
    of partitions based on the default parallelism, and repartitions the
    dataframe accordingly. It then returns the repartitioned dataframe.

    It does so by:
    1. Getting the default parallelism of the SparkContext
    2. Calculating the ideal number of partitions for the dataframe
    3. Repartitioning the dataframe with the calculated number of partitions

    :param spark: The SparkSession to get the defaultParallelism
    :param data_frame: The DataFrame to be repartitioned.
    :return: The repartitioned DataFrame and the repartition number
    """

    default_parallelism = spark.sparkContext.defaultParallelism
    num_partitions = int(data_frame.count() / default_parallelism)
    return data_frame.repartition(num_partitions), num_partitions


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
