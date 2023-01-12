version: 0.2

phases:
  pre_build:
    commands:
      - aws ecr get-login-password --region ${region_name} | docker login --username AWS --password-stdin ${ecr_repo}
  build:
    commands:
      - docker build -t ${docker_tag}:latest .
      - docker tag ${docker_tag} ${ecr_repo}${docker_tag}:latest
  post_build:
    commands:
      - docker push ${ecr_repo}${docker_tag}:latest

