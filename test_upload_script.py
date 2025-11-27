#!/usr/bin/env python3
"""Test file upload functionality"""

import requests
import json

# Upload test file
with open('test_upload.txt', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:8001/upload', files=files)

print("Upload Response:")
print(json.dumps(response.json(), indent=2))

# Get statistics
stats_response = requests.get('http://localhost:8001/stats')
print("\nSystem Statistics After Upload:")
print(json.dumps(stats_response.json(), indent=2))

# List nodes
list_response = requests.get('http://localhost:8001/nodes')
print("\nNodes Created:")
print(json.dumps(list_response.json(), indent=2))
