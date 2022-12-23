output "lambda_function_arn" {
  value = aws_lambda_function.lambda-function.arn
}

output "lambda_function_name" {
  value = aws_lambda_function.lambda-function.function_name
}

output "lambda_function_invoke_arn" {
  value = aws_lambda_function.lambda-function.invoke_arn
}