output "ecr_repo" {
  value = aws_ecr_repository.ecr_repo
}

output "docker_image" {
  value = docker_image.docker_image
}

output "tag" {
  value = var.tag
}