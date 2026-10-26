import getpass
import json
from pathlib import Path
from minio import MinioAdmin
from minio.credentials import StaticProvider

policy_path = Path(__file__).with_name("student-files-policy.json")

with policy_path.open("r", encoding="utf-8") as file:
    policy = json.load(file)

password = getpass.getpass("Enter MinIO administrator password: ")

admin = MinioAdmin(
    endpoint="127.0.0.1:9000",
    credentials=StaticProvider("studentadmin", password),
    secure=False,
)

policy_name = "cloudvault-student-files"

print("Uploading the CloudVault policy...")
admin.policy_add(policy_name, policy_file=str(policy_path))

print("Assigning the policy to cloudappuser...")
admin.attach_policy(policies=[policy_name], user="cloudappuser")

print("Policy applied and assigned successfully.")