#!/usr/bin/env python3
"""Test retrieval endpoints"""

import requests
import json
import time

BASE_URL = "http://localhost:8001"

print("\n" + "="*80)
print("TESTING RETRIEVAL SYSTEM - ALL 3 MODES")
print("="*80)

# First populate with demo data
print("\n📥 Populating with demo data...")
response = requests.post(f"{BASE_URL}/demo/populate")
print(f"✓ Demo data created: {response.json()}")

time.sleep(1)

# Test queries
test_queries = [
    "Who founded SpaceX?",
    "What companies are related to Elon Musk?",
    "Where is Google headquartered?",
    "Tell me about Tesla"
]

for query in test_queries:
    print(f"\n\n{'='*80}")
    print(f"QUERY: {query}")
    print('='*80)
    
    # 1. LOCAL (VECTOR ONLY)
    print(f"\n1️⃣  LOCAL SEARCH (Vector-only)")
    print("-"*80)
    try:
        response = requests.post(
            f"{BASE_URL}/retrieve/local",
            json={"query_text": query, "top_k": 3}
        )
        result = response.json()
        print(f"Mode: {result.get('mode')}")
        print(f"Confidence: {result.get('confidence', 0):.2%}")
        print(f"Latency: {result.get('latency_ms')}ms")
        print(f"Results found: {result.get('total_found', 0)}")
        
        for i, res in enumerate(result.get('results', []), 1):
            print(f"\n  {i}. {res['text'][:70]}")
            print(f"     Score: {res['similarity_score']:.4f}")
    except Exception as e:
        print(f"Error: {e}")
    
    # 2. GLOBAL (GRAPH ONLY)
    print(f"\n2️⃣  GLOBAL SEARCH (Graph-only)")
    print("-"*80)
    try:
        response = requests.post(
            f"{BASE_URL}/retrieve/global",
            json={"query_text": query, "depth": 2}
        )
        result = response.json()
        print(f"Mode: {result.get('mode')}")
        print(f"Entities found: {result.get('entities_found', 0)}")
        print(f"Reachable nodes: {result.get('reachable_nodes', 0)}")
        print(f"Relationships: {len(result.get('relationships', []))}")
        print(f"Latency: {result.get('latency_ms')}ms")
        
        for i, entity in enumerate(result.get('matching_entities', []), 1):
            print(f"\n  {i}. {entity['text'][:70]}")
            print(f"     Relevance: {entity['relevance']:.4f}")
        
        for i, rel in enumerate(result.get('relationships', [])[:3], 1):
            print(f"  Rel: {rel['source']} --[{rel['type']}]--> {rel['target']}")
    except Exception as e:
        print(f"Error: {e}")
    
    # 3. HYBRID (BEST)
    print(f"\n3️⃣  HYBRID SEARCH (Vector + Graph) ⭐")
    print("-"*80)
    try:
        response = requests.post(
            f"{BASE_URL}/retrieve/hybrid",
            json={
                "query_text": query,
                "top_k": 5,
                "vector_weight": 0.6,
                "graph_weight": 0.4,
                "do_rerank": True
            }
        )
        result = response.json()
        print(f"Mode: {result.get('mode')}")
        print(f"Confidence: {result.get('confidence')}")
        print(f"Results: {len(result.get('results', []))}")
        print(f"Vector weight: {result.get('vector_weight')}")
        print(f"Graph weight: {result.get('graph_weight')}")
        print(f"Latency: {result.get('latency_ms')}ms")
        
        for i, res in enumerate(result.get('results', []), 1):
            print(f"\n  {i}. {res['text'][:70]}")
            print(f"     Hybrid: {res['hybrid_score']} | Vector: {res['vector_score']} | Graph: {res['graph_score']}")
        
        print(f"\n  Relationships found: {len(result.get('relationships', []))}")
        for rel in result.get('relationships', [])[:2]:
            print(f"    - {rel['source']} --[{rel['type']}]--> {rel['target']}")
    except Exception as e:
        print(f"Error: {e}")

print(f"\n\n{'='*80}")
print("✅ RETRIEVAL SYSTEM TEST COMPLETE")
print('='*80)
