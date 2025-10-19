import boto3

# Connect to EC2 in region us-east-1
ec2_client = boto3.client('ec2', region_name='us-east-1')
'''
key_name = 'myKeyPair'
key_pair = ec2_client.create_key_pair(KeyName=key_name)

# Save to PEM file
with open(f'{key_name}.pem', 'w') as file:
    file.write(key_pair['KeyMaterial'])

print("Key Pair created and saved as", f'{key_name}.pem')

sg = ec2_client.create_security_group(
    GroupName='ece326-group8',
    Description='Allow SSH, HTTP, and Ping'
)

security_group_id = sg['GroupId']
print("Security Group ID:", security_group_id)

rules = ec2_client.authorize_security_group_ingress(
    GroupId=security_group_id,
    IpPermissions=[
        {
            'IpProtocol': 'icmp',
            'FromPort': -1,
            'ToPort': -1,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        },
        {
            'IpProtocol': 'tcp',
            'FromPort': 22,
            'ToPort': 22,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        },
        {
            'IpProtocol': 'tcp',
            'FromPort': 80,
            'ToPort': 80,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        }
    ]
)
print("Inbound rules set.")
print(rules)
'''
#get existing security group id
security_group_id = ec2_client.describe_security_groups(
    GroupNames=['ece326-group8']
)['SecurityGroups'][0]['GroupId']

instances = ec2_client.run_instances(
    ImageId='ami-0c398cb65a93047f2',  # Ubuntu 22.04 LTS for us-east-1
    InstanceType='t3.micro',           # Free-tier eligible
    KeyName='myKeyPair',
    SecurityGroupIds=[security_group_id],
    MinCount=1,
    MaxCount=1
)

instance_id = instances['Instances'][0]['InstanceId']
print("Launched instance:", instance_id)

ec2_resource = boto3.resource('ec2', region_name='us-east-1')
instance = ec2_resource.Instance(instance_id)

print("Waiting for instance to start...")
instance.wait_until_running()
instance.reload()

print("Instance is running!")
print("Public IPv4 Address:", instance.public_ip_address)
print("Root device type:", instance.root_device_type)
print("Root device name:", instance.root_device_name)
