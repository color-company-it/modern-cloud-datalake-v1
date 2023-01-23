# Configuration

The `generate_extract_config` function takes in a config object and processes it to create a list of event payloads for
the extract pipelines. The function first extracts the extract-related information from the config object and sets up
some defaults. It then iterates over the tables in the extract section of the config, creating a new configuration for
each table. The new configuration includes information about the source, the specific extract table, the job type and
source type, the database engine and secret, the port, the name of the database, and various extract-related parameters
such as the partition column, the lower and upper bounds, the extract type, the high watermark column name and type, the
low and high watermark values, the number of partitions, the fetch size, the worker number and type, and whether to
repartition the dataframe or extract S3 partitions. Finally, the function appends each new configuration to a list of
event arguments and returns the list.

## Default Configs

The `default` closure method is defined within the `generate_extract_config` function and is used to handle default
arguments within the configuration. It takes in one parameter, item, which is the name of an extract-related parameter.

The method first checks if the table_config object, which is defined in the outer scope and holds the specific
configuration for the current table being processed, contains a value for the item parameter. If it does, the method
returns the value from the `table_config` object. If not, it returns the default value for that parameter from the
defaults object, which is also defined in the outer scope and holds the default arguments for the entire extract
configuration.

This allows for the generate_extract_config function to handle both specific and default arguments for each table in the
extract configuration. For example, if a specific table has a value for num_partitions in its configuration, that value
will be used, otherwise the default value from defaults will be used.

```python
config = {
    "source_name": "my_source",
    "extract": {
        "job_type": "incremental",
        "source_type": "rdbms",
        "db_engine": "postgres",
        "db_secret": "my_secret",
        "db_port": "5432",
        "db_name": "mydb",
        "default_arguments": {
            "partition_column": "id",
            "lower_bound": "1",
            "upper_bound": "10000",
            "extract_type": "PE",
            "hwm_col_name": "created_at",
            "hwm_column_type": "TimestampType",
            "lwm_value": "2022-01-01",
            "hwm_value": "2022-02-01",
            "repartition_dataframe": "True",
            "extract_s3_partitions": "True",
            "num_partitions": "10",
            "fetchsize": "1000",
            "worker_no": "4",
            "worker_type": "m4.large"
        },
        "tables": {
            "mydb.schema.table1": {
                "hwm_col_name": "updated_at",
                "num_partitions": "8"
            },
            "mydb.schema.table2": {
                "extract_type": "FE",
                "repartition_dataframe": "False"
            },
            "mydb.schema.table3": {}
        }
    }
}

event_arguments = generate_extract_config(config)
print(event_arguments)

```

The solution works with Yaml within the configuration layer, and the extract process first begins with
an AWS Lambda function that makes use of the above method.

## Lambda Config Managers

### extract_config_manager.py

The `lambda_handler` function is an AWS Lambda function that takes in an event payload and a context. The event payload
contains two key-value pairs: `source_name` (a string representing the name of the config file stored in an S3 bucket)
and `extract_tables` (a list of tables that are specified in the config file and are to be run in this extract Glue job)
.
The function is responsible for triggering an extract job by sending a payload to an AWS Step Function.

The function first logs the event payload and then uses the `source_name` provided in the event payload to retrieve the
config file from an S3 bucket. The function then uses the generate_extract_config method to set up the config file into
a flat structure for the event payload for the extract pipelines.

The function then creates two lists: _`tables_to_extract` and _`tables_not_to_extract`. The _`tables_to_extract` list is
populated with the extract tables that are specified in the _`extract_tables` list provided in the event payload, and
additional data such as extract_s3_uri and tracking_table_name is added to each extract item in the list. The
`_tables_not_to_extract` list is populated with the extract tables that are not specified in the _`extract_tables` list
provided in the event payload.

The lambda function returns a dictionary with two keys: status_code and tables_to_extract. The status_code key has a
value of 200, indicating that the function has executed successfully. The tables_to_extract key contains a list of
dictionaries, where each dictionary represents a table to be extracted and includes additional data needed for the
extract job, such as extract_s3_uri, tracking_table_name, etc. The tables contained in the list are specified in the
extract_tables key of the event payload passed to the function. The function also logs the extract tables that will not
be extracted in this run.

#### Return Object

This is a JSON object that the AWS Lambda function returns when it's invoked. It has two key-value pairs:

- status_code: This key has a value of 200 which indicates a successful execution of the Lambda function.
- tables_to_extract: This key has a value of a list of dictionaries, where each dictionary contains the information
  needed to execute an extract job on a specific table. Each dictionary has the following keys:
    - source_name: The name of the config file stored in an S3 bucket. The config file is in YAML format and has
      information about the extract Glue job to be run.
    - extract_table: The table name that is specified in the config file and is to be run in this extract Glue job.
    - job_type: The type of job to run. In this case, it is "glue"
    - source_type: The type of the source. In this case, it is "jdbc"
    - db_engine: The JDBC engine used for the extract job. In this case, it is "postgres"
    - db_secret: The name of the secret that holds the JDBC connection details.
    - db_port: The port used to connect to the JDBC source.
    - db_name: The name of the database.
    - partition_column: The column to partition on.
    - lower_bound: The lower bound of the partition column.
    - upper_bound: The upper bound of the partition column.
    - extract_type: The type of extract, whether it is full or partial.
    - hwm_col_name: The high watermark column.
    - hwm_column_type: The data type of the high watermark column
    - lwm_value: The low watermark value.
    - hwm_value: The high watermark value.
    - repartition_dataframe: Whether to repartition the dataframe
    - extract_s3_partitions: The column to partition the data on when writing to S3
    - num_partitions: The number of partitions
    - fetchsize: The fetch size
    - extract_s3_uri: The S3 URI where the extracted data will be stored.
    - tracking_table_name: The name of the DynamoDB table used for tracking the extract job progress.

This object is returned by the lambda function, which is triggered by an event object, containing the source_name and
extract_tables keys. The function retrieves the configuration file from an S3 bucket, and generates a list of tables to
extract and their corresponding data that is necessary to execute the extract job. This list is returned by the function
as the value of the tables_to_extract key, and it will be sent as a payload to the AWS Step Function, which will trigger
the extract job based on the job_type specified in the configuration file.

Finally, this payload is submitted to the Extract Job Run.

---
<small> 
Please note that the above code and associated documentation are provided as a reference and are not guaranteed to be
error-free. This solution is a work in progress and may be subject to change. It is the responsibility of the user to
thoroughly test and verify the correctness of the code before using it in production environments. 
</small>