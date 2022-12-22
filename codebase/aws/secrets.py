import json
import logging

import boto3

SECRETS = boto3.client("secretsmanager")


def get_db_secret(secret_name):
    logging.info(f"Getting DBSecret: {secret_name}")
    response = SECRETS.get_secret_value(SecretId=secret_name)
    return json.loads(response["SecretString"])
