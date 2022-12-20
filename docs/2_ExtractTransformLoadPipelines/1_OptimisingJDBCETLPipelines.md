# 3.1 Optimizing JDBC ETL Pipelines

There are a variety of techniques to optimize for ingestion in PySpark, including creating a suitable SQL query with
high watermarks or pushdown predicates, designing parallel readings, and creating a suitable partitioning scheme for the
data being ingested. Here are a few of the main issues our platform addresses.

## Using High Watermarks

> Define an optimized SQL query that uses a high watermark to consume data from a read-only relational database.

```sql
SELECT 
  * 
FROM 
  table 
WHERE 
  id > (
    SELECT 
      MAX(id) 
    FROM 
      processed_records
  )
```

The high watermark, which represents the highest value of the id column that has been processed in previous iterations
of the query, is kept in this query in the processed records table. Only new rows that haven't been processed before
will be returned by the query because the WHERE clause filters out any rows with an id value that is less than or equal
to the high watermark.

## Using Pushdown Queries

Create a pushdown query with a high watermark value to only retrieve the most recent data for a read-only database.
Here is an illustration of a better SQL query that pulls only the most recent information from a read-only relational
database using a pushdown query and a high watermark:

```sql
WHERE <hwm_col_name> > <lwm_value> and <hwm_col_name> <= <hwm_value>

(SELECT * FROM <db/table> <sql_where_condition>) <table>_alias
```

In this query, any rows that have already been processed in prior iterations of the query are filtered away by the inner
SELECT statement, which makes advantage of the high watermark. The outer SELECT query then uses the timestamp value of
the rows to filter out any that are not the most recent ones.
With this method, the filtering can be done by the database engine using a pushdown query, which can enhance the query's
efficiency by lowering the volume of information that needs to be communicated from the database server to the client.

## Constructing Queries in Python & PySpark

Convert parameters into a SQL select statement with a pushdown predicate and a high watermark value using a Python
script. Make the predicate a pushdown predicate; this will vary depending on the predicate and table in question, thus
this is merely an illustration.

```python
import sys
import sqlparse

table_name = sys.argv[1]
predicate = sys.argv[2]
high_watermark = sys.argv[3]

pushdown_predicate = f"WHERE {predicate} AND id > {high_watermark}"
sql_query = f"SELECT * FROM {table_name} {pushdown_predicate}"

formatted_sql_query = sqlparse.format(sql_query, reindent=True)
```

The result is a sql query that would look like this:

```sql
SELECT * FROM my_table WHERE name = 'DirkSCGM' AND id > 1000
```

## High/Low Watermarks vs Upper/Lower Bounds

The upper bound and lower bound in a PySpark JDBC query are not necessarily the same as the hwm value and lwm value.

The upper bound and lower bound in a PySpark JDBC query refer to the maximum and minimum values of the specified field
that will be used in the WHERE clause of the query. This can be used to limit the amount of data that is queried from
the database, which can improve the performance of the query.

On the other hand, the hwm value and lwm value refer to the maximum and minimum values of a field in a PySpark data
frame. These values can be calculated using the max() and min() functions. The hwm value and lwm value do not
necessarily have anything to do with the upper bound and lower bound in a PySpark JDBC query.

### In order to calculate the distribution of high watermark values as partitions for a Spark job extracting data from a relational database, you will need to follow these steps:

1. Determine the criteria for partitioning the data: You will need to decide on the columns or criteria that you want to
   use to partition the data. This could be based on a specific column in the table, such as a timestamp or an ID, or a
   combination of columns.
2. Determine the high watermark values: The high watermark values are the maximum values of the chosen partitioning
   criteria that have been processed in the previous runs of the job. You will need to determine these values in order
   to ensure that the current run of the job is processing data that has not been processed before.
3. Calculate the number of partitions: Based on the high watermark values and the size of the data that you want to
   process, you will need to calculate the number of partitions that are required. This can be done by dividing the
   total size of the data by the desired size of each partition.
4. Assign the high watermark values to the partitions: Once you have determined the number of partitions, you will need
   to assign the high watermark values to the partitions. This can be done by dividing the range of values for the
   partitioning criteria by the number of partitions, and then assigning the high watermark values to the appropriate
   partitions based on the resulting range.
5. Extract the data using the partitions: Finally, you can use the calculated partitions and high watermark values to
   extract the data from the database using Spark. This can be done using the partitionBy function in the Spark
   DataFrame API, which allows you to specify the partitioning criteria and the high watermark values for each
   partition.
