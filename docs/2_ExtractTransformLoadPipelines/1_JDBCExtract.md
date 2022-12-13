# 2.1 JDBC Extract

Connecting to the data sources and retrieving the pertinent data are the responsibilities of this component.
The extraction module may retrieve the data and extract it in the required format using a number of methods, including
SQL queries, API calls, or custom scripts.

The PySpark JDBC Extract Job is a script that extracts data from a JDBC source by connecting to a JDBC URL and reading
data from a table using a SQL pushdown query. The job can be parameterized with options that allow customization of the
extract process, such as specifying the type of extract, the database engine, the extract table, and the database host
and port. Additionally, the job can be configured to repartition the extracted dataframe and write the results to a
specified S3 URI.

To use the PySpark JDBC Extract Job, you will need to specify the following command-line arguments:

| Flag                                | Description                                                                         |
|-------------------------------------|-------------------------------------------------------------------------------------|
| --extract_type:                     | The type of extract to be performed (e.g. FULL or INCREMENTAL).                     |
| --engine:                           | The database engine to be used (e.g. ORACLE or POSTGRES).                           |
| --db_host:                          | The hostname of the database server.                                                |
| --db_port:                          | The port of the database server.                                                    |
| --db_name:                          | The name of the database to be accessed.                                            |
| --db_user:                          | The username for connecting to the database.                                        |
| --db_password:                      | The password for the provided username.                                             |
| --extract_table:                    | The table to be extracted. This argument can be specified in the form schema.table. |
| --extract_s3_uri:                   | The S3 URI to which the extracted data should be written.                           |
| --repartition_dataframe (optional): | Whether or not to repartition the extracted dataframe. This argument should be set  |

to True or False.

## Different Extraction Methods

Data in a relational database can be extracted in several different ways, including a full extract, partial extract, or
extract using upperbound and lowerbound values.

#### Full Extract: FE

A full extract involves extracting all of the data from a relational database. This can be useful when you want to
create a backup of your database, or when you want to analyze all of the data in the database. However, extracting all
of the data from a large database can be time-consuming and resource-intensive, so it's not always the best option.

#### Partial Extract: PE

A partial extract involves extracting only a subset of the data from a relational database. This can be useful when you
only need to analyze a specific portion of the data, or when you want to reduce the amount of time and resources
required to extract the data. To extract a partial dataset, you can use a WHERE clause in your SQL query to specify the
conditions that the data must meet in order to be included in the extract.

### Expressing these Extract Types in SQL

Here are some SQL statements for each of the different extract methods discussed above:

*Full Extract:*

```sql
SELECT * FROM table_name;
```

*Partial Extract:*

```sql
SELECT * FROM table_name
WHERE column_name = 'value';
```

*Extract using upperbound and lowerbound values:*

```sql
SELECT * FROM table_name
WHERE column_name BETWEEN lower_value AND upper_value;
```

To optimize the efficiency of these SQL queries, you can use a few different techniques. Here are some ways to optimize
the performance of your SQL queries:

- Use indexes to speed up the search process. Indexes allow the database to quickly locate and retrieve the data that
  you are looking for, which can improve the performance of your queries.
- Use the right data types for your columns. Choosing the right data type for your columns can help the database to
  store and retrieve data more efficiently, which can improve the performance of your queries.
- Use WHERE clauses to filter the data that you want to extract. Specifying conditions in your WHERE clause can help the
  database to only extract the data that you are interested in, which can improve the performance of your queries.
- Use the LIMIT clause to limit the number of rows that are returned. If you only need a small number of rows from a
  large table, using the LIMIT clause can help to reduce the amount of data that is extracted, which can improve the
  performance of your queries.
- Use a combination of these techniques to optimize the performance of your SQL queries. By using these techniques
  together, you can create SQL queries that are both efficient and effective.

## Getting started with PySpark

Using a secure key kept in AWS Secrets Manager, the following PySpark ETL pipeline ingests data from a relational
database, obfuscates sensitive data, and saves the result as parquet in AWS S3:

```python
import argparse

from pyspark.pandas import DataFrame
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

from codebase import get_logger

# Create a Spark session
SPARK = SparkSession.builder.appName("ingest JDBC source").getOrCreate()
LOGGER = get_logger()

from pyspark.sql.functions import udf


@udf
def encrypt_udf(col, key):
    """
    Encryption UDF.
    """
    return col


def main():
    # Read the data from the source database
    data_frame: DataFrame = (
        SPARK.read.format("jdbc")
            .option("url", _db_url)
            .option("dbtable", _db_table)
            .option("user", _db_user)
            .option("password", _db_password)
            .load()
    )

    for field in _obfuscate_fields:
        # Obfuscate the sensitive data using a secure key
        data_frame = data_frame.withColumn(
            field, encrypt_udf(col(field), _encryption_key)
        )

    # Save the data as parquet in AWS S3
    data_frame.write.mode("overwrite").parquet("S3://<bucket-name>/<output-path>")


if __name__ == "__main__":
    _parser = argparse.ArgumentParser()
    _parser.add_argument("--db_url", type=str)
    _parser.add_argument("--db_table", type=str)
    _parser.add_argument("--db_user", type=str)
    _parser.add_argument("--db_password", type=str)
    _parser.add_argument("--obfuscate_fields", type=str)
    _parser.add_argument("--encryption_key", type=str)

    _args, _ = _parser.parse_known_args()
    _db_table = _args["db_table"]
    _db_user = _args["db_user"]
    _db_url = _args["db_url"]
    _db_password = _args["db_password"]
    _obfuscate_fields: list = _args["obfuscate_fields"].split(",")
    _encryption_key = _args["encryption_key"]

    main()
```

