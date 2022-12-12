/*
The codebase deployment block takes the codebase/ directory
and sets it up as a zip file that can be used by the AWS resources globally.
*/

data "archive_file" "codebase" {
  source_dir       = "${path.root}/../codebase/"
  output_path      = "${path.root}/../codebase.zip"
  type             = "zip"
  output_file_mode = "0666"
}

resource "aws_s3_bucket_object" "codebase" {
  bucket = aws_s3_bucket.enterprise-datalake-poc-2022.bucket
  key    = "codebase.zip"
  source = data.archive_file.codebase.output_path
}