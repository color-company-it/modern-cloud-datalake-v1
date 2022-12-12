# 1.1 Repository Structure

## Overall Repository Structure

For this solution, I am going to make use of my favorite tools, PySpark, Terraform, and Airflow.
Within the repo there will be the following:

```
modern-cloud-datalake-v1/
    |--codebase/        # this is where all the python code and modules are kept, we have no code in the infra layer
    |--tests/           # this is the unittests for the codebase
    |--scripts/         # this is the scripts for the AWS resources such as glue, lambda etc
    |--configuration/   # this is the user-interface to submit configurations that will build to the cloud
    |--infrastructure/  # this is all terraform
    |--orchestration/   # this is all airflow
```

## AWS S3 Buckets

This Terraform configuration file creates several Amazon S3 buckets. The names of the buckets are determined by the
business_name variable, which is prefixed to each bucket's name. For example, if the business_name variable is set to
acme, the codebase-bucket will be named acme-codebase.

The following five S3 buckets are created:

- codebase-bucket: This bucket is used to store the codebase for the business.
- configuration-bucket: This bucket is used to store configuration files for the business.
- orchestration-bucket: This bucket is used for orchestrating processes in the business.
- etl-bucket: This bucket is used for ETL (Extract, Transform, Load) operations in the business.
- scripts-bucket: This bucket is used to store scripts for the business.

All of these buckets have an access control list (ACL) of private, meaning that only authorized users can access the
contents of the bucket.