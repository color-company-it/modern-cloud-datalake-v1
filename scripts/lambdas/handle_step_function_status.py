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
    _return = {"status_code": 200}
    LOGGER.info(f"Return: {_return}")
    return json.dumps(_return)
