# 1 Codebase

The entire repository makes use of a single codebase that is imported for all ETL scripts.
This follows the much-needed DRY principle that is often missed in most cloud-based environment.
This is achieved by making use of archive and import methods for resources such as AWS Glue, EMR and ECS.

It is important to stress that this codebase should be completely divorced from the business logic,
and should instead focus on being a repository for utilities and industry standard tools that are
tech-agnostic. They can be used in any environment that hs the necessary dependencies, and as a result,
is not a critical factor in the security of the Data Lake.

This codebase is also available via PyPi, so services can pip install it where they need it.
Remember that the Python Index is not secure and sensitive code should never be sent there.

## 1.1 AWS Interface | codebase.aws

### codebase.aws.AWS

The module has a base class called `AWS` that serves as an "interface" for developers to use boto3
with minimal effort and code. Though Boto3 on it's own is terrific, making use of interfaces allows
developers to reduce the need to page, handle response errors and monitor api request statuses.
Rather have a codebase that does all of this for you.

```python
from codebase.aws import AWS

aws = AWS(region_name="eu-west-1")
session = aws.get_session()
```

### codebase.aws.retry

The retry function is a decorator that wraps a function and retries the function a specified number of times if it
doesn't return a successful response. If the wrapped function returns a response with a status code of 200, the
decorator will immediately return the response. Otherwise, the decorator will wait for an increasing amount of time
between each retry, using a backoff factor to determine the amount of time to wait. After the specified number of
retries, the decorator will return the final response from the wrapped function, regardless of the status code.

Here is an example of how to use the retry decorator:

```python
import requests
from codebase.aws import retry


@retry
def make_request():
    response = requests.get('http://example.com')
    return response
```

In this example, the make_request function will be retried up to three times if the response has a status code other
than 200. Between each retry, the decorator will wait for an increasing amount of time determined by the backoff factor.
If the function returns a successful response on any of the retries, the decorator will immediately return the response.
Otherwise, it will return the final response from the function after all retries have been attempted.