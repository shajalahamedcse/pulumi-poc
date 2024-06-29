"""A Python Pulumi program"""

import pulumi
import pulumi_aws as aws
import os

vpc = aws.ec2.Vpc("my-vpc",
    cidr_block="10.10.0.0/16",
    enable_dns_hostnames=True,
    enable_dns_support=True,
    tags={
        "Name": "MyVPC"  # Replace "MyVPC" with your desired name
    }
    )

public_subnet = aws.ec2.Subnet("public-subnet",
    vpc_id = vpc.id,
    cidr_block = "10.10.1.0/24",
    map_public_ip_on_launch=True,
    availability_zone='ap-southeast-1a',
    )

igw = aws.ec2.InternetGateway("igw",vpc_id=vpc.id)

# Create Route Table
route_table = aws.ec2.RouteTable("route-table",
    vpc_id=vpc.id,
    routes=[{
        "cidr_block": "0.0.0.0/0",
        "gateway_id": igw.id,
    }],
)

# Associate Route Table with Public Subnet
rt_assoc_public = aws.ec2.RouteTableAssociation("rt-assoc-public",
    subnet_id=public_subnet.id,
    route_table_id=route_table.id,
)

# Create Security Group
security_group = aws.ec2.SecurityGroup("web-secgrp",
    description='Enable SSH and K3s access',
    vpc_id=vpc.id,
    ingress=[
        {
            "protocol": "tcp",
            "from_port": 22,
            "to_port": 22,
            "cidr_blocks": ["0.0.0.0/0"],
        },
        {
            "protocol": "tcp",
            "from_port": 6443,
            "to_port": 6443,
            "cidr_blocks": ["0.0.0.0/0"],
        },
    ],
    egress=[{
        "protocol": "-1",
        "from_port": 0,
        "to_port": 0,
        "cidr_blocks": ["0.0.0.0/0"],
    }],
)


ami_id = "ami-003c463c8207b4dfa"  # Replace with a valid AMI ID for your region
instance_type = "t3.small"

# Read the public key from the environment (set by GitHub Actions)
public_key = os.getenv("PUBLIC_KEY")
# Create the EC2 KeyPair using the public key
key_pair = aws.ec2.KeyPair("my-key-pair",
    key_name="my-key-pair",
    public_key=public_key)


master_node = aws.ec2.Instance("master-node",
    instance_type=instance_type,
    ami=ami_id,
    subnet_id=public_subnet.id,
    key_name=key_pair.key_name,
    vpc_security_group_ids=[security_group.id],
    tags={
        "Name": "master-node"
    })


worker_node_1 = aws.ec2.Instance("worker-node-1",
    instance_type=instance_type,
    ami=ami_id,
    subnet_id=public_subnet.id,
    key_name=key_pair.key_name,
    vpc_security_group_ids=[security_group.id],
    tags={
        "Name": "worker-node-1"
    })

worker_node_2 = aws.ec2.Instance("worker-node-2",
    instance_type=instance_type,
    ami=ami_id,
    subnet_id=public_subnet.id,
    key_name=key_pair.key_name,
    vpc_security_group_ids=[security_group.id],
    tags={
        "Name": "worker-node-2"
    })


# Create Nginx instance
nginx_instance = aws.ec2.Instance("nginx-instance",
    instance_type=instance_type,
    ami=ami_id,
    subnet_id=public_subnet.id,
    key_name=key_pair.key_name,
    vpc_security_group_ids=[security_group.id],
    tags={
        "Name": "nginx-instance"
    })

# Export outputs
pulumi.export("master_public_ip", master_node.public_ip)