output "codebuild-project-name" {
  value = aws_codebuild_project.docker-deploy.name
}

output "codebuild-project-service-role" {
  value = aws_codebuild_project.docker-deploy.service_role
}