This example uses the encrypt udf function, a PySpark UDF that accepts a column and a key and returns the column's
encrypted form. Then, to encrypt a column in a data frame, use the UDF in a withColumn action. When the UDF is called,
the secure key is supplied as a parameter.

One could also approach this using the PySpark expression:

```python
df = df.withColumn('encrypted_value', F.expr("aes_encrypt(mobno, 'your_secret_key')"))
```

## PySpark Extraction pipeline using AWS ECS

The actions listed below must be completed by a data engineer in order to set up a PySpark ingestion pipeline using AWS
ECS:

1. On the AWS ECS cluster, they would first need to install and set up PySpark. Setting up the required dependencies,
   such as Java and Hadoop, as well as establishing the PySpark environment would be required.
2. The AWS ECS cluster, where the PySpark ingestion pipeline will run, must then be configured by the data engineer.
   Terraform, a tool for building, modifying, and versioning infrastructure quickly and safely, can be used for this.
3. The data engineer would need to specify the cluster's properties, such as the number of instances and their instance
   type, as well as the network and security settings, in order to construct the ECS PySpark cluster in AWS ECS using
   Terraform. The Terraform resources aws ecs cluster and aws ecs task definition can be used to accomplish this.
4. The data engineer can use PySpark to connect to the relational database and load the data into a Spark DataFrame once
   the ECS PySpark cluster has been established.
5. The DataFrame can then be saved in AWS S3 as a parquet file using the PySpark write method by the data engineer. The
   data can be saved in a particular S3 bucket and folder by utilizing the saveAsTable method, which makes this
   possible.

```terraform
# Create an ECS cluster
resource "aws_ecs_cluster" "pyspark_cluster" {
  name = "pyspark-cluster"
}

# Create an EC2 instance that will run the PySpark tasks
resource "aws_instance" "pyspark_worker" {
  ami           = "ami-12345678"
  instance_type = "t2.micro"

  # Add the necessary components for running PySpark on the EC2 instance
  user_data = <<EOF
#!/bin/bash

# Install Java
apt-get update
apt-get install -y openjdk-8-jdk

# Install Spark
wget http://mirror.symnds.com/software/Apache/spark/spark-2.4.5/spark-2.4.5-bin-hadoop2.7.tgz
tar xvf spark-2.4.5-bin-hadoop2.7.tgz

# Set up the environment variables for running PySpark
export SPARK_HOME="$(pwd)/spark-2.4.5-bin-hadoop2.7"
export PYSPARK_PYTHON=python3
EOF
}

# Create an ECS task definition that specifies how to run the PySpark application
resource "aws_ecs_task_definition" "pyspark_task" {
  family                = "pyspark-task"
  container_definitions = <<EOF
[
  {
    "name": "pyspark-container",
    "image": "pyspark-image:latest",
    "cpu": 256,
    "memory": 512,
    "command": [
      "spark-submit",
      "--deploy-mode", "cluster",
      "--master", "yarn",
      "--py-files", "my_pyspark_script.py"
    ]
  }
]
EOF
}

# Create an ECS service that will run the PySpark task on the ECS cluster
resource "aws_ecs_service" "pyspark_service" {
  name            = "pyspark-service"
  cluster         = aws_ecs_cluster.pyspark_cluster.id
  task_definition = aws_ecs_task_definition.pyspark_task.arn
  desired_count   = 1

  # Attach the EC2 instance to the ECS cluster
  attach_instance_role_arn = aws_iam_instance_profile.ecs_instance_role.arn
  attachment {
    instance       = aws_instance.pyspark_worker.id
    target_id      = aws_ecs_cluster.pyspark_cluster.id
    container_name = "pyspark-container"
  }
}

```

We could also make use of a Docker image in ECR that we can reference and reuse in our ECS Container Definitions:

```Dockerfile
FROM python:3.8-slim

RUN apt-get update && apt-get install -y openjdk-11-jre-headless wget
RUN wget -q http://www-us.apache.org/dist/spark/spark-2.4.6/spark-2.4.6-bin-hadoop2.7.tgz
RUN tar xf spark-2.4.6-bin-hadoop2.7.tgz && mv spark-2.4.6-bin-hadoop2.7 /usr/local/spark
RUN pip install pyspark hudi

ENV PATH="/usr/local/spark/bin:${PATH}"

CMD ["pyspark"]

```

## Implementation details and instructions for maintenance and troubleshooting