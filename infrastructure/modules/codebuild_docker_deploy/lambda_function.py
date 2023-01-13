"""
This Lambda function is responsible for triggering a CodeBuild project on AWS.

It uses the PROJECT_NAME and REGION_NAME environment variables to create a boto3 session and a CodeBuild client.
It then calls the start_build method on the client, passing in the PROJECT_NAME.
In case of success, it returns a JSON object with a 200 statusCode and message indicating the successful
start of the CodeBuild project.
In case of failure, it returns a JSON object with a 400 statusCode and message indicating the failure of
starting the CodeBuild project along with the error message.
"""

import os
import boto3

PROJECT_NAME = os.getenv("PROJECT_NAME")
SESSION = boto3.Session(region_name=os.getenv("REGION_NAME"))
CODEBUILD = SESSION.client("codebuild")


def lambda_handler(event, context):
    try:
        CODEBUILD.start_build(project_name=PROJECT_NAME)
        return {
            "statusCode": 200,
            "message": f"Successfully started codebuild project: {CODEBUILD}",
        }
    except Exception as error:
        return {
            "statusCode": 400,
            "message": f"Unable to start codebuild project codebuild project: {CODEBUILD}, error: {error}",
        }
