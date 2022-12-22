# 1.2 JDBC Extract Pipeline

The Data Lake is split up into three major parts, the Extract Pipeline, Transform Pipeline and Load Pipeline.
Each of which have a vanilla PySpark script for EMR and any other solution. There is an equal Glue version of the same
script, however it does not make explicit use of the Glue Context.

## jdbc_extract_job.py

The `main()` function in this Spark JDBC extract code is responsible for extracting data from a JDBC source and saving
it
to a DynamoDB table. The extract can be either a full extract or a partial extract, and can be resumed on the next run
or rerun based on the success of the pipeline.

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
target
table and mode specified as arguments. The number of rows extracted is then updated in the tracking table, along with a
flag indicating that the extract was successful.

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

### Step-by-step guide for spinning up a Docker image with the above code and pipeline:

An example of how this can be used in the docker image is as follows. You can run a pipeline locally:

1. Build the base_pyspark Docker image using the command:

```shell
docker build -t base_pyspark -f scripts/docker/base_pyspark/Dockerfile .
```

2. Build the etl_jdbc Docker image using the command:

```shell
docker build -t etl_jdbc -f scripts/docker/etl_jdbc/Dockerfile .
```

3. Run the etl_jdbc Docker image with the necessary environment variables set. More on this can be found below.

#### The above solution in AWS Glue

To use the above code in an AWS Glue job, you will need to specify the input arguments as Glue job parameters. You can
do this by setting up a Glue job and specifying the parameters in the job's configuration.

You can then access the input arguments in your PySpark script using the `getResolvedOptions` class. This class allows
you
to retrieve the job parameters as a dictionary.

Here is an example of how you might retrieve the input arguments in your PySpark script:

```python
import sys
from awsglue.utils import getResolvedOptions

# Retrieve the job parameters as a dictionary
args = getResolvedOptions(sys.argv,
                          ['EDL_TYPE', 'DB_ENGINE', 'DB_SECRET', 'DB_PORT',
                           'DB_NAME', 'PARTITION_COLUMN', 'LOWER_BOUND', 'UPPER_BOUND',
                           'NUM_PARTITIONS', 'FETCHSIZE', 'EXTRACT_TABLE', 'EXTRACT_TYPE',
                           'HWM_COL_NAME', 'HWM_COLUMN_TYPE', 'LWM_VALUE', 'HWM_VALUE',
                           'REPARTITION_DATAFRAME', 'EXTRACT_S3_PARTITIONS', 'EXTRACT_S3_URI',
                           'REINGEST', 'TRACKING_TABLE_NAME']
                          )
```

This is already set up in the infrastructure layer. Once you have extracted the job parameters, you can use them in your
PySpark script just like you would in any other Python script. You can then run your Glue job as usual, and the input
arguments will be passed to the script as expected.

## base_pyspark Docker Container

The docker container is based on the Amazon Linux 2 image, which is a lightweight and secure Linux operating system used
by AWS. It is intended to be used as a base image for creating PySpark applications.

The container installs and configures Java, AWS CLI, and PySpark, and includes Hadoop and Spark configuration files. It
also includes JDBC jar files, which are necessary for connecting to a JDBC data source from PySpark.

To use this docker container, you will first need to build it using the docker build command:

```shell
docker build -t base_pyspark -f scripts/docker/base_pyspark/Dockerfile .
```

Once the container is built, you can run it using the docker run command, specifying any necessary environment variables
and mounting any necessary volumes:

```shell
docker run \
  -v ~/.aws:/root/.aws \
  --rm=true \
  -e ENV_VAR_1=value1 \
  -e ENV_VAR_2=value2 \
  base_pyspark
```

## etl_jdbc Docker Container (This is the one you use to run the Extract Spark Pipeline)

To use the docker container for the code above, you will need to have Docker installed on your local machine. Once you
have Docker installed, follow the steps below:

1. Build the base_pyspark image by running the command: docker build -t base_pyspark -f
   scripts/docker/base_pyspark/Dockerfile .
2. Build the etl_jdbc image by running the command: docker build -t etl_jdbc -f scripts/docker/etl_jdbc/Dockerfile .
3. Run the etl_jdbc image with the required input arguments by using the command:

```shell
docker run \
  -v ~/.aws:/root/.aws \
  --rm=true \
  -e SCRIPT_NAME=jdbc_dev_extract_job.py \
  -e EDL_TYPE=extract \
  -e DB_ENGINE=postgres \
  -e DB_SECRET=business/accounts\
  -e DB_PORT=5432 \
  -e DB_NAME=fzmjfsta \
  -e PARTITION_COLUMN=AccountID \
  -e LOWER_BOUND=1 \
  -e UPPER_BOUND=1000 \
  -e NUM_PARTITIONS=4 \
  -e FETCHSIZE=1000 \
  -e EXTRACT_TABLE=public.accounts \
  -e EXTRACT_TYPE=PE \
  -e HWM_COL_NAME=AccountID \
  -e HWM_COLUMN_TYPE=IntegerType \
  -e LWM_VALUE=1 \
  -e HWM_VALUE=1000 \
  -e REPARTITION_DATAFRAME=True \
  -e EXTRACT_S3_PARTITIONS=AccountType \
  -e EXTRACT_S3_URI=dirkscgm-test/ \
  -e REINGEST=True \
  -e TRACKING_TABLE_NAME=s3://my-bucket/extract/accounts \
  etl_jdbc
```

The docker container will run the PySpark job specified in the `SCRIPT_NAME`, so essentially any spark script can be run
with their respective input arguments.

## Conclusion

In conclusion, the above code represents a Spark JDBC extract pipeline that can be used to extract data from a JDBC
source and save it to a DynamoDB table in a cloud environment. The pipeline is designed to follow the DRY principle and
adhere to best practices for unit testing and integration testing. The codebase module is available in AWS S3 as a .whl
file, .zip file, and a lambda layer .zip file. The pipeline can be run using the docker run command, or in AWS Glue
using the Glue GetResolvedOptions class. It is important to note that the solution only supports MySQL and Postgres, and
that the developers are working to improve the current solution before taking on other database engines.


---
<small> 
Please note that the above code and associated documentation are provided as a reference and are not guaranteed to be
error-free. This solution is a work in progress and may be subject to change. It is the responsibility of the user to
thoroughly test and verify the correctness of the code before using it in production environments. 
</small>
