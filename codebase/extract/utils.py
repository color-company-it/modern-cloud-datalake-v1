from pyspark.sql import SparkSession, DataFrame


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
