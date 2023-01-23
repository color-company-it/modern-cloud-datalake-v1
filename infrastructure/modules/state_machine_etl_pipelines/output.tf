output "sns_topic" {
  value = aws_sns_topic.source_topic
}

output "extract_state_machine" {
  value = aws_sfn_state_machine.extract.*
}
