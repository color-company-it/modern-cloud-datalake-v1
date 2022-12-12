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