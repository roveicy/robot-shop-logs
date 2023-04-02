from datetime import datetime
from elasticsearch import Elasticsearch
import os
import time
import subprocess

# Define Elasticsearch connection details
es = Elasticsearch(["http://10.152.183.203:32258"])

# Define namespaces and container names
namespaces = ["robot-shop", "chaos-testing"]
containers = {
    "robot-shop": [
        "load-5d6668d47c-9dpp8",
        "payment-756c8bc778-xlc7w",
        "mongodb-7b454c7f5-dggx6",
        "user-69bbb794f8-ncvv9",
        "web-5bb5686896-vgdhq"
    ],
    "chaos-testing": [
        "chaos-daemon-kjdnm"
    ]
}

# Define Elasticsearch index details
index_prefix = "kubernetes-logs"
index_format = f"{index_prefix}-%Y.%m.%d"
index = f"{index_prefix}-{datetime.utcnow().strftime('%Y.%m.%d')}"

# Create Elasticsearch index if it doesn't exist
if not es.indices.exists(index=index):
    es.indices.create(index=index)

# Loop forever
while True:
    # Get current timestamp
    timestamp = datetime.utcnow().isoformat()
    # Loop through namespaces and containers
    for namespace in namespaces:
        for container in containers[namespace]:
            # Construct command to extract logs
            command = f"kubectl logs -n {namespace} {container}"
            # Use subprocess to run command and capture output
            output = subprocess.check_output(command, shell=True)
            # Construct document for Elasticsearch
            document = {
                "@timestamp": timestamp,
                "namespace": namespace,
                "container": container,
                "log": output.decode()
            }
            # Index document in Elasticsearch
            es.index(index=index, body=document)
            print(f"Indexed log for {namespace}/{container} at {timestamp}")
    # Wait 1 minute before repeating loop
    time.sleep(60)
