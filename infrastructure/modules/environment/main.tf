/*
To set up a secure data lake environment in AWS using Terraform, you can use the following steps:

    Create a VPC with a private and a public subnet. The private subnet should have no internet
    access and will host the data lake resources such as the S3 bucket and the data lake analytics
    service. The public subnet should have internet access and will host resources that need to
    connect to the internet such as a NAT gateway.

    Create a security group for the VPC that allows inbound traffic only from trusted sources such
    as your corporate network and outbound traffic to the internet.

    Create security groups for the private and public subnets. The private subnet's security group
    should allow inbound traffic only from the VPC's security group, while the public subnet's
    security group should allow inbound traffic only from the VPC's security group and outbound
    traffic to the internet.

    Create an S3 bucket and configure it to only accept connections from the private subnet's
    security group.

    Create a NAT gateway in the public subnet to allow outbound internet access for resources
    in the private subnet.

    Add your data lake analytics resources to the private subnet and configure them to use the
    NAT gateway for internet access.

    Test your setup to ensure that resources in the private subnet can access the internet while
    remaining secure from external threats.

It is important to note that this is just a general example and you should adjust the resources,
subnets, and security groups as per your specific requirement.
*/


resource "aws_vpc" "default" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "private" {
  vpc_id            = aws_vpc.default.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "${var.region_name}a"
}

resource "aws_subnet" "public" {
  vpc_id            = aws_vpc.default.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "${var.region_name}b"
}

resource "aws_security_group" "vpc" {
  name        = "${var.name}-vpc"
  description = "Controls access to the VPC"
  vpc_id      = aws_vpc.default.id

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["10.0.0.0/8"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "private" {
  name        = "${var.name}-private"
  description = "Controls access to the private subnet"
  vpc_id      = aws_vpc.default.id

  ingress {
    from_port       = 0
    to_port         = 0
    protocol        = "-1"
    security_groups = [aws_security_group.vpc.id]
  }
}

resource "aws_security_group" "public" {
  name        = "${var.name}-public"
  description = "Controls access to the public subnet"
  vpc_id      = aws_vpc.default.id

  ingress {
    from_port       = 0
    to_port         = 0
    protocol        = "-1"
    security_groups = [aws_security_group.vpc.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

