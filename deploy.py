## one-click deployment script

#!/usr/bin/env python3
import json
import os
import sys
import time
import subprocess

def ensure_boto3():
    try:
        import boto3  # noqa
        return
    except ImportError:
        print("[INFO] boto3 not found. Attempting to install via pip...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "boto3"])
        except Exception as e:
            print("Details:", e)
            sys.exit(1)

ensure_boto3()
import boto3
from botocore.exceptions import ClientError


def run_cmd(cmd, description=None):
    """Run a shell command and raise if it fails."""
    if description:
        print(f"[CMD] {description}")
    print("      ", " ".join(cmd))
    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError as e:
        print("[ERROR] Command failed with exit code", e.returncode)
        sys.exit(1)


def load_config(config_path):
    with open(config_path, "r") as f:
        return json.load(f)


def get_or_create_security_group(ec2_client, group_name, vpc_id=None):
    """Return security group ID. Create it if not existing."""
    try:
        response = ec2_client.describe_security_groups(GroupNames=[group_name])
        sg_id = response["SecurityGroups"][0]["GroupId"]
        print(f"[INFO] Using existing security group '{group_name}' ({sg_id})")
        return sg_id
    except ClientError as e:
        if "InvalidGroup.NotFound" not in str(e):
            raise

        print(f"[INFO] Security group '{group_name}' not found. Creating it...")
        create_args = {
            "GroupName": group_name,
            "Description": "Allow SSH and app port (8080)",
        }
        if vpc_id:
            create_args["VpcId"] = vpc_id

        sg = ec2_client.create_security_group(**create_args)
        sg_id = sg["GroupId"]
        print("[INFO] Created security group:", sg_id)

        # Add ingress rules: SSH (22), HTTP (80), ICMP (ping)
        ec2_client.authorize_security_group_ingress(
            GroupId=sg_id,
            IpPermissions=[
                {
                    "IpProtocol": "icmp",
                    "FromPort": -1,
                    "ToPort": -1,
                    "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
                },
                {
                    "IpProtocol": "tcp",
                    "FromPort": 22,
                    "ToPort": 22,
                    "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
                },
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 8080,
                    'ToPort': 8080,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                },
            ],
        )
        print("[INFO] Inbound rules configured.")
        return sg_id


def main():
    if len(sys.argv) != 2:
        print("Usage: python deploy.py <aws_config.json>")
        sys.exit(1)

    config_path = sys.argv[1]
    if not os.path.exists(config_path):
        print(f"[ERROR] Config file '{config_path}' not found.")
        sys.exit(1)

    config = load_config(config_path)

    aws_access_key_id = config.get("aws_access_key_id")
    aws_secret_access_key = config.get("aws_secret_access_key")
    region_name = config.get("region_name", "us-east-1")
    ami_id = config.get("ami_id")
    instance_type = config.get("instance_type", "t3.micro")
    key_name = config.get("key_name")
    ssh_key_path = config.get("ssh_key_path")
    security_group_name = config.get("security_group_name")
    local_app_path = config.get("local_app_path", ".")
    remote_app_path = config.get("remote_app_path", "/home/ubuntu/app/app_src")
    startup_command = config.get("startup_command")
    exposed_port = config.get("exposed_port", 80)

    if not all([aws_access_key_id, aws_secret_access_key, ami_id, key_name, ssh_key_path, security_group_name, startup_command]):
        print("[ERROR] Missing required fields in config file.")
        sys.exit(1)

    if not os.path.isfile(ssh_key_path):
        print(f"[ERROR] SSH key file not found: {ssh_key_path}")
        sys.exit(1)

    # Initialize EC2 client/resource
    ec2_client = boto3.client(
        "ec2",
        region_name=region_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )
    ec2_resource = boto3.resource(
        "ec2",
        region_name=region_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )

    # Determine default VPC for security group if needed
    vpcs = ec2_client.describe_vpcs()
    default_vpc = next((v for v in vpcs["Vpcs"] if v.get("IsDefault")), None)
    vpc_id = default_vpc["VpcId"] if default_vpc else None

    security_group_id = get_or_create_security_group(ec2_client, security_group_name, vpc_id)

    print("[INFO] Launching EC2 instance...")
    instances = ec2_client.run_instances(
        ImageId=ami_id,
        InstanceType=instance_type,
        KeyName=key_name,
        SecurityGroupIds=[security_group_id],
        MinCount=1,
        MaxCount=1,
    )

    instance_id = instances["Instances"][0]["InstanceId"]
    instance = ec2_resource.Instance(instance_id)

    print(f"[INFO] Launched instance: {instance_id}")
    print("[INFO] Waiting for instance to start...")
    instance.wait_until_running()
    instance.reload()

    public_ip = instance.public_ip_address
    public_dns = instance.public_dns_name
    print("[INFO] Instance is running.")
    print(f"[INFO] Public IP: {public_ip}")
    print(f"[INFO] Public DNS: {public_dns}")

    # Give SSH some extra time
    time.sleep(30)

    # Ensure remote directory exists
    ssh_base = [
        "ssh",
        "-o", "StrictHostKeyChecking=no",
        "-i", ssh_key_path,
        f"ubuntu@{public_ip}",
    ]

    run_cmd(
        ssh_base + [f"mkdir -p {remote_app_path}"],
        "Create remote application directory"
    )

    # Copy application files (recursive)
    run_cmd(
        [
            "scp",
            "-o", "StrictHostKeyChecking=no",
            "-i", ssh_key_path,
            "-r",
            local_app_path.rstrip("/"),
            f"ubuntu@{public_ip}:{remote_app_path}",
        ],
        "Copy application files to remote instance"
    )

   # -----------------------------------------
    # Install dependencies
    # -----------------------------------------
    install_cmd = (
        "sudo apt-get update -y && "
        "sudo apt-get install -y python3 python3-pip && "
        "cd {app_path}/app_src && "
        "pip3 install --user -r requirements.txt"
    ).format(app_path=remote_app_path)

    run_cmd(
        ssh_base + [install_cmd],
        "Install Python and dependencies"
    )


    # -----------------------------------------
    # Copy systemd service file
    # -----------------------------------------
    run_cmd(
        [
            "scp",
            "-o", "StrictHostKeyChecking=no",
            "-i", ssh_key_path,
            "app.service",
            f"ubuntu@{public_ip}:/home/ubuntu/app/"
        ],
        "Copy systemd service file"
    )


    # -----------------------------------------
    # Enable and start the systemd service
    # -----------------------------------------
    enable_service_cmd = (
        "sudo mv /home/ubuntu/app/app.service /etc/systemd/system/app.service && "
        "sudo systemctl daemon-reload && "
        "sudo systemctl enable app.service && "
        "sudo systemctl restart app.service"
    )

    run_cmd(
        ssh_base + [enable_service_cmd],
        "Enable and start systemd service"
    )

    print("\n[SUCCESS] Deployment complete!")
    print(f"Instance ID: {instance_id}")
    print(f"Public DNS: {public_dns}")
    print(f"Public IP:  {public_ip}")
    print(f"Search engine URL: http://{public_dns}:{exposed_port}/ (or use IP instead of DNS)")


if __name__ == "__main__":
    main()
