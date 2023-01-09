import os

import boto3
import logging

CODEBUILD_PROJECT_NAME = os.getenv("codebuild_project_name")
CODEBUILD = boto3.client("codebuild")


def lambda_handler(event, context):
    try:
        logging.info(f"Starting codebuild project: {CODEBUILD_PROJECT_NAME}")
        CODEBUILD.start_build(projectName=CODEBUILD_PROJECT_NAME)
    except Exception as error:
        msg = f"Unable to start codebuild project: {CODEBUILD_PROJECT_NAME} with error {error}"
        logging.info(msg)
        return msg
