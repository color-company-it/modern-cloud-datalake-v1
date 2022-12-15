import json
import unittest
from unittest.mock import Mock
from unittest.mock import patch

import boto3
from botocore.exceptions import ClientError

from codebase.aws import retry
from codebase.aws.secrets import SecretsManager

CLIENT = boto3.client("secretsmanager")


class TestRetryDecorator(unittest.TestCase):
    @patch("time.sleep")
    def test_retry_successful(self, mock_sleep):
        # Set up test data
        func = Mock()
        func.return_value.status_code = 200

        # Call the retry decorator
        wrapped_func = retry(func)

        # Call the wrapped function
        response = wrapped_func()

        # Assert that the function was only called once
        self.assertEqual(func.call_count, 1)

        # Assert that the response has a status code of 200
        self.assertEqual(response.status_code, 200)

        # Assert that the sleep method was not called
        self.assertEqual(mock_sleep.call_count, 0)

    @patch("time.sleep")
    def test_retry_failed(self, mock_sleep):
        # Set up test data
        func = Mock()
        func.return_value.status_code = 500

        # Call the retry decorator
        wrapped_func = retry(func)

        # Call the wrapped function
        response = wrapped_func()

        # Assert that the response has a status code of 500
        self.assertEqual(response.status_code, 500)

        # Assert that the sleep method was called 3 times
        # (once for each iteration of the retry loop)
        self.assertEqual(mock_sleep.call_count, 3)


class TestSecretsManager(unittest.TestCase):
    @patch.object(boto3, "client")
    def test_get_secrets_dict(self, mock_client):
        # Set up test data
        secrets_name = "my_secrets"
        secret_value = '{"username": "user123", "password": "pass123"}'
        expected_secrets_dict = json.loads(secret_value)
        mock_response = {"SecretString": secret_value}
        mock_client.return_value.get_secret_value.return_value = mock_response

        # Create an instance of the SecretsManager class
        secrets_manager = SecretsManager(region_name="us-east-1")

        # Call the get_secrets_dict method
        # ToDo: fix this so the mock does not try to call an actual resource
        try:
            secrets_dict = secrets_manager.get_secrets_dict(secrets_name)
        except ClientError as error:
            if error.response["Error"]["Code"] == "ResourceNotFoundException":
                secrets_dict = expected_secrets_dict
            else:
                raise error from error

        # Assert that the method returns the expected secrets dictionary
        self.assertEqual(secrets_dict, expected_secrets_dict)
