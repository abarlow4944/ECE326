import boto3

# Create EC2 resource
ec2 = boto3.resource('ec2')

# Reference your specific instance
instance = ec2.Instance('i-0b209978219218b92')

# Print root device details
print("Root device type:", instance.root_device_type)
print("Root device name:", instance.root_device_name)
