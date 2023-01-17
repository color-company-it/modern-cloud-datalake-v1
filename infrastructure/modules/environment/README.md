# Introduction

This Terraform configuration sets up a VPC, private and public subnets, and security groups in AWS for a data lake
environment. The VPC is configured with a private subnet that has no internet access, and a public subnet that has
internet access. The private subnet is used to host the data lake resources, while the public subnet is used to host
resources that need to connect to the internet.
Variables

The following variables are used in this configuration:

- region_name: The region name for the resources. The default value is "us-west-2".
- name: The name for the resources. The default value is "example".

## Resources

The following resources are created in this configuration:

- aws_vpc: A VPC with a CIDR block of "10.0.0.0/16".
- aws_subnet: Two subnets, one private and one public, that are associated with the VPC. The private subnet has a CIDR
  block of "10.0.1.0/24" and the public subnet has a CIDR block of "10.0.2.0/24".
- aws_security_group: Three security groups, one for the VPC and one for each subnet. The VPC security group allows
  inbound traffic only from the trusted sources such as corporate network and outbound traffic to the internet. The
  private subnet's security group allows inbound traffic only from the VPC security group, while the public subnet's
  security group allows inbound traffic only from the VPC security group and outbound traffic to the internet.

## Outputs

The following outputs are exported:

- vpc_id: The ID of the VPC.
- private_subnet_id: The ID of the private subnet.
- public_subnet_id: The ID of the public subnet.

## Usage

It's important to note that this is just an example and you should adjust the resources, subnets, and security groups as
per your specific requirement.