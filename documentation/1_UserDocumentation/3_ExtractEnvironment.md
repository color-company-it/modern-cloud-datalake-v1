# 1.3 Extract Environment

## Lambdas & Lambda Layers

### jdbc_extract_manager.py

This is a AWS Lambda function that is responsible for sending a payload to an AWS Step Function that triggers an extract
Glue job. The function first imports necessary modules and defines some environment variables. It then defines a
lambda_handler function, which takes in an event and context (both optional) as arguments.

The event is a dictionary containing the following key-value pairs:

- `source_name`: a string that represents the name of the config file stored in an S3 bucket. The config file is in YAML
  format and has information about the extract Glue job to be run.
- `extract_tables`: a list of tables that are specified in the config file and are to be run in this extract Glue job.
  The function then retrieves the config file from an S3 bucket, using the get_config_from_s3 function and the
  source_name provided in the event. It then processes the config file using the generate_extract_config function.

The function then initializes two empty lists, _tables_to_extract and _tables_not_to_extract. It iterates through the
items in the processed config file and checks if the extract_table field is present in the extract_tables list provided
in the event. If it is, it populates additional data (such as extract_s3_uri and tracking_table_name) and adds the item
to the _tables_to_extract list. If it is not, it adds the extract_table to the _tables_not_to_extract list.

Finally, the function returns a dictionary containing a status key with a value of 200 and a tables_to_extract key with
a value of the _tables_to_extract list. This dictionary will be sent as a payload to the AWS Step Function, which will
trigger the extract Glue job.
