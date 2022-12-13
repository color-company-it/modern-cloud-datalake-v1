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
