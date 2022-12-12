output "archive_path" {
  value       = data.archive_file.archive_directory.output_path
  description = "The path to the zip archive that was created"
}

output "bucket_object_key" {
  value       = aws_s3_bucket_object.archive_directory.key
  description = "The key of the object that was created in the S3 bucket"
}
