#!/usr/bin/env python3
"""
Comprehensive Retrieval System Validation Test
Tests all three retrieval modes: Local, Global, and Hybrid
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8001"

def test_local_retrieval() -> bool:
    """Test LOCAL retrieval (vector-only semantic search)"""
    print("\n" + "="*70)
    print("TEST 1: LOCAL RETRIEVAL (Vector-only semantic search)")
    print("="*70)
    
    test_cases = [
        {"query_text": "SpaceX rockets", "top_k": 3},
        {"query_text": "electric vehicles", "top_k": 2},
        {"query_text": "California", "top_k": 2},
    ]
    
    success = True
    for i, query in enumerate(test_cases, 1):
        try:
            response = requests.post(
                f"{BASE_URL}/retrieve/local",
                json=query,
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                print(f"\nQuery {i}: '{query['query_text']}'")
                print(f"  Status: {response.status_code}")
                print(f"  Mode: {data['mode']}")
                print(f"  Results: {len(data['results'])} found")
                print(f"  Confidence: {data['confidence']:.4f}")
                print(f"  Latency: {data['latency_ms']}ms")
                if data['results']:
                    print(f"  Top result: {data['results'][0]['text'][:60]}...")
            else:
                print(f"FAILED - Status {response.status_code}")
                success = False
        except Exception as e:
            print(f"ERROR: {e}")
            success = False
    
    return success

def test_global_retrieval() -> bool:
    """Test GLOBAL retrieval (graph-only entity search)"""
    print("\n" + "="*70)
    print("TEST 2: GLOBAL RETRIEVAL (Graph-only entity search)")
    print("="*70)
    
    test_cases = [
        {"query_text": "Elon Musk", "depth": 2},
        {"query_text": "Tesla CEO", "depth": 1},
        {"query_text": "SpaceX founder", "depth": 2},
    ]
    
    success = True
    for i, query in enumerate(test_cases, 1):
        try:
            response = requests.post(
                f"{BASE_URL}/retrieve/global",
                json=query,
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                print(f"\nQuery {i}: '{query['query_text']}'")
                print(f"  Status: {response.status_code}")
                print(f"  Mode: {data['mode']}")
                print(f"  Entities Found: {data['entities_found']}")
                print(f"  Reachable Nodes: {data['reachable_nodes']}")
                print(f"  Relationships: {len(data['relationships'])}")
                print(f"  Latency: {data['latency_ms']}ms")
            else:
                print(f"FAILED - Status {response.status_code}")
                success = False
        except Exception as e:
            print(f"ERROR: {e}")
            success = False
    
    return success

def test_hybrid_retrieval() -> bool:
    """Test HYBRID retrieval (vector + graph combined) - BEST MODE"""
    print("\n" + "="*70)
    print("TEST 3: HYBRID RETRIEVAL (Vector + Graph combined) **BEST MODE**")
    print("="*70)
    
    test_cases = [
        {"query_text": "Elon Musk founder", "top_k": 3},
        {"query_text": "SpaceX rockets space", "top_k": 3},
        {"query_text": "Tesla electric manufacturing", "top_k": 2},
    ]
    
    success = True
    for i, query in enumerate(test_cases, 1):
        try:
            response = requests.post(
                f"{BASE_URL}/retrieve/hybrid",
                json=query,
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                print(f"\nQuery {i}: '{query['query_text']}'")
                print(f"  Status: {response.status_code}")
                print(f"  Mode: {data['mode']}")
                print(f"  Results: {len(data['results'])} found")
                print(f"  Total Candidates: {data['total_candidates']}")
                print(f"  Confidence: {data['confidence']}")
                print(f"  Vector Weight: {data['vector_weight']} | Graph Weight: {data['graph_weight']}")
                print(f"  Latency: {data['latency_ms']}ms")
                
                if data['results']:
                    top = data['results'][0]
                    print(f"\n  Top Result: {top['text'][:60]}...")
                    print(f"    Vector Score: {top['vector_score']}")
                    print(f"    Graph Score: {top['graph_score']}")
                    print(f"    Hybrid Score: {top['hybrid_score']}")
            else:
                print(f"FAILED - Status {response.status_code}")
                success = False
        except Exception as e:
            print(f"ERROR: {e}")
            success = False
    
    return success

def test_system_stats() -> bool:
    """Test system statistics endpoint"""
    print("\n" + "="*70)
    print("TEST 4: SYSTEM STATISTICS")
    print("="*70)
    
    try:
        response = requests.get(f"{BASE_URL}/stats", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"\nStatus: {response.status_code}")
            print(f"Total Nodes: {data['total_nodes']}")
            print(f"Total Edges: {data['total_edges']}")
            print(f"Vector DB Size: {data['vector_db_size']}")
            print(f"Graph DB Size: {data['graph_db_size']}")
            print(f"Vector Dimension: {data['vector_dimension']}")
            print(f"Timestamp: {data['timestamp']}")
            return True
        else:
            print(f"FAILED - Status {response.status_code}")
            return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def main():
    """Run all tests"""
    print("\n")
    print("*" * 70)
    print("COMPREHENSIVE RETRIEVAL SYSTEM VALIDATION TEST")
    print("*" * 70)
    
    # Wait for server to be ready
    max_retries = 10
    for attempt in range(max_retries):
        try:
            requests.get(f"{BASE_URL}/stats", timeout=2)
            break
        except:
            if attempt < max_retries - 1:
                time.sleep(0.5)
    
    results = {
        "Local Retrieval": test_local_retrieval(),
        "Global Retrieval": test_global_retrieval(),
        "Hybrid Retrieval": test_hybrid_retrieval(),
        "System Stats": test_system_stats(),
    }
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"{test_name:.<50} {status}")
        if not passed:
            all_passed = False
    
    print("="*70)
    if all_passed:
        print("ALL TESTS PASSED! Retrieval system is working correctly.")
        return 0
    else:
        print("SOME TESTS FAILED! Please review the output above.")
        return 1

if __name__ == "__main__":
    exit(main())
