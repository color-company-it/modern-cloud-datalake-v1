# Extract

## AWS Glue

The Spark script is a Glue Job using PySpark that is used to extract data from a JDBC source and save it to a DynamoDB
table using non-parallel methods. The script supports full extracts and partial extracts, and can be used to continue
with the extract on the next run, or reingest or rerun based on the success of the pipeline. The script supports the
following JDBC engines: postgres and mysql.

The script starts by importing necessary modules such as GlueContext, transforms, SparkContext, and DataFrame from the
awsglue package and functions and other required modules from the codebase package.

The script defines a main() function that starts by fetching the tracking table item using the get_tracking_table_item
function from the codebase.aws.ddb package. Then it calls the determine_extract_plan function from the
codebase.etl.extract package to determine the extract plan, passing it necessary parameters like provided_hwm_value,
provided_lwm_value, extract_type and the tracking_table.

The script then updates the tracking table with new or existing data using the update_extract_tracking_table function
from the codebase.aws.ddb package. If the row_count is -1 it means the pipeline is running OR it failed during the last
run.

It then creates a JDBC url using the get_jdbc_url function from the codebase.etl.extract package, and a SQL where
condition using the get_sql_where_condition function from the same package. It also converts the database namespaces
using the convert_db_namespaces function and gets the pushdown query using the get_pushdown_query function.

The script then creates the JDBC parameters, that includes url, properties, table, and assigns it to _jdbc_params. The
properties includes the user, password, driver, encrypt, trustServerCertificate, and applicationIntent.

The script then creates the source schema using the create_db_table_schema function from the codebase.etl.extract
package and assigns it to source_schema.

The script then creates a Glue DynamicFrame using the glueContext.create_dynamic_frame.from_options method and passing
it the JDBC parameters and the source schema.

The script then performs a repartition operation on the DynamicFrame using the repartition_dataframe parameter passed to
it, and uses the num_partitions parameter to determine the number of partitions to be used.

### Glue Job in Detail:

The `main()` function in this Spark JDBC extract code is responsible for extracting data from a JDBC source and saving
it to a DynamoDB table. The extract can be either a full extract or a partial extract, and can be resumed on the next
run or rerun based on the success of the pipeline.

The function first retrieves the tracking table item from DynamoDB, and then determines the extract plan based on the
provided extract type, high and low watermark values, and the tracking table. The tracking table is then updated with
new or existing data, with a default value of -1 for the number of rows extracted, indicating that the pipeline is
either running or failed during the last run.

The tracking table also has the `extract_successful` field that is either `Y` or `N` and is set to `N` either while the
pipeline is running, or the last attempt has failed. This means the next run will accommodate for the previous fail, for
example, a PE run would try to extract the previous high watermark values and not increment until it has succeeded.
If the `extract_successful` field is `Y` it means the last run was successful.

The JDBC URL, SQL WHERE condition, extract table namespace, and pushdown query are then obtained using helper functions.
The JDBC parameters, including the URL, user credentials, and driver, are set in a dictionary.

The source schema is created by inferring the data types of the columns in the extract table, and the data is then read
from the JDBC source using the `read.jdbc()` method of the DataFrameReader class, with the JDBC parameters and schema
passed as arguments. The number of partitions is calculated based on the sample data, and the data is repartitioned
using the `repartition()` method of the DataFrame class.

Finally, the data is written to DynamoDB using `the write.dynamodb()` method of the DataFrameWriter class, with the
target table and mode specified as arguments. The number of rows extracted is then updated in the tracking table,
along with a flag indicating that the extract was successful.

