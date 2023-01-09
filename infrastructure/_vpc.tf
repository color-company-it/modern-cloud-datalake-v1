resource "aws_vpc" "datalake" {
  cidr_block = "10.0.0.0/16"

  tags = {
    sdlc-stage   = var.sdlc-stage
    company-name = var.business-name
  }
}

resource "aws_subnet" "datalake" {
  vpc_id     = aws_vpc.datalake.id
  cidr_block = "10.0.1.0/24"

  tags = {
    sdlc-stage   = var.sdlc-stage
    company-name = var.business-name
  }
}

resource "aws_security_group" "datalake" {
  name   = "${var.business-name}-${var.sdlc-stage}-sg"
  vpc_id = aws_vpc.datalake.id

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    sdlc-stage   = var.sdlc-stage
    company-name = var.business-name
  }
}
