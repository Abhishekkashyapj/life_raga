#!/usr/bin/env python
"""Quick test script for Hybrid RAG system"""
import requests
import json

print("[*] Testing Hybrid RAG Backend")
print("=" * 60)

# Test upload
print("\n[1] Testing file upload...")
try:
    with open('test_document.txt', 'rb') as f:
        response = requests.post('http://localhost:8001/upload', files={'file': f})
    
    if response.status_code == 200:
        print("[+] Upload successful!")
        data = response.json()
        print(f"    Nodes created: {data.get('nodes_created')}")
    else:
        print(f"[-] Upload failed: {response.status_code}")
except Exception as e:
    print(f"[-] Error: {e}")

# Test hybrid search
print("\n[2] Testing hybrid search...")
try:
    query_data = {
        'query_text': 'What is machine learning?',
        'top_k': 5
    }
    response = requests.post('http://localhost:8001/retrieve/hybrid', json=query_data)
    
    if response.status_code == 200:
        print("[+] Search successful!")
        data = response.json()
        print(f"    Results: {len(data.get('results', []))}")
        print(json.dumps(data, indent=2)[:300])
    else:
        print(f"[-] Search failed: {response.status_code}")
        print(f"    {response.text}")
except Exception as e:
    print(f"[-] Error: {e}")

# Test stats
print("\n[3] Checking system stats...")
try:
    response = requests.get('http://localhost:8001/stats')
    if response.status_code == 200:
        stats = response.json()
        print("[+] System stats:")
        print(f"    Total nodes: {stats.get('total_nodes')}")
        print(f"    Total edges: {stats.get('total_edges')}")
        print(f"    Vector dimension: {stats.get('vector_dimension')}")
except Exception as e:
    print(f"[-] Error: {e}")

print("\n" + "=" * 60)
print("[+] Testing complete!")
