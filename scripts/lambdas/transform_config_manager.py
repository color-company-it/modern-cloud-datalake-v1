import os

from codebase import get_logger
from codebase.aws.s3 import get_config_from_s3
from codebase.config import generate_transform_config

# items provided as lambda envs
REGION_NAME = os.getenv("region_name")
SDLC_STAGE = os.getenv("sdlc_stage")
ACCOUNT_ID = os.getenv("account_id")
CONFIG_S3_BUCKET = os.getenv("config_s3_bucket")
EXTRACT_S3_BUCKET = os.getenv("extract_s3_bucket")
TRANSFORM_S3_BUCKET = os.getenv("transform_s3_bucket")
TRANSFORM_TRACKING_TABLE = os.getenv("transform_tracking_table")
LOGGER = get_logger()


def lambda_handler(event, context):
    """
    This function sends a payload to an AWS Step Function that triggers a transform job.
    The payload contains a list of tables to transform and additional data needed for the job.


    :params event (dict): A dictionary containing the following key-value pairs:
        - `source_name` (str): The name of the config file stored in an S3 bucket.
           The config file is in YAML format and has information about the extract
           Glue job to be run.
        - `extract_tables` (list): A list of tables that are specified in the config
           file and are to be run in this extract Glue job.
    :params context (optional): The context in which the function is being executed.

    :returns: A dictionary containing a `status` key with a value of `200` and a
    `tables_to_extract` key with a value of the list of tables to extract and their
    corresponding data. This dictionary will be sent as a payload to the AWS Step
    Function, which will trigger the extract job based on the job_type specified in
    the config.
    """
    LOGGER.info(f"Event: {event}")

    _transform_tables = event["transform_tables"]
    _source_name = event["source_name"]

    _transform_config = get_config_from_s3(
        bucket_name=CONFIG_S3_BUCKET, file_name=f"{_source_name}.yml"
    )
    LOGGER.info(f"Received config object: {_transform_config}")

    _transform_config = generate_transform_config(config=_transform_config)

    _tables_to_transform, _tables_not_to_transform = (
        [],
        [],
    )  # a list to send to the AWS Step Function Map
    for transform_item in _transform_config:
        transform_table = transform_item.get("transform_table")

        # only add to list if ready to be run
        if transform_table in _transform_tables:
            # populate additional data populated by terraform
            transform_item[
                "extract_s3_uri"
            ] = f"s3://{EXTRACT_S3_BUCKET}/{transform_item['db_name']}/{transform_item['transform_table'].replace('.', '/')}/"
            transform_item[
                "transform_s3_uri"
            ] = f"s3://{TRANSFORM_S3_BUCKET}/{transform_item['db_name']}/{transform_item['transform_table'].replace('.', '/')}/"
            transform_item["tracking_table_name"] = TRANSFORM_TRACKING_TABLE
            _tables_to_transform.append(transform_item)
        else:
            _tables_not_to_transform.append(transform_table)

    LOGGER.info(
        f"The extract_table(s) {_tables_not_to_transform} will not be extracted in this run"
    )

    _return = {"status_code": 200, "tables_to_transform": _tables_to_transform}
    LOGGER.info(f"Return: {_return}")
    return _return
