# 4.1 Configuration

The purpose of using a configuration layer when developing a cloud-based datalake platform is to provide a centralized,
consistent way to manage and control the various components of the platform. This can include things like data source
connections, security settings, data transformation rules, and other aspects of the platform's architecture and
functionality.

There are several benefits to using a configuration layer in a cloud-based datalake platform. Some of these benefits
include:

- Improved consistency and reliability. A configuration layer can help to ensure that all of the components of the
  datalake platform are configured and integrated in a consistent and reliable way. This can help to reduce the risk of
  errors or inconsistencies in the data, and can improve the overall performance and reliability of the platform.
- Enhanced flexibility and scalability. A configuration layer can make it easier to modify or expand the datalake
  platform as needed. For example, you can use the configuration layer to add new data sources or data transformations
  without having to change the underlying code or architecture of the platform. This can make the platform more flexible
  and scalable, and can help to support future growth or changes in the platform.
- Simplified maintenance and management. A configuration layer can provide a single, centralized location for managing
  and controlling the various components of the datalake platform. This can make it easier to maintain and manage the
  platform, and can help to reduce the complexity and overhead of managing a large and complex datalake platform.

In conclusion, using a configuration layer in a cloud-based datalake platform can provide several important benefits,
including improved consistency and reliability, enhanced flexibility and scalability, and simplified maintenance and
management. By using a configuration layer, you can create a more robust and efficient datalake platform that is better
able to support the needs of your organization.

Create a Python script that consumes a yaml configuration file that will set up the parameters and query for a PySpark
relational database ingestion pipeline.

```python
import yaml

from pyspark.sql import SparkSession

with open("config.yml", "r") as f:
    config = yaml.safe_load(f)
spark = (
    SparkSession.builder.appName("pipeline")
        .config("spark.jars.packages", config["jars"])
        .getOrCreate()
)

df = (
    spark.read.format(config["format"])
        .option("url", config["url"])
        .option("dbtable", config["table"])
        .option("user", config["user"])
        .option("password", config["password"])
        .load()
)

df.write.format(config["output_format"]).option("path", config["output_path"]).save()
```