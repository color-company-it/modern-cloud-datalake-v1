import sys
import time
from typing import Callable

import boto3


def retry(func: Callable) -> Callable:
    """
    A decorator that will attempt the boto3 request 3
    times if the response code is not 200 before
    returning the error.

    :param func: The function to wrap and retry.
    :return: A wrapped version of the original function.
    """

    def wrapper(*args, **kwargs):
        max_retries = 3
        backoff_factor = 0.5

        response = None
        for i in range(1, max_retries + 1):
            response = func(*args, **kwargs)
            if response.status_code == 200:
                return response
            else:
                sleep_time = backoff_factor * (2**i)
                sys.stdout.write(
                    str(
                        f"Boto3 call returned status code: {response.status_code} "
                        f"attempting again in {sleep_time} seconds. Attempt {i}/3"
                    )
                    + "\n"
                )
                time.sleep(sleep_time)
        return response

    return wrapper


class AWS:
    def __init__(self, region_name: str):
        self._session = boto3.Session(region_name=region_name)

    def get_session(self):
        return self._session
