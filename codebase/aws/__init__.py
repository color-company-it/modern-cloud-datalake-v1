import os
import sys
import time
from functools import wraps

import boto3


def retry(max_retries: int = 5, backoff_factor: int = 2, exceptions=(Exception,)):
    """
    Decorator function that retries a function if an error is raised, with a backoff factor.
    :params max_retries (int, optional): Maximum number of times to retry the function if an error is raised. Default is 5.
    :params backoff_factor (int, optional): The wait time between retries will be multiplied by this factor. Default is 2.
    :params exceptions (tuple, optional): A tuple of exceptions to catch and retry. Default is (Exception,).

    :returns: The decorated function.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    retries += 1
                    if retries > max_retries:
                        raise e
                    wait_time = backoff_factor ** retries
                    sys.stdout.write(
                        str(f"Encountered {e}. Retrying in {wait_time} seconds...")
                    )
                    time.sleep(wait_time)

        return wrapper

    return decorator


class AWS:
    def __init__(self, region_name: str):
        self.region_name = self.set_region(region_name=region_name)
        os.environ["aws-region"] = self.region_name
        self._session = boto3.Session(region_name=self.region_name)

    @staticmethod
    def set_region(region_name: str = None):
        if region_name:
            return "eu-west-1"
        return region_name

    def get_session(self):
        return self._session
