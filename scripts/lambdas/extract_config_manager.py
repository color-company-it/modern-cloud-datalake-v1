import os

from codebase import get_logger
from codebase.aws.s3 import get_config_from_s3
from codebase.config import generate_extract_config

# items provided as lambda envs
REGION_NAME = os.getenv("region_name")
SDLC_STAGE = os.getenv("sdlc_stage")
ACCOUNT_ID = os.getenv("account_id")
CONFIG_S3_BUCKET = os.getenv("config_s3_bucket")
EXTRACT_S3_BUCKET = os.getenv("extract_s3_bucket")
EXTRACT_TRACKING_TABLE = os.getenv("extract_tracking_table")
LOGGER = get_logger()


def set_extract_item(extract_item: dict, source_name: str) -> dict:
    """
    Method to quickly update the extract item with the relevant dynamic information.
    """
    extract_item[
        "extract_s3_uri"
    ] = f"s3://{EXTRACT_S3_BUCKET}/{source_name}/{extract_item['db_name']}/{extract_item['extract_table'].replace('.', '/')}/"
    extract_item["tracking_table_name"] = EXTRACT_TRACKING_TABLE
    return extract_item


def lambda_handler(event, context):
    """
    This function sends a payload to an AWS Step Function that triggers an extract job.
    The payload contains a list of tables to extract and additional data needed for the job.


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

    _extract_tables = event["extract_tables"]
    _source_name = event["source_name"]

    _extract_config = get_config_from_s3(
        bucket_name=CONFIG_S3_BUCKET, file_name=f"{_source_name}.yml"
    )
    LOGGER.info(f"Received config object: {_extract_config}")

    _extract_config = generate_extract_config(_extract_config)

    _tables_to_extract, _tables_not_to_extract = (
        [],
        [],
    )  # a list to send to the AWS Step Function Map
    for extract_item in _extract_config:
        extract_table = extract_item.get("extract_table")

        # if _extract_tables is "*" then all tables can be run
        if _extract_tables == "*":
            extract_item = set_extract_item(
                extract_item=extract_item, source_name=_source_name
            )
            _tables_to_extract.append(extract_item)

        # only add to list if ready to be run
        else:
            if extract_table in _extract_tables:
                extract_item = set_extract_item(
                    extract_item=extract_item, source_name=_source_name
                )
                _tables_to_extract.append(extract_item)
            else:
                _tables_not_to_extract.append(extract_table)

    LOGGER.info(
        f"The extract_table(s) {_tables_not_to_extract} will not be extracted in this run"
    )

    _return = {"status_code": 200, "tables_to_extract": _tables_to_extract}
    LOGGER.info(f"Return: {_return}")
    return _return
