import json

import boto3

from codebase.aws import retry

CLIENT = boto3.client("secretsmanager")


class SecretsManager:
    def __init__(self):
        self._client = boto3.client("secretsmanager")

    def get_client(self):
        return self._client

    @retry
    def get_secrets_dict(self, secrets_name: str) -> dict:
        """
        Gets a dictionary object containing secrets from an AWS Secrets resource.

        :param secrets_name: The name of the secrets' resource in AWS Secrets Manager.
        :return: A dictionary object containing the secrets.
        """

        # Get the secret value
        response = self._client.get_secret_value(SecretId=secrets_name)

        # Decrypt the secret value (if necessary)
        if "SecretString" in response:
            secret_value = response["SecretString"]
        else:
            # Decrypts secret using the associated KMS CMK.
            # Depending on whether the secret is a string or binary, one of these fields will be populated.
            secret_binary = response["SecretBinary"]

            # Convert the binary secret value to a string
            secret_value = secret_binary.decode("utf-8")

        # Parse the secret value as a JSON object
        secrets_dict = json.loads(secret_value)

        return secrets_dict
