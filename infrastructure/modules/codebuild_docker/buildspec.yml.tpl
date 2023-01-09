version: 0.2
phases:
  pre_build:
    commands:
      - echo Logging into AWS ECR
      - aws ecr get-login-password --region ${region} | docker login --username AWS --password-stdin ${account-id}-dkr.ecr.${region}.amazonaws.com
  build:
    commands:
      - echo Build started on `date`
      - echo Building the Docker image...
      - docker build -t ${docker-tag}:latest
      - docker tag ${docker-tag} ${account-id}-dkr.ecr.${region}.amazonaws.com/${docker-tag}:latest
  post_build:
    commands:
      - echo Build completed on `date`
      - echo Pushing the Docker image...
      - docker push ${account-id}-dkr.ecr.${region}.amazonaws.com/${docker-tag}:latest