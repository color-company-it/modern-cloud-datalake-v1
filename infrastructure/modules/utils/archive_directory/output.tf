output "archive_path" {
  value       = data.archive_file.archive_directory.output_path
  description = "The path to the zip archive that was created"
}

output "object_uri" {
  value       = "s3://${aws_s3_bucket_object.archive_directory.bucket}/${aws_s3_bucket_object.archive_directory.key}"
  description = "The uri of the object that was created in the S3 bucket"
}