| Argument              | Type | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
|-----------------------|------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| extract_table         | str  | The name of the table to extract. This can be "schema_name.table_name" or just "table_name"                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| db_engine             | str  | The database engine. Must be either 'mysql' or 'postgres'.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| db_host               | str  | The hostname of the database server provided by the AWS Secret.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| db_port               | int  | The port number of the database server.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| db_name               | str  | The name of the database .                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| db_user               | str  | The username to use for connecting to the database provided by the AWS Secret.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| db_password           | str  | The password to use for connecting to the database provided by the AWS Secret.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |    
| hwm_col_name          | str  | The name of the high watermark column.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |  
| hwm_column_type       | str  | The data type of the high watermark column. Must be either 'int' or 'timestamp'.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | 
| extract_type          | str  | The type of extract. Must be either 'FE' for full extract or 'PE' for partial extract.                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| tracking_table_name   | str  | The name of the tracking table to use for storing the high and low watermark values.                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |      
| reingest              | bool | Flag indicating whether to reingest data. If True, the extract will read data from the beginning of the table. If False, the extract will read data from the last high watermark value.                                                                                                                                                                                                                                                                                                                                                                            | 
| hwm_value             | Any  | The high watermark value to use for the extract. If extract_type is 'PE', this value will be ignored in favor of the value in the tracking table. If extract_type is 'FE', this value will be used to determine the end of the extract. If hwm_column_type is 'int', this must be an int. If hwm_column_type is 'timestamp', this must be a string in the format 'YYYY-MM-DD HH:MM:SS'.                                                                                                                                                                            |
| lwm_value             | Any  | The low watermark value to use for the extract. If extract_type is 'PE', this value will be ignored in favor of the value in the tracking table. If extract_type is 'FE', this value will be used to determine the start of the extract. If hwm_column_type is 'int', this must be an int. If hwm_column_type is 'timestamp', this must be a string in the format 'YYYY-MM-DD HH:                                                                                                                                                                                  |
| partition_column      | bool | The column to use for partitioning the data.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| db_secret             | str  | The AWS Secrets Manager secret name that returns `{ "db_user" : "", "db_password": "", "db_host": ""}` this is ideal as added security.                                                                                                                                                                                                                                                                                                                                                                                                                            |
| lower_bound           | str  | This specifies the minimum value for the column used to partition the data. This is used to determine the range of data that should be extracted from the JDBC source in each partition. This is not used during Partial Extracts.                                                                                                                                                                                                                                                                                                                                 |
| upper_bound           | str  | This specifies the maximum value for the column used to partition the data. This is used to determine the range of data that should be extracted from the JDBC source in each partition. This is not used during Partial Extracts.                                                                                                                                                                                                                                                                                                                                 |
| num_partitions        | int  | used to specify the number of partitions that the resulting DataFrame should be repartitioned into. This can be useful in cases where the data is skewed, or if the number of rows in the table is much larger than the target number of rows per partition.                                                                                                                                                                                                                                                                                                       |
| fetchsize             | int  | This determines the number of rows that will be fetched at a time when the JDBC driver retrieves data from the database. This can be useful for optimizing the performance of the extract by allowing the driver to fetch data in smaller chunks, which can reduce the amount of memory required to hold the results in memory. However, setting the fetchsize too low can also lead to decreased performance, as it will require more round trips to the database to fetch all the data.                                                                          |
| repartition_dataframe | bool | The repartition_dataframe argument is a boolean value indicating whether or not the DataFrame should be repartitioned. If this argument is set to True, the number of partitions in the DataFrame will be adjusted to match the value of the num_partitions argument. This can be useful for improving the performance of the extract process, particularly if the data is skewed or if the target data store has a limited number of connections. However, repartitioning can also introduce overhead, so it should be used with caution and only when necessary. |
| extract_s3_uri        | str  | The extract_s3_uri argument is the location in S3 where the extracted data will be saved. It is a string in the format `s3://<bucket_name>/<path_to_folder>`.                                                                                                                                                                                                                                                                                                                                                                                                      |
| extract_s3_partitions | str  | A comma separated list of fields in the table being extracted. This specifies the number of partitions to use when writing the extracted data to S3. This can be useful for optimizing the performance of the extract process, as it allows the data to be distributed across multiple workers and written in parallel. It is generally recommended to set the number of partitions to a value that is large enough to fully utilize the available resources, but small enough to avoid overwhelming the S3 infrastructure.                                        |

## DynamoDb Extract Table

The DynamoDb table can be used to store the High Water Mark (HWM) and Low Water Mark (LWM) values for each extract table
that is being processed. These values can be used to determine the range of rows to extract from the JDBC source, for
example by using the `determine_extract_plan` method in the codebase.etl.extract module. The HWM and LWM values can also
be used to check whether a previous extract job has been successful and whether a full or partial extract needs to be
done. Additionally, the DynamoDb table can be used to store metadata about the extract job, such as the number of rows
extracted and whether the extract was successful, and can be used to update the status of the extract job using the
`update_extract_tracking_table` method in the codebase.aws.ddb module.

## S3 Extract Destination

The glue job writes data to S3 by using the `DataFrame.write` method with the `.parquet()` format.

In this example, the extracted_dataframe is created from the jdbc source, converted to a DataFrame, and then written to
a specific location in S3 in parquet format. The mode is set to overwrite which means that if the files are already
present, they will be overwritten with the new files. The _extract_s3_uri is the destination S3 bucket and the
`add_url_safe_current_time()` function is used to append a timestamp to the filename to make it unique.

---
<small> 
Please note that the above code and associated documentation are provided as a reference and are not guaranteed to be
error-free. This solution is a work in progress and may be subject to change. It is the responsibility of the user to
thoroughly test and verify the correctness of the code before using it in production environments. 
</small>