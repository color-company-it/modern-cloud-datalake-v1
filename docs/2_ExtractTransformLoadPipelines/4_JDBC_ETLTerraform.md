# 4.1 AWS S3 Buckets

The Terraform code creates several AWS S3 buckets and uploads various files to them.
The code first creates an S3 bucket for the codebase, with the bucket name derived from a variable business-name. The
bucket's access control list (ACL) is set to "private". This can be refined to use other configurations in a business
environment such as KMS.

> Amazon Web Services (AWS) Key Management Service (KMS) is a managed service that makes it easy for you to create and
> control the encryption keys used to encrypt your data.
> KMS allows you to create, rotate, disable, and define policies for the keys used to encrypt your data. This provides
> you with a central location to manage the keys that protect your data across a variety of AWS services, such as S3,
> EBS, and RDS.

Next, the code uses a module called archive_directory to create a zip archive of the codebase directory and upload it to
the codebase bucket, with the key "codebase/codebase.zip".

Then, the code creates another zip archive, this time of the codebase_layer directory, and uploads it to the codebase
bucket with the key "codebase/codebase_layer.zip".

The code then creates a separate S3 bucket for configuration files and uploads the files listed in the
configuration-files local variable to the bucket.

Another S3 bucket is created for orchestration files, but no files are currently being uploaded to it.
Similarly, an S3 bucket is created for ETL pipeline files, but no further action is taken with it.

Finally, the code creates an S3 bucket for scripts and uploads two groups of files to it: "docker" scripts and "
spark/jdbc" scripts. The files to be uploaded are listed in the local variables docker-scripts and spark-jdbc-scripts,
respectively.

# 4.2 Running Docker Containers

To create a shell script for a docker entrypoint that takes container environment variables and runs a PySpark script
that uses argparse, you can use the following approach:

1. Define the PySpark script that uses argparse and processes the required arguments. This script should use the
   argparse module to define and parse the required arguments, and then use those arguments to perform the necessary
   operations in PySpark.
2. In the shell script, use the docker command to run the PySpark script inside a Docker container, passing the required
   arguments and environment variables as necessary. You can use the -e flag to pass environment variables to the Docker
   container, and the -v flag to mount the local directory containing the PySpark script inside the container.