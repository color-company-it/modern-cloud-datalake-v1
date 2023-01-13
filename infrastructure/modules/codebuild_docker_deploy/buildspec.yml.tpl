version: 0.2

phases:
  pre_build:
    commands:
      - echo "Logging in to ECR with region ${region_name} and repo ${ecr_repo}..."
      - aws ecr get-login-password --region ${region_name} | docker login --username AWS --password-stdin ${ecr_repo}
  build:
    commands:
      - echo "Building Docker image with tag ${docker_tag}..."
      - docker build -t ${docker_tag}:latest .
      - echo "Tagging image with ECR repo URL ${ecr_repo}..."
      - docker tag ${docker_tag} ${ecr_repo}${docker_tag}:latest
  post_build:
    commands:
      - echo "Pushing image to ECR repo ${ecr_repo} with tag ${docker_tag}..."
      - docker push ${ecr_repo}${docker_tag}:latest
