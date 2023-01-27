import json
import os

import boto3

from codebase import get_logger

# items provided as lambda envs
REGION_NAME = os.getenv("region_name")
SDLC_STAGE = os.getenv("sdlc_stage")
ACCOUNT_ID = os.getenv("account_id")
CONFIG_S3_BUCKET = os.getenv("config_s3_bucket")
EXTRACT_S3_BUCKET = os.getenv("extract_s3_bucket")
EXTRACT_TRACKING_TABLE = os.getenv("extract_tracking_table")
LOGGER = get_logger()


def push_sns_message(source_topic_arn: str, subject: str, message: str) -> dict:
    """
    Sens a message to the relevant source topic ARN found in the Step Function payload.
    """
    client = boto3.client("sns", region_name=REGION_NAME)
    return client.publish(
        TopicArn=source_topic_arn,
        Message=message,
        Subject=subject,
    )


def get_job_run_type(event: dict) -> str:
    """
    Checks if the event payload comes from Glue, EMR or ECS.
    """
    if "JobName" in event:
        return "glue"
    if "ClusterId" in event:
        return "emr"
    if "TaskArn" in event:
        return "ecs"

    raise ValueError("Could not determine job run type from event payload")


def lambda_handler(event, context):
    # iterate through events from the step function map
    for _event in event:
        LOGGER.info(f"Event: {_event}")

        # ToDo: Update handing for EMR and ECS
        _job_run_type = get_job_run_type(event=_event)

        # Check if there was a failure in the event otherwise get the run information
        if "Error" in _event and "Cause" in _event:
            error, cause = _event["Error"], json.loads(_event["Cause"])
            error_message = cause["ErrorMessage"]

            if _job_run_type == "glue":
                job_name = _event["JobName"]
                arguments = _event["Arguments"]
                source_topic_arn = arguments["--source_topic_arn"]
                sns_subject = (
                    f"Error:{error} occurred during Glue Job Run for :{job_name}'"
                )
                sns_message = f"""
                               The error raised was:\n {error_message}
                                """.strip()
            else:
                raise ValueError("Cloud not define SNS payload from event payload")

        else:
            if _job_run_type == "glue":
                job_name = _event["JobName"]
                arguments = _event["Arguments"]
                source_topic_arn = arguments["--source_topic_arn"]
                sns_subject = f"Run Succeeded for Glue Job: {job_name}"
                sns_message = f"""
                Glue Job Run Succeeded for {arguments['--source_type']} source {arguments['--extract_table']}
                """.strip()
            else:
                raise ValueError("Cloud not define SNS payload from event payload")

        LOGGER.info(f"sns_subject: {sns_subject}\nsns_message: {sns_message}")
        push_sns_message(
            source_topic_arn=source_topic_arn, subject=sns_subject, message=sns_message
        )
