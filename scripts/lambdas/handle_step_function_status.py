import json
import os

from codebase import get_logger

# items provided as lambda envs
REGION_NAME = os.getenv("region_name")
SDLC_STAGE = os.getenv("sdlc_stage")
ACCOUNT_ID = os.getenv("account_id")
CONFIG_S3_BUCKET = os.getenv("config_s3_bucket")
EXTRACT_S3_BUCKET = os.getenv("extract_s3_bucket")
EXTRACT_TRACKING_TABLE = os.getenv("extract_tracking_table")
LOGGER = get_logger()


def lambda_handler(event, context):
    LOGGER.info(f"Event: {event}")
    _return = {"status_code": 200}
    LOGGER.info(f"Return: {_return}")

    sns_message = None

    # Check if there was a failure in the event
    if "Error" in event and "Cause" in event:
        error, cause = event["Error"], json.loads(event["Cause"])
        error_message = cause["ErrorMessage"]

        if "JobName" in cause:
            job_name = cause["JobName"]
            print(
                f"Error:`{error}` occurred during Glue Job Run for :`{job_name}`, with  {error_message}"
            )

    else:
        if "JobName" in event:
            job_name = event["JobName"]
            print(f"Run Succeeded for Glue Job: {job_name}")

    return json.dumps(_return)
