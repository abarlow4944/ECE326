#!/usr/bin/env python3
import json
import os
import sys
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
            print("[ERROR] Failed to install boto3 automatically.")
            print("        Please install it manually: pip install boto3")
            print("Details:", e)
            sys.exit(1)

ensure_boto3()
import boto3


def load_config(config_path):
    with open(config_path, "r") as f:
        return json.load(f)


def main():
    if len(sys.argv) != 3:
        print("Usage: python terminate.py <aws_config.json> <instance_id>")
        sys.exit(1)

    config_path = sys.argv[1]
    instance_id = sys.argv[2]

    if not os.path.exists(config_path):
        print(f"[ERROR] Config file '{config_path}' not found.")
        sys.exit(1)

    config = load_config(config_path)

    aws_access_key_id = config.get("aws_access_key_id")
    aws_secret_access_key = config.get("aws_secret_access_key")
    region_name = config.get("region_name", "us-east-1")

    if not all([aws_access_key_id, aws_secret_access_key]):
        print("[ERROR] Missing required AWS credentials in config file.")
        sys.exit(1)

    ec2_client = boto3.client(
        "ec2",
        region_name=region_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )

    print(f"[INFO] Terminating instance {instance_id}...")
    try:
        response = ec2_client.terminate_instances(InstanceIds=[instance_id])
        current_state = response["TerminatingInstances"][0]["CurrentState"]["Name"]
        print(f"[INFO] Terminate request sent. Current state: {current_state}")
        print("[SUCCESS] Termination script completed successfully.")
    except Exception as e:
        print("[ERROR] Failed to terminate instance.")
        print("Details:", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
