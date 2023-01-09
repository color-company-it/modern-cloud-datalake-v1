import logging
import time
from io import BytesIO

import boto3
import yaml
from botocore.exceptions import ClientError

from codebase.aws import RETRIES, RETRY_CODES, RETRY_DELAY

S3 = boto3.client("s3")


def get_config_from_s3(bucket_name: str, file_name: str) -> dict:
    """
    Downloads and parses a YAML file from an S3 bucket.

    :param bucket_name: Name of the S3 bucket
    :param file_name: Name of the file in the bucket
    :return: Dictionary containing the parsed YAML file data
    """
    # Download the file from S3 and save it to a BytesIO object
    logging.info(f"Getting config from s3://{bucket_name}/{file_name}")

    for i in range(RETRIES):
        try:
            obj = S3.get_object(Bucket=bucket_name, Key=file_name)
            file_data = obj["Body"].read()
            yaml_file = BytesIO(file_data)

            # Parse the .yaml file into a Python dictionary
            return yaml.safe_load(yaml_file)
        except ClientError as error:
            if error.response["Error"]["Code"] in RETRY_CODES:
                logging.warning(
                    f"Encountered a retryable error '{error}', retrying in {retry_delay} seconds"
                )
                time.sleep(RETRY_DELAY)
            else:
                logging.error(
                    f"Encountered a non-retryable error '{error}', raising exception"
                )
                raise
