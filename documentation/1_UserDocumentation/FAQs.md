# 1.10 Frequently Asked Questions

**Q: What is the purpose of the codebase?**

- A: The codebase is designed to reduce duplicate code in a cloud environment and data lake by following DRY (Don't
  Repeat
  Yourself) principles, and to properly support unit testing and integration testing.

**Q: How is the codebase available?**

- A: The codebase is available in AWS S3 as a .whl file, .zip file, and a lambda layer .zip file.

**Q: What is the purpose of using a pushdown query for JDBC extract?**

- A: A pushdown query, also known as a "predicate pushdown", is a way to optimize the extraction of data from a JDBC
  source by reducing the amount of data that needs to be transferred over the network. By specifying a WHERE condition
  in
  the pushdown query, the JDBC driver can filter the data at the source before sending it to the client, reducing the
  amount of data transferred and improving performance.

**Q: Why is the alias added to the query in the get_pushdown_query() method?**

- A: The alias is added to the query to give a name to the temporary table that is created when the query is run. This
  can be useful for referencing the table in subsequent queries or for referencing the table's columns.

**Q: How does the extract pipeline work?**

- A: The extract pipeline is a series of steps that are executed to extract data from a JDBC source and save it to an S3
  bucket. The pipeline starts with a Lambda function that is responsible for consuming the event payload, which contains
  a list of tables to extract and additional data needed for the job. This function then sends the payload to an AWS
  Step Function that triggers an extract job. The pipeline then iterates through the list of tables to extract, and for
  each table, it determines the appropriate extract plan and updates the extract tracking table in DynamoDB. The
  pipeline then uses Glue to start the extract job run using the input arguments constructed from the event payload, and
  it saves the extracted data to an S3 bucket.

**Q: What is the extract config manager in the pipeline?**

- A: The extract config manager is a Lambda function that is responsible for consuming the event payload, which contains
  a list of tables to extract and additional data needed for the job. This function then constructs the input arguments
  for the extract jobs and sends the payload to the AWS Step Function that triggers the extract job.

**Q: What is the extract tracking table?**

- A: The extract tracking table is a DynamoDB table that is used to store information about the progress of the extract
  pipeline. This table contains information such as the last successful high watermark value, the last successful low
  watermark value, and the status of the extract job.

**Q: How does the pipeline determine the appropriate extract plan?**

- A: The pipeline determines the appropriate extract plan by comparing the provided high watermark value and low
  watermark value with the values stored in the extract tracking table. If the provided values are not specified, the
  pipeline will use the values stored in the extract tracking table.

**Q: What is the Glue job responsible for in the pipeline?**

- A: The Glue job is responsible for running the extract job using the input arguments constructed from the event
  payload. It reads the data from the JDBC source using the pushdown query and saves the extracted data to an S3 bucket.