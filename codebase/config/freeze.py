"""
The freeze class makes use of pickle to store configuration data
that will be used across the datalake environment.

Pickle is a module in Python that allows you to serialize Python
objects into a byte stream, which can be saved to a file or
transmitted over a network. This allows you to save the state of
your program, so that you can restore it later or transfer it
to another Python program.

When you save a class object using pickle, you are able to save the
state of the object and all its attributes, including any instance
variables and methods. This means that you can use the object in
another Python function just as you would use it in the original program.
"""

import pickle

import boto3

S3 = boto3.client("S3")


class Freeze:
    def __init__(self, data: object):
        """
        Initialize the Freeze class.

        :param data: The object to be serialized/deserialized.
        """
        self.data = data

    def save_to_s3(self, bucket: str, key: str) -> None:
        """
        Serialize the object using pickle and
        upload the pickled object to S3.

        :param bucket: The S3 bucket.
        :param key: The S3 key.
        :return: None
        """
        data = pickle.dumps(self.data)
        S3.put_object(Bucket=bucket, Key=key, Body=data)

    @staticmethod
    def load_from_s3(bucket: str, key: str) -> object:
        """
        Download the object from S3 and
        deserialize the object using pickle.

        :param bucket: The S3 bucket.
        :param key: The S3 key.
        :return: The deserialized object.
        """
        response = S3.get_object(Bucket=bucket, Key=key)
        obj = pickle.loads(response["Body"])
        return obj.process_data()

    def process_data(self):
        """
        Process the data stored in self.data.
        """
        # Do something with self.data
        pass
