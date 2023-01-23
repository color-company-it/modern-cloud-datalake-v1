# Codebase

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

## ETL

This code defines a number of variables and functions used in ETL (extract, transform, load) operations using PySpark.

The `get_spark_logger` function sets up a logger with a specific format and log level. The level parameter defaults to
logging.INFO if not provided. The function returns the logger object.

`JDBC_ENGINES` is a list of supported JDBC engines (Postgres and MySQL in this case). `JDBC_DRIVERS` is a dictionary
that maps the JDBC engine names to their corresponding driver classes.

`SCHEMA_QUERY_MAPPING` is a dictionary that maps JDBC engine names to their corresponding SQL query for fetching the
schema of a table.

`MIN_VALUES` is a dictionary that maps Spark SQL data types to their minimum representable values.

`DATA_TYPE_MAPPING` is a dictionary that maps JDBC engine names to their corresponding data type mappings. Each engine
mapping is a dictionary that maps SQL data types to their corresponding Spark SQL data types.

### Extract

This code defines a number of functions used for extracting data from a database using PySpark.

#### convert_db_namespaces

The convert_db_namespaces function converts the namespaces of a specified extract table based on the database engine. It
takes in the name of the extract table, the name of the database, and the database engine as input. It returns the
converted namespaces in the form of a string.

```python
# convert_db_namespaces example
extract_table = "schema.table"
db_name = "mydb"
db_engine = "postgres"

converted_namespaces = convert_db_namespaces(extract_table, db_name, db_engine)
# converted_namespaces = "mydb"."schema"."table"
```

#### get_sql_where_condition

The get_sql_where_condition function generates a SQL WHERE clause based on the extract type, lwm value, hwm column name,
hwm value, hwm column type, and reingest flag. If the extract type is "FE", the function returns an empty string. If the
extract type is "PE", the function generates a WHERE clause that filters data based on the lwm value and hwm value. If
the reingest flag is set to true, the function generates a WHERE clause that filters data based on the hwm column type,
and the minimum value of that type.

```python
# get_sql_where_condition example
extract_type = "PE"
lwm_value = "2022-01-01"
hwm_col_name = "created_at"
hwm_value = "2022-02-01"
hwm_column_type = "TimestampType"
reingest = False

sql_where_condition = get_sql_where_condition(extract_type, lwm_value, hwm_col_name, hwm_value, hwm_column_type,
                                              reingest)
# sql_where_condition = "WHERE created_at > '2022-01-01' and created_at <= '2022-02-01'"
```

#### get_pushdown_query

The get_pushdown_query function generates a query that can be pushed down to the database to extract data. It takes in
the extract table name, the SQL WHERE clause and the database name as input and returns a string representing the
pushdown query.

```python
# get_pushdown_query example
extract_table = "mydb.schema.table"
sql_where_condition = "WHERE created_at > '2022-01-01'"
db_name = "mydb"

pushdown_query = get_pushdown_query(extract_table, sql_where_condition, db_name)
# pushdown_query = "(SELECT * FROM mydb.schema.table WHERE created_at > '2022-01-01') mydb_alias"
```

#### get_jdbc_url

The get_jdbc_url function generates a JDBC URL for connecting to a database. It takes in the host name, port number,
database name and database engine as input and returns a string representing the JDBC URL.

```python
# get_jdbc_url example
db_host = "localhost"
db_port = "5432"
db_name = "mydb"
db_engine = "postgres"

jdbc_url = get_jdbc_url(db_host, db_port, db_name, db_engine)
# jdbc_url = "jdbc:postgresql://localhost:5432/mydb"
```

#### get_jdbc_properties

The get_jdbc_properties function generates a dictionary of properties for connecting to a database. It takes in the
database username and password as input and returns a dictionary of properties.

```python
# get_jdbc_properties example
db_username = "myuser"
db_password = "mypassword"

jdbc_properties = get_jdbc_properties(db_username, db_password)
# jdbc_properties = {"user": "myuser", "password": "mypassword"}
```

#### get_db_connection

The get_db_connection function establishes a connection to a database. It takes in the JDBC URL and properties as input
and returns a connection object.

```python
# get_db_connection example
jdbc_url = "jdbc:postgresql://localhost:5432/mydb"
jdbc_properties = {"user": "myuser", "password": "mypassword"}

conn = get_db_connection(jdbc_url, jdbc_properties)
# conn = <psycopg2.extensions.connection object at 0x7f2a8c1b1f10>
```

#### get_table_schema

The get_table_schema function fetches the schema of a table in a database. It takes in the table name, database
connection and database engine as input and returns a list of tuples representing the schema of the table.

```python
# get_table_schema example
table_name = "schema.table"
conn = < db_conn_obj >
db_engine = "postgres"

table_schema = get_table_schema(table_name, conn, db_engine)
```

#### get_dataframe

The get_dataframe function extracts data from a database table and returns it as a DataFrame. It takes in the pushdown
query, JDBC URL, JDBC properties and the database engine as input and returns a DataFrame representing the extracted
data.

```python
from pyspark.sql import SparkSession

# Create a SparkSession
spark = SparkSession.builder.appName("ETL").getOrCreate()

# Set up JDBC URL and properties
db_host = "localhost"
db_port = "5432"
db_name = "mydb"
db_engine = "postgres"
jdbc_url = get_jdbc_url(db_host, db_port, db_name, db_engine)
db_username = "myuser"
db_password = "mypassword"
jdbc_properties = get_jdbc_properties(db_username, db_password)

# Set up pushdown query and extract type
extract_table = "mydb.schema.table"
extract_type = "PE"
lwm_value = "2022-01-01"
hwm_col_name = "created_at"
hwm_value = "2022-02-01"
hwm_column_type = "TimestampType"
reingest = False

sql_where_condition = get_sql_where_condition(extract_type, lwm_value, hwm_col_name, hwm_value, hwm_column_type,
                                              reingest)
pushdown_query = get_pushdown_query(extract_table, sql_where_condition, db_name)

# Get the DataFrame
df = get_dataframe(pushdown_query, jdbc_url, jdbc_properties, db_engine)

# Perform some operations on the DataFrame
df.show()
df.printSchema()
df.count()
```

## What is Full Extract (FE) and Partial Extract

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