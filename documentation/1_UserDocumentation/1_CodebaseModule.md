# 1.1 Codebase Module - For Python3

The Codebase module is a collection of functions and classes that are designed to be used across multiple projects in
the DataLake environment. The goal of the module is to reduce duplication of code and improve the maintainability and
reliability of the projects that use it.

> Please note that this solution only supports **MySQL** and **Postgres** databases, as they are widely available and
> open-source. The developers are working on refining the current solution before adding support for other database
> engines such as Microsoft SQL Server and Oracle.

The Codebase module is available in multiple formats to support different types of deployment scenarios. The `.whl` file
is a Python wheel file that can be used to install the module using pip or can be added to the AWS Glue
`--additional-python-modules` default argument. The `.zip` file is a compressed archive that
contains the source code of the module and can be used to install the module using pip or manually by extracting the
contents of the archive and running python setup.py install. The `lambda layer .zip` file is a compressed archive that
contains the compiled version of the module and can be used to create a Lambda layer in AWS.

To use the Codebase module in a project, it must be installed either using pip or by manually adding the source code to
the project. Once the module is installed, it can be imported and used like any other Python module.

The Codebase module includes unit tests and integration tests to ensure that it is working as intended. These tests
should be run before deploying the module to ensure that it is free of bugs and errors.

To use the Codebase module with AWS Glue, you can install the .whl file as follows:

1. In the AWS Glue console, navigate to the Dev Endpoints page and select the dev endpoint that you want to use.
2. In the Action dropdown menu, select "Edit".
3. On the Edit Dev Endpoint page, in the Python Library Paths section, click "Add Python Library".
4. In the "Add Python Library" dialog, select "Upload a Python library in .whl format".
5. Choose the .whl file that you downloaded in step 1, and then click "Add".
6. Click "Save" to save the changes to your dev endpoint.

The Codebase module will now be available to be imported and used in your Glue ETL scripts.

Note: If you are using the Codebase module in a Glue ETL job or development endpoint, you will need to add the module to
the Glue Python library path for each job or endpoint that uses it. The steps above need to be repeated for each job or
endpoint. This is managed in the infrastructure layer automatically.

## codebase.etl.get_num_partitions()

The get_num_partitions() method is used to calculate the number of repartitions for a PySpark JDBC extract process,
taking into account data skew. This is done to ensure that the data is distributed evenly across the available resources
and to minimize the overhead of data shuffling and partitioning.

To use the get_num_partitions() method, you need to pass in a DataFrame containing a sample of the data to extract, and
an optional rows_per_partition parameter, which specifies the target number of rows per partition. The method will then
calculate the number of rows in the DataFrame, determine the average number of rows per partition, calculate the skew
factor, and adjust the number of repartitions based on the skew factor. Finally, the method returns the number of
repartitions as an integer.

Here is an example of how to use the get_num_partitions() method:

```python
from codebase.etl import get_num_partitions

# Load a sample of the data into a DataFrame
data_frame = spark.read.format("jdbc").options(
    url=jdbc_url,
    driver=driver,
    dbtable=pushdown_query,
    user=db_user,
    password=db_password,
).load()

# Calculate the number of repartitions based on the target number of rows per partition
num_partitions = get_num_partitions(data_frame, rows_per_partition=1000)

# Repartition the DataFrame
data_frame = data_frame.repartition(num_partitions)
```

## codebase.etl.extract.convert_db_namespaces()

The convert_db_namespaces() method is used to convert the database namespaces in a specified extract table based on the
database engine.

Parameters:

- `extract_table` (str): A string representing the extract table whose namespaces are to be converted.
- `db_name` (str): A string representing the name of the database.
- `db_engine` (str): A string representing the database engine (e.g. "postgres", "mysql").

Returns:

- A string representing the converted database namespaces for the specified extract table.

Example:

```python
from codebase.etl.extract import convert_db_namespaces

convert_db_namespaces('schema_name.table_name', 'db_name', 'postgres')
>> '"db_name"."schema_name"."table_name"'
```

## codebase.etl.extract.get_sql_where_condition()

The get_sql_where_condition() method is used to generate a SQL WHERE clause for use in a SELECT statement. The method
takes in several arguments:

- `extract_type`: a string representing the type of extract being performed. This can be either 'FE' (full extract) or '
  PE' (partial extract).
- `lwm_value`: the low watermark value to use in the WHERE clause. This is the minimum value that the target column can
  have.
