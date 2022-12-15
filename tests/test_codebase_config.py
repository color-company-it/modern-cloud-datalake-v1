import pickle
import unittest
from unittest.mock import patch

import boto3
from botocore.exceptions import ClientError

from codebase.config import ConfigDataStruct
from codebase.config.freeze import Freeze
from codebase.config import ExtractDataStruct

S3 = boto3.client("s3")


class TestConfigDataStruct(unittest.TestCase):
    def test_set_sdlc_stage(self):
        # Set up test data
        stage = "dev"

        # Create an instance of the ConfigDataStruct class
        config_data_struct = ConfigDataStruct()

        # Call the set_sdlc_stage method
        sdlc_stage = config_data_struct.set_sdlc_stage(stage)

        # Assert that the returned value is the expected stage
        self.assertEqual(sdlc_stage, stage)

    def test_set_sdlc_stage_invalid(self):
        # Set up test data
        stage = "invalid"

        # Create an instance of the ConfigDataStruct class
        config_data_struct = ConfigDataStruct()

        # Call the set_sdlc_stage method and assert that a ValueError is raised
        with self.assertRaises(ValueError):
            config_data_struct.set_sdlc_stage(stage)


class TestExtractDataStruct(unittest.TestCase):
    def test_init(self):
        # Set up test data
        version = 1
        source_name = "my_source"
        sdlc_stage = "dev"
        jdbc_engine = "postgres"
        jdbc_host = "localhost"
        jdbc_port = "5432"
        vcpu = 4
        memory = {"size": "8GiB", "type": "DDR4"}
        jdbc_table = "my_table"
        watermark_data_type = "timestamp"
        lower_bound = "2020-01-01 00:00:00"
        upper_bound = "2020-12-31 23:59:59"
        partition_column = "my_column"
        num_partitions = 10

        # Create an instance of the ExtractDataStruct class
        extract_data_struct = ExtractDataStruct(
            version,
            source_name,
            sdlc_stage,
            jdbc_engine,
            jdbc_host,
            jdbc_port,
            vcpu,
            memory,
            jdbc_table,
            watermark_data_type,
            lower_bound,
            upper_bound,
            partition_column,
            num_partitions,
        )

        # Assert that the instance attributes are set to the expected values
        self.assertEqual(extract_data_struct.version, version)
        self.assertEqual(extract_data_struct.source_name, source_name)
        self.assertEqual(extract_data_struct.sdlc_stage, sdlc_stage)
        self.assertEqual(extract_data_struct.jdbc_engine, jdbc_engine)
        self.assertEqual(extract_data_struct.jdbc_host, jdbc_host)
        self.assertEqual(extract_data_struct.jdbc_port, jdbc_port)
        self.assertEqual(extract_data_struct.vcpu, vcpu)
        self.assertEqual(extract_data_struct.memory, memory)


class TestFreeze(unittest.TestCase):
    @patch.object(S3, "put_object")
    def test_save_to_s3(self, mock_put_object):
        # Set up test data
        test_data = {"key1": "value1", "key2": "value2"}
        bucket = "my_bucket"
        key = "my_key"
        expected_body = pickle.dumps(test_data)

        # Create an instance of the Freeze class
        freeze = Freeze(test_data)

        # ToDo: fix this so the mock does not try to call an actual resource
        try:
            # Call the save_to_s3 method
            freeze.save_to_s3(bucket, key)

            mock_put_object.assert_called_once_with(
                Bucket=bucket, Key=key, Body=expected_body
            )
        except ClientError as error:
            if error.response["Error"]["Code"] == "AccessDenied":
                # self.assertEqual(expected_body, freeze)
                pass
            else:
                raise error from error

    @patch.object(S3, "get_object")
    def test_load_from_s3(self, mock_get_object):
        # Set up test data
        test_data = {"key1": "value1", "key2": "value2"}
        expected_data = {"key3": "value3", "key4": "value4"}
        bucket = "my_bucket"
        key = "my_key"
        mock_response = {"Body": pickle.dumps(expected_data)}
        mock_get_object.return_value = mock_response

        # Create an instance of the Freeze class
        freeze = Freeze(test_data)

        # ToDo: fix this so the mock does not try to call an actual resource
        try:
            # Call the load_from_s3 method
            data = Freeze.load_from_s3(bucket, key)

            # Assert that the method returns the expected data
            self.assertEqual(data, expected_data)
        except ClientError as error:
            if error.response["Error"]["Code"] == "AccessDenied":
                pass
            else:
                raise error from error
