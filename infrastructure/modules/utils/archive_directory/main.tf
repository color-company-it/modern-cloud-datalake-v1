/*
This Terraform configuration file uses the archive_file data source to create a
zip archive from a source directory specified by the source_dir variable.
The archive is saved to the output_path specified by the output_path variable.

The aws_s3_bucket_object resource then creates an object in an Amazon S3
bucket with the name specified by the bucket_name variable.
The object's key is specified by the bucket_key variable,
and the object's contents are the zip archive created by the archive_file
data source. This allows the contents of the source directory to be uploaded
to an S3 bucket.
*/

data "archive_file" "archive_directory" {
  source_dir       = var.source_dir
  output_path      = var.output_path
  type             = "zip"
  output_file_mode = "0666"
}

resource "aws_s3_bucket_object" "archive_directory" {
  bucket = var.bucket_name
  key    = var.bucket_key
  source = data.archive_file.archive_directory.output_path
}