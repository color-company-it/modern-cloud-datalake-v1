# User Set Up

## Setting Up a JDBC Source

### Extract

To use the configuration .yml file to run the extract pipeline, a user would first need to ensure that they have the
necessary AWS services set up, such as Glue and Step Functions. The user would also need to have the appropriate
permissions and access to the resources defined in the .yml file, such as the JDBC source and the DynamoDB tracking
table.

Once the necessary prerequisites are in place, the user can then use the .yml file to define the extract pipeline's
settings, such as the job type, script name, and arguments. The user can also specify the default arguments for the
pipeline, such as the number of partitions and the fetchsize, as well as the database engine, secret, port, and name.

The user can then define the tables to be extracted in the "tables" section of the .yml file, specifying the partition
column, lower and upper bounds, and other relevant settings for each table. The user can also specify whether the
dataframe should be repartitioned and define the extract_s3_partitions.

Once the .yml file is set up, the user can then use it to invoke the extract pipeline using the Step Function's "Extract
Config Manager" state, passing in the necessary variables such as the --test argument and the default_arguments set in
the .yml file.

The Step Function will then use the Glue service to run the extract job using the script name and arguments defined in
the .yml file and extract the data from the specified tables in the JDBC source, saving it to the specified S3 location,
and updating the DynamoDB tracking table with the relevant information.

Here is an example of a configuration file for an enterprise data source:

```yaml
source_name: "enterprise_data_source"
source_owners:
  - data_owner1@enterprise.com
  - data_owner2@enterprise.com
extract:
  job_type: glue # emr, ecs
  script_name: jdbc_extract_job.py
  arguments:
    --test: 1
  default_arguments:
    num_partitions: "4"
    fetchsize: "1000"
    extract_type: "FE"
    worker_no: "2"
    worker_type: "Standard"
  db_engine: "postgres" # mysql
  db_secret: "postgres/enterprise_db"
  db_port: "5432"
  db_name: "enterprise_data"
  tables:
    public.employees:
      partition_column: "employee_id"
      lower_bound: "1"
      upper_bound: "10000"
      extract_type: "PE"
      hwm_col_name: "employee_id"
      hwm_column_type: "IntegerType"
      lwm_value: "1"
      hwm_value: "10000"
      repartition_dataframe: "true"
      extract_s3_partitions: "department"
    public.sales:
      partition_column: "sale_id"
      lower_bound: "1"
      upper_bound: "100000"
      hwm_col_name: "sale_id"
      hwm_column_type: "IntegerType"
      lwm_value: "1"
      hwm_value: "100000"
      repartition_dataframe: "true"
      extract_s3_partitions: "region"
    public.customers:
      partition_column: "customer_id"
      lower_bound: "1"
      upper_bound: "100000"
      hwm_col_name: "customer_id"
      hwm_column_type: "IntegerType"
      lwm_value: "1"
      hwm_value: "100000"
      repartition_dataframe: "true"
      extract_s3_partitions: "customer_segment,account_type"
```

In this example, the source name is "enterprise_data_source" and the source owners are "data_owner1@enterprise.com"
and "data_owner2@enterprise.com". These emails are automatically subscribe to an email SNS topic.
The extract process uses a Glue job, with a script named "jdbc_extract_job.py" and
some optional arguments, such as "--test: 1". The extract process also has some default arguments, such as "
num_partitions: 4" and "fetchsize: 1000". The extract job will connect to a postgres database.

The configuration file is used to specify the details of the extract pipeline for a given enterprise data source. The
key-value pairs in the file define the parameters that are passed to the extract job when it is run. Below is a
description and use case for each key in the configuration file:

- `source_name`: This key is used to specify the name of the data source. It is used to identify the source of the data
  in the extract pipeline and in any downstream processing or analysis.
- `source_owners`: This key is used to specify the email addresses of the owners or stewards of the data source. It is
  used to ensure that the correct people are notified of any issues or questions that may arise during the extract
  pipeline.
- `extract`: This key is used to specify the details of the extract pipeline for the data source.
    - `job_type`: This key is used to specify the type of job that will be used to extract the data. It can be set to "
      glue", "emr", or "ecs".
    - `script_name`: This key is used to specify the script that will be run to extract the data. It should be the name
      of the script that contains the extract job.
    - `arguments`: This key is used to specify any additional arguments that should be passed to the extract job when it
      is run. These arguments can be used to customize the behavior of the extract job or to pass in any required
      parameters.
    - `default_arguments` : This key is used to specify the default arguments that should be passed to the extract job
      when it is run. The default arguments are used if the arguments are not defined in the tables sections
    - `db_engine`: This key is used to specify the type of database engine that the data source uses. It can be set to "
      postgres" or "mysql".
    - `db_secret`: This key is used to specify the name of the AWS Secrets Manager secret that contains the credentials
      for the data source.
    - `db_port`: This key is used to specify the port number that should be used to connect to the data source.
    - `db_name`: This key is used to specify the name of the database that contains the data to be extracted.
    - `tables`: This key is used to specify the details of the tables that will be extracted from the data source. Each
      table is specified as a key-value pair, with the key being the name of the table and the value being a dictionary
      of parameters that are passed to the extract job when it runs.