"""A Python Pulumi program"""

import pulumi
import pulumi_aws as aws

vpc = aws.ec2.Vpc("my-vpc",
    cidr_block="10.10.0.0/16",
    enable_dns_hostnames=True,
    enable_dns_support=True,
    )

public_subnet = aws.ec2.Subnet("public-subnet",
    vpc_id = vpc.id,
    cidr_block = "10.10.1.0/24",
    map_public_ip_on_launch=True,
    availability_zone='ap-southeast-1a',
    )