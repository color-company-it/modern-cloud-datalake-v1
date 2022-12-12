# 1.3 Overview of the DataLake

A scalable company data lake developed in the cloud using Python and Terraform would likely have a distributed
a cloud-based data storage provider, such as Amazon S3, was used to create the data lake itself. This
by merely including new nodes to the system as required, would enable the data lake to scale horizontally.
a growing body of information.

The data lake would be created as a modular system, with several components handling various aspects of the
system's efficiency. For instance, different modules could exist for data ingestion, data processing, and data storage.
and access to data. This modular structure would enable various teams within the firm to collaborate on various
components of the platform. It would be simpler to update and manage the data lake over time if the system could operate
independently.

The data lake would be developed using a combination of Python and Terraform to implement this architecture.
Terraform configuration files and code. The various data components would be implemented using Python code.
such as the modules for processing and ingesting data into the lake. On the other side, the Terraform configuration
files would be
used to specify the infrastructure needed to host the data lake, including cloud-based data storage services and
the computing power required to execute the Python code.

Using Python and Terraform, the architecture and design of a scalable enterprise data lake were created in the cloud.
would want to offer a modular, scalable, and adaptable method for handling and storing a lot of data in the
cloud.

## The ETL way

> sticking to the basics before we go mad with power.

A system for extracting data from various sources, transforming the data into a format suitable for analysis, and
loading the data into a data warehouse or another data storage system is known as a scalable cloud-based ETL pipeline.
Such a system's design technique and rationale often take into account a variety of factors, such as the particular
needs of the company or organization, the type and volume of data being processed, and the accessibility and scalability
of the underlying cloud infrastructure.

The necessity to handle enormous volumes of data efficiently and affordably is a crucial factor in the design of a
scalable cloud-based ETL pipeline. Usually, this entails the use of distributed computing and storage technologies like
Hadoop or Spark, which are made to process data concurrently across several cluster nodes. As a result, the ETL pipeline
can expand horizontally by adding more nodes as necessary to handle growing data volumes.

The requirement to allow real-time or nearly real-time data processing is another crucial factor. Businesses and
organizations frequently need to be able to assess data as soon as it becomes available so that they may make decisions
that are both timely and well-informed. A scalable cloud-based ETL pipeline may include stream processing technologies,
like Apache Flink or Apache Storm, which are made to process data in real-time as it is generated, to support this
requirement.

The design of a scalable cloud-based ETL pipeline should take into account the organization's unique business objectives
and requirements in addition to these technical ones. A clear set of pipeline criteria and objectives as well as a list
of the precise sources and categories of data that will be processed may be necessary to accomplish this. Determining
the target data warehouse or storage system where the data will be loaded, as well as the data transformations and
cleaning procedures that will be used on the data, may also be necessary.

Overall, designing a scalable cloud-based ETL pipeline requires both technical know-how and an understanding of the
needs and objectives of the business. It is feasible to create a pipeline that is effective, scalable, and able to
satisfy the unique needs of the company by carefully taking these criteria into account.
Create the schema for a cutting-edge, scalable, cloud-based ETL solution.

The components that make up a modern, highly modular, scalable, cloud-based ETL solution often cooperate to extract,
convert, and load data. The following elements may be found in the solution's schema:

**Data sources:**
The many databases, systems, and other sources listed above are the ones the ETL solution will use to extract data from.
Transactional databases, operational systems, web logs, and social media feeds are a few examples of data sources.

**Extraction module:**
Connecting to the data sources and retrieving the pertinent data are the responsibilities of this component.
The extraction module may retrieve the data and extract it in the required format using a number of methods, including
SQL queries, API calls, or custom scripts.

**Transformation module:**
Any required data transformations, such as cleansing, filtering, or aggregation, must be applied by this component. To
carry out these operations, the transformation module may employ a variety of instruments and methods, including SQL,
Python, or R.

**Load module:**
The converted data must be loaded into the desired data warehouse or storage system by this component. The load module
can effectively load data using a variety of methods, including bulk loading and SQL INSERT statements.
the target system with the data.

**Scheduling and orchestration:**
The execution of the various ETL solution components must be coordinated by this component. A solution like Apache
Airflow or AWS Glue may be used by the scheduling and orchestration component to define
To oversee and control the ETL workflow as well as the execution of the individual tasks.

**Monitoring and alerting:**
This part is in charge of keeping an eye on the performance and general well-being of the ETL solution and issuing
alerts in the event that any problems or faults are found. A variety of methods, like log analysis, performance
measures, or machine learning, may be used by the monitoring and alerting component to monitor the system and spot
potential problems.

![An Example from EDCUBA](https://cdn.educba.com/academy/wp-content/uploads/2019/12/Data-Lake.png.webp)

In general, a modern, highly modular, and scalable cloud-based ETL solution comprises of a variety of various parts that
cooperate to effectively extract, convert, and load data. It is possible to develop a solution that can manage massive
volumes of data and serve the unique demands and requirements of the business or organization by carefully developing
and putting each of these components into place.

# 1.2 Conventions

In an ETL DataLake context, there isn't a single "optimal" naming strategy for script and configuration files because
various businesses may have their own preferences and traditions. However, you might find the following general
principles useful:

1. Use names for your files that are meaningful and descriptive and that express the purpose or content of the file.
2. To make it simple to comprehend and browse your DataLake, apply the same naming convention to all of your files.
3. Avoid naming your files with punctuation, special characters, or spaces because these can cause issues when working
   with the files.
4. Use camelCase or snake case as an easy-to-read and understand naming standard instead of abbreviations or acronyms
   unless they are well-known and often used.
5. To keep track of various versions of your files and prevent confusion, think about implementing a versioning system,
   such as appending a version number or date to your file names.
6. To keep your DataLake tidy and organized, be consistent and adhere to your chosen naming convention in all of your
   files, scripts, and configuration files.

As a result, the naming convention for all files at a source level will be:

```
<source_name>_<etl_stage>_<sdlc_stage>_<use_case>_<version_number>
```

Where `etl_stage` could be:

- config
- extract
- transform
- load

And `sdlc_stage` could be:

- dev
- int
- qa
- prd

And `version_number` is a whole integer:

- 1
- 10
- 100
- and so on...

Scripts and other core features will follow a similar approach, and if a constituent is not needed or unavaialble, the
namespace will
be left blank. So if there is no `sdlc_stage` the name would
be `<source_name>_<etl_stage>__<use_case>_<version_number>`.
This is similar to how AWS constructs arns, where namespaces irrelevant to the arn is left blank resulting in an `::`.
