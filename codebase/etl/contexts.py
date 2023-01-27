"""
Hudi (Hadoop Upserts and Incremental Handling) is a storage layer for big data that enables incremental
and upsert operations on large datasets stored in Apache Hive or Apache Hadoop Distributed File System (HDFS).
"""
import logging

from pyspark.sql import SparkSession


def set_spark_for_hudi(spark: SparkSession) -> SparkSession:
    """
    The function sets up the Spark environment for Hudi by configuring the following:
    1. spark.serializer: The KryoSerializer is more performant with Hudi in Spark and Glue.
    2. spark.sql.catalog.spark_catalog: The HoodieCatalog is used for interacting with the Hudi catalog.
    3. spark.sql.extensions: The HoodieSparkSessionExtension is used to add the Hoodie functions to SparkSession.
    """
    logging.info("Setting up the Spark Environment for Hudi")
    spark.conf.set("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
    spark.conf.set(
        "spark.sql.catalog.spark_catalog",
        "org.apache.spark.sql.hudi.catalog.HoodieCatalog",
    )
    spark.conf.set(
        "spark.sql.extensions", "org.apache.spark.sql.hudi.HoodieSparkSessionExtension"
    )
    spark.conf.set("spark.sql.hive.convertMetastoreParquet", "false")
    return spark


def get_hudi_options(
    table_name: str,
    record_key: str,
    partition_path: str,
    precombine_filed: str,
    hive_style_partitioning: str = "true",
    hive_sync_mode: str = "hms",
    upsert_shuffle_parallelism: int = 200,
    insert_shuffle_parallelism: int = 200,
    index_type: str = "GLOBAL_SHUFFLE",
) -> dict:
    """
    hoodie.table.name: This option specifies the name of the table in the target storage system (e.g. Hive).
    hoodie.datasource.write.recordkey.field: This option specifies the field in the source data that is used
                                             as the primary key for the records. This value is used to uniquely
                                             identify records and perform upsert operations.
    hoodie.datasource.write.partitionpath.field: This option specifies the field in the source data that is
                                                 used to partition the data in the target storage system.
                                                 This allows for efficient querying and retrieval of data.
    hoodie.datasource.write.table.name: This option specifies the name of the target table in the storage system.
    hoodie.datasource.write.operation: This option specifies the type of operation that is being performed on
                                       the records. The value 'upsert' indicates that the records will be updated
                                       if they already exist in the target table, or inserted if they do not.
    hoodie.datasource.write.precombine.field: This option specifies the field in the source data that is used
                                              to group records before they are written to the target table.
    hoodie.datasource.hive_style_partitioning: This option set to "true" indicates that the data will be
                                               partitioned in the target directory.
    hoodie.datasource.hive_sync.mode: This option determines how Hudi synchronizes the data with the target
                                      storage system (e.g. Hive). The value "hms" stands for Hive Metastore
                                      Service. When it is set to "hms" it will update the metadata in the Hive
                                      Metastore service with the new table and partition locations, this allows
                                      Hive to see the new data and it can be queried using HiveQL.
    hoodie.upsert.shuffle.parallelism: This option determines the parallelism level to use when performing shuffle
                                       operations during upserts. The value n indicates that the shuffle will be
                                       done with n parallel tasks.
    hoodie.insert.shuffle.parallelism: This option determines the parallelism level to use when performing shuffle
                                       operations during inserts. The value n indicates that the shuffle will be
                                       done with n parallel tasks.
    hoodie.index.type: This option determines the type of indexing to use for the data. The value "GLOBAL_SHUFFLE"
                       indicates that the indexing will be done using the global shuffle method, which is the
                       default indexing mechanism in Hudi and allows for fast queries on large datasets.
    hoodie.parquet.compression.codec: This option determines the compression codec to use for the data stored
                                      in parquet format. The value "snappy" indicates that the data will be
                                      compressed using the Snappy codec, which is a fast and efficient compression
                                      algorithm.
    """
    return {
        "hoodie.table.name": table_name,  # this can be the Glue Table
        "hoodie.datasource.write.recordkey.field": record_key,
        "hoodie.datasource.write.partitionpath.field": partition_path,
        "hoodie.datasource.write.table.name": table_name,
        "hoodie.datasource.write.operation": "upsert",
        "hoodie.datasource.write.precombine.field": precombine_filed,
        "hoodie.datasource.hive_style_partitioning": hive_style_partitioning,
        "hoodie.datasource.hive_sync.mode": hive_sync_mode,
        "hoodie.upsert.shuffle.parallelism": upsert_shuffle_parallelism,
        "hoodie.insert.shuffle.parallelism": insert_shuffle_parallelism,
        "hoodie.index.type": index_type,
        "hoodie.parquet.compression.codec": "snappy",
    }
