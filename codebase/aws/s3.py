import logging

import boto3
import yaml
from io import BytesIO

S3 = boto3.client("s3")


def get_config_from_s3(bucket_name: str, file_name: str) -> dict:
    # Download the file from S3 and save it to a BytesIO object
    logging.info(f"Getting config from s3://{bucket_name}/{file_name}")
    obj = S3.get_object(Bucket=bucket_name, Key=file_name)
    file_data = obj["Body"].read()
    yaml_file = BytesIO(file_data)

    # Parse the .yaml file into a Python dictionary
    return yaml.safe_load(yaml_file)