- `hwm_col_name`: the name of the high watermark column. This is the column that the WHERE clause will be based on.
- `hwm_value`: the high watermark value to use in the WHERE clause. This is the maximum value that the target column can
  have.
- `hwm_column_type`: the data type of the high watermark column. This is used to determine the minimum possible value
  for the column.
- `reingest`: a boolean value indicating whether the data is being reingested. If True, all original data may be
  overwritten.

The method returns a string representing the WHERE clause to be used in the SELECT statement. If the extract_type is '
FE', an empty string is returned. If the extract_type is 'PE', the WHERE clause is based on the `lwm_value` and
`hwm_value` parameters.

If reingest is True, the WHERE clause will include only the `hwm_col_name` column and will retrieve all rows
where the value of that column is greater than the minimum possible value for the column's data type. If `hwm_value` is
'-1', the WHERE clause will retrieve all rows where the value of the `hwm_col_name` column is greater than `lwm_value`.

## codebase.etl.extract.get_pushdown_query()

The get_pushdown_query() method is used to generate a pushdown query for extracting data from a database table.

It takes three arguments:

- `extract_table`: a string representing the name of the table to extract data from.
- `sql_where_condition`: a string representing the WHERE clause to use in the SELECT statement.
- `db_name`: a string representing the name of the database.

- It returns a string representing the pushdown query. The pushdown query is a SELECT statement with the specified
  extract_table and sql_where_condition wrapped in parentheses and followed by an alias for the database.

Example usage:

```python
from codebase.etl.extract import get_pushdown_query

extract_table = "sales.orders"
sql_where_condition = "WHERE order_date > '2022-01-01'"
db_name = "marketing_db"

pushdown_query = get_pushdown_query(extract_table, sql_where_condition, db_name)
print(pushdown_query)
```

This will print `"(SELECT * FROM sales.orders WHERE order_date > '2022-01-01') marketing_db_alias"`.

### What is a pushdown query and why do we use it?

A pushdown query is a type of SELECT statement that is executed directly on the database server rather than in the
client application. This can be useful for extracting data from a database table when the data volume is large and the
client application has limited resources.

By executing the SELECT statement on the database server, the pushdown query can take advantage of the server's
resources and processing power to perform the query and return only the relevant data to the client application. This
can help to reduce the amount of data that needs to be transferred over the network and improve the overall performance
of the extract process.

Pushdown queries can also be useful for optimizing the execution of complex queries by allowing the database server to
perform more of the processing work. This can help to reduce the workload on the client application and improve the
overall efficiency of the extract process.

### Why do we use an alias?

The alias added to the query refers to the name given to the subquery within the main query. In this case, the subquery
is the SELECT statement with the WHERE clause, and the alias is a name that is assigned to the result of that subquery.
The alias allows the result of the subquery to be referred to in the rest of the query, such as in the FROM clause, as
if it were a table. This can make the query more readable and easier to understand. It can also be used to avoid naming
conflicts with other tables or queries in the same statement.

## codebase.etl.extract.get_jdbc_url()

The get_jdbc_url() method is used to generate a JDBC URL for a specific database. This URL can be used to connect to the
database using a JDBC driver.

The method takes the following parameters:

- `db_host` (str): The hostname of the database server.
- `db_port` (int): The port number of the database server.
- `db_name` (str): The name of the database.
- `db_engine` (str): The database engine (e.g. "postgres", "mysql").
  It returns a string representing the JDBC URL for the specified database.

The method first checks the value of db_engine. If it is "postgres", it generates a JDBC URL in the format jdbc:
`postgresql://{db_host}:{db_port}/{db_name}`.
If it is "mysql", it generates a JDBC URL in the format `jdbc:mysql://{db_host}:{db_port}/{db_name}`.

If the value of db_engine is neither of these, it raises an EnvironmentError indicating
that the engine is not supported. At the moment, the pipeline only supports MySQL and Postgres.

This method is useful when connecting to a database using a JDBC driver, as it allows you to easily generate the correct
URL for the desired database.

## codebase.etl.extract.get_column_data_types()

The get_column_data_types() method is used to retrieve the data types of the columns in a database table. It takes in
the following parameters:

- `engine` (str): The database engine. Currently, only postgres and mysql are supported.
- `host` (str): The hostname of the database server.
- `port` (int): The port number of the database server.
- `database` (str): The name of the database.
- `user` (str): The username to use for connecting to the database.
- `password` (str): The password to use for connecting to the database.
- `table_name` (str): The name of the table.
  It returns a dictionary mapping column names to data types as strings.

