output "buildspec-s3-object-key" {
  value = aws_s3_bucket_object.buildspec-docker.key
}

output "buildspec-s3-object-bucket" {
  value = aws_s3_bucket_object.buildspec-docker.bucket
}

output "codebuild-project-name" {
  value = aws_codebuild_project.codebuild-docker.name
}

output "lambda-function-name" {
  value = aws_lambda_function.lambda-function.function_name
}

output "s3-notification-bucket" {
  value = aws_s3_bucket_object.buildspec-docker.bucket
}