This method connects to the specified database using the psycopg2 or mysql.connector library (depending on the value of
engine), and executes a SELECT statement to retrieve the column names and data types from the information_schema.columns
table. It then iterates through the results of the query, creating a dictionary mapping column names to data types.

This method is useful for creating the schema for a PySpark DataFrame when extracting data from a database table. It
allows you to infer the data types of the columns in the table, which can be used to define the schema of the DataFrame.

### Why are we getting the data types from the JDBC source?

Using PySpark's built-in datatype inference solution can be unreliable, as it may not always accurately detect the
correct data types for all columns in a database table. This can lead to data loss or incorrect data being loaded into
the target system.

The get_column_data_types() method provides a more reliable solution by querying the database's information schema
directly to get the data types of the columns in a table. This ensures that the correct data types are used when
creating the schema for the table, which can help to prevent data loss or incorrect data being loaded.

However, this method does require more maintenance as it is necessary to periodically update the DATA_TYPE_MAPPING
dictionary to include any new data types that may be added to the database. Despite this additional maintenance, the
get_column_data_types() method is still a more reliable solution for ensuring accurate data types when working with a
database.

## codebase.etl.extract.create_db_table_schema()

The create_db_table_schema() method is used to create the schema for a database table by inferring the data types of the
columns. It does this by connecting to the database and querying the information_schema to get the column names and data
types. It then uses the difflib library to find the closest matching Spark data type for each column, based on the data
type mapping specified in the DATA_TYPE_MAPPING dictionary. If a close match is found, the column is added to the schema
with the matching Spark data type. If no close match is found, the column is added to the schema with a data type of
StringType. The resulting schema is returned as a StructType object.

It is important to note that this method only works for MySQL and Postgres databases, as these are the only databases
currently supported by the DATA_TYPE_MAPPING dictionary. If you are using a different database, you will need to modify
the DATA_TYPE_MAPPING dictionary to include data type mappings for that database, and update the
create_db_table_schema() method to use the correct information_schema table and column names.

This method is useful for creating an accurate schema for a database table, as PySpark's built-in data type inference
can sometimes be unreliable. However, it is important to keep in mind that this method relies on a manually-maintained
data type mapping dictionary, which may require regular updates to ensure that it remains accurate and up-to-date.

## codebase.etl.extract.determine_extract_plan()

The determine_extract_plan() method is used to determine the high and low watermark values to use for an extract
process. The method takes in three arguments:

- `provided_hwm_value` (Any): The high watermark value that has been provided.
- `provided_lwm_value` (Any): The low watermark value that has been provided.
- `extract_type` (str): The type of extract. Can be either 'FE' (full extract) or 'PE' (partial extract).
- `tracking_table` (Dict[str, Any]): A dictionary containing the tracking table for the extract. The keys 'hwm_value'
  and 'lwm_value' should contain the high and low watermark values, respectively.
  The method returns a tuple containing the high and low watermark values to use for the extract.

If the extract type is 'FE', the provided high and low watermark values are returned. If the extract type is 'PE', the
tracking table is checked for the high and low watermark values. If the tracking table is empty, the provided high and
low watermark values are returned. If the extract type is not 'FE' or 'PE', a ValueError is raised.

This method is useful for ensuring that the correct high and low watermark values are used for an extract process,
whether it is a full extract or a partial extract. It is important to properly track the high and low watermark values
in order to avoid extracting duplicate data or missing data during a partial extract.

### What is Full Extract (FE) and Partial Extract

FE stands for Full Extract, which means that all data in the specified table will be extracted. This is typically used
for the initial extract or when data needs to be completely refreshed.

PE stands for Partial Extract, which means that only data that has been added or modified since the last extract will be
extracted. This is typically used for incremental extracts where only new or updated data needs to be processed. The
high and low watermark values are used to determine the range of data to be extracted. The high watermark value is the
highest value of a particular column in the data that has been previously extracted, and the low watermark value is the
lowest value of that same column in the data that has not yet been extracted. The extract process will retrieve all data
with a value of the specified column greater than the high watermark value and less than or equal to the low watermark
value.

---
<small> 
Please note that the above code and associated documentation are provided as a reference and are not guaranteed to be
error-free. This solution is a work in progress and may be subject to change. It is the responsibility of the user to
thoroughly test and verify the correctness of the code before using it in production environments. 
</small>