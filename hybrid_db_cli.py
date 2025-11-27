"""
CLI Tool for Vector + Graph Hybrid Database
Demonstrates all core operations: CRUD, search, and hybrid retrieval
"""

import asyncio
import requests
import json
from typing import Optional
from tabulate import tabulate
from datetime import datetime

BASE_URL = "http://localhost:8000"

class HybridDBCLI:
    """Interactive CLI for Hybrid Database"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def health_check(self):
        """Check if API is running"""
        try:
            response = self.session.get(f"{BASE_URL}/health")
            response.raise_for_status()
            return True, response.json()
        except Exception as e:
            return False, str(e)
    
    # ===== NODE OPERATIONS =====
    
    def create_node(self, text: str, metadata: Optional[dict] = None):
        """Create a new node"""
        payload = {
            "text": text,
            "metadata": metadata or {"created_by": "cli"}
        }
        response = self.session.post(f"{BASE_URL}/nodes", json=payload)
        return response.json()
    
    def get_node(self, node_id: str):
        """Retrieve a node by ID"""
        response = self.session.get(f"{BASE_URL}/nodes/{node_id}")
        return response.json()
    
    def list_nodes(self, limit: int = 10):
        """List all nodes"""
        response = self.session.get(f"{BASE_URL}/nodes", params={"limit": limit})
        return response.json()
    
    # ===== EDGE OPERATIONS =====
    
    def create_edge(self, source_id: str, target_id: str, rel_type: str, weight: float = 1.0):
        """Create a relationship between two nodes"""
        payload = {
            "source_id": source_id,
            "target_id": target_id,
            "relationship_type": rel_type,
            "weight": weight
        }
        response = self.session.post(f"{BASE_URL}/edges", json=payload)
        return response.json()
    
    # ===== SEARCH OPERATIONS =====
    
    def vector_search(self, query: str, top_k: int = 5):
        """Vector similarity search"""
        payload = {"query_text": query, "top_k": top_k}
        response = self.session.post(f"{BASE_URL}/search/vector", json=payload)
        return response.json()
    
    def graph_traversal(self, start_id: str, depth: int = 2):
        """Graph traversal from a node"""
        response = self.session.get(
            f"{BASE_URL}/search/graph",
            params={"start_id": start_id, "depth": depth}
        )
        return response.json()
    
    def hybrid_search(self, query: str, vector_weight: float = 0.6, 
                     graph_weight: float = 0.4, top_k: int = 5):
        """Hybrid search combining vector and graph scores"""
        payload = {
            "query_text": query,
            "vector_weight": vector_weight,
            "graph_weight": graph_weight,
            "top_k": top_k
        }
        response = self.session.post(f"{BASE_URL}/search/hybrid", json=payload)
        return response.json()
    
    # ===== SYSTEM OPERATIONS =====
    
    def get_stats(self):
        """Get system statistics"""
        response = self.session.get(f"{BASE_URL}/stats")
        return response.json()
    
    def populate_demo(self):
        """Load demo data"""
        response = self.session.post(f"{BASE_URL}/demo/populate")
        return response.json()

# ============================================================================
# DISPLAY UTILITIES
# ============================================================================

def print_header(title):
    """Print formatted header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def print_success(msg):
    """Print success message"""
    print(f"✓ {msg}")

def print_error(msg):
    """Print error message"""
    print(f"✗ {msg}")

# ============================================================================
# INTERACTIVE DEMO
# ============================================================================

def run_interactive_demo():
    """Run interactive demo"""
    cli = HybridDBCLI()
    
    print_header("HYBRID DATABASE CLI - INTERACTIVE DEMO")
    
    # Check health
    print("1. Checking API health...")
    is_healthy, health_info = cli.health_check()
    
    if not is_healthy:
        print_error(f"API not running: {health_info}")
        print("\nStart the API with: python hybrid_db_api.py")
        return
    
    print_success("API is running")
    print(json.dumps(health_info, indent=2))
    
    # Populate demo data
    print("\n2. Loading demo data...")
    try:
        demo_result = cli.populate_demo()
        print_success(f"Created {demo_result['nodes_created']} nodes and {demo_result['edges_created']} edges")
    except Exception as e:
        print_error(f"Failed to load demo data: {e}")
        return
    
    # List nodes
    print("\n3. Listing all nodes...")
    nodes_result = cli.list_nodes()
    print_success(f"Total nodes: {nodes_result['total']}")
    
    if nodes_result['nodes']:
        table_data = []
        for node in nodes_result['nodes']:
            table_data.append([
                node['id'],
                node['text'][:50],
                node['embedding_dim']
            ])
        print(tabulate(table_data, headers=['Node ID', 'Text', 'Dim'], tablefmt='grid'))
    
    # Get stats
    print("\n4. System Statistics")
    stats = cli.get_stats()
    print(f"   Total Nodes: {stats['total_nodes']}")
    print(f"   Total Edges: {stats['total_edges']}")
    print(f"   Vector Dimension: {stats['vector_dimension']}")
    
    # Vector search
    print("\n5. VECTOR SEARCH (Semantic Similarity)")
    print("   Query: 'space exploration and rockets'")
    vector_results = cli.vector_search("space exploration and rockets", top_k=3)
    
    if vector_results['results']:
        table_data = []
        for result in vector_results['results']:
            table_data.append([
                result['node_id'],
                result['text'][:40],
                f"{result['score']:.4f}"
            ])
        print(tabulate(table_data, headers=['Node ID', 'Text', 'Score'], tablefmt='grid'))
    
    # Graph traversal
    print("\n6. GRAPH TRAVERSAL (Relationship Reasoning)")
    print("   Starting from: node-0 (Elon Musk founded SpaceX)")
    print("   Depth: 2 hops")
    
    try:
        graph_results = cli.graph_traversal("node-0", depth=2)
        if graph_results['reachable_nodes']:
            table_data = []
            for node in graph_results['reachable_nodes']:
                table_data.append([
                    node['node_id'],
                    node['text'][:40],
                    node['depth'],
                    node['edges_from_start']
                ])
            print(tabulate(table_data, headers=['Node ID', 'Text', 'Depth', 'Edges'], tablefmt='grid'))
        else:
            print("   (No reachable nodes)")
    except Exception as e:
        print(f"   Graph traversal not available: {e}")
    
    # Hybrid search
    print("\n7. HYBRID SEARCH (CORE FEATURE)")
    print("   Combining vector similarity (60%) + graph closeness (40%)")
    print("   Query: 'CEO technology companies'")
    
    hybrid_results = cli.hybrid_search(
        "CEO technology companies",
        vector_weight=0.6,
        graph_weight=0.4,
        top_k=5
    )
    
    if hybrid_results['results']:
        table_data = []
        for result in hybrid_results['results']:
            table_data.append([
                result['node_id'],
                result['text'][:35],
                f"{result['vector_score']:.3f}",
                f"{result['graph_score']:.3f}",
                f"{result['hybrid_score']:.3f}",
                result['source']
            ])
        print(tabulate(
            table_data,
            headers=['ID', 'Text', 'Vector', 'Graph', 'Hybrid', 'Source'],
            tablefmt='grid'
        ))
    
    # Comparison: Why hybrid is better
    print("\n8. WHY HYBRID IS BETTER")
    print("   Vector-only: Finds semantically similar content (good for meaning)")
    print("   Graph-only: Finds connected nodes (good for relationships)")
    print("   Hybrid: Combines both (best for relevance + reasoning)")
    
    print("\n" + "="*70)
    print("Demo complete! Try the API docs at: http://localhost:8000/docs")
    print("="*70 + "\n")

# ============================================================================
# PERFORMANCE BENCHMARK
# ============================================================================

def run_performance_benchmark():
    """Benchmark query performance"""
    cli = HybridDBCLI()
    import time
    
    print_header("PERFORMANCE BENCHMARK")
    
    is_healthy, _ = cli.health_check()
    if not is_healthy:
        print_error("API not running")
        return
    
    # Ensure demo data exists
    try:
        cli.populate_demo()
    except:
        pass  # Data might already exist
    
    benchmarks = {
        "Vector Search": lambda: cli.vector_search("technology", top_k=5),
        "Graph Traversal": lambda: cli.graph_traversal("node-0", depth=2),
        "Hybrid Search": lambda: cli.hybrid_search("innovation", top_k=5),
    }
    
    results = []
    
    for name, func in benchmarks.items():
        times = []
        for _ in range(5):
            start = time.time()
            func()
            end = time.time()
            times.append((end - start) * 1000)  # Convert to ms
        
        avg_time = sum(times) / len(times)
        results.append([name, f"{avg_time:.2f} ms", f"{1000/avg_time:.1f} ops/sec"])
    
    print(tabulate(results, headers=['Operation', 'Avg Time', 'Throughput'], tablefmt='grid'))
    print()

# ============================================================================
# HYBRID SEARCH EFFECTIVENESS DEMO
# ============================================================================

def demonstrate_hybrid_advantage():
    """Show why hybrid search is better than vector-only or graph-only"""
    cli = HybridDBCLI()
    
    print_header("HYBRID SEARCH EFFECTIVENESS DEMONSTRATION")
    
    is_healthy, _ = cli.health_check()
    if not is_healthy:
        print_error("API not running")
        return
    
    # Ensure demo data
    try:
        cli.populate_demo()
    except:
        pass
    
    query = "founder CEO companies"
    
    print(f"Query: '{query}'\n")
    
    # Vector-only
    print("VECTOR-ONLY SEARCH (Semantic Similarity)")
    print("-" * 70)
    vector_res = cli.vector_search(query, top_k=3)
    if vector_res['results']:
        for i, r in enumerate(vector_res['results'], 1):
            print(f"{i}. {r['node_id']}: {r['text']}")
            print(f"   Score: {r['score']:.4f}\n")
    
    # Hybrid
    print("\nHYBRID SEARCH (Semantic + Relationship)")
    print("-" * 70)
    hybrid_res = cli.hybrid_search(query, top_k=3)
    if hybrid_res['results']:
        for i, r in enumerate(hybrid_res['results'], 1):
            print(f"{i}. {r['node_id']}: {r['text']}")
            print(f"   Vector: {r['vector_score']:.4f} | Graph: {r['graph_score']:.4f} | Hybrid: {r['hybrid_score']:.4f}")
            print(f"   Source: {r['source']}\n")
    
    print("ANALYSIS:")
    print("-" * 70)
    print("• Vector-only focuses on semantic similarity to keywords")
    print("• Hybrid also considers graph relationships (connectedness)")
    print("• Results can differ based on which is more important")
    print("• Hybrid scoring: vector_weight=0.6, graph_weight=0.4 (adjustable)")
    print()

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point"""
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "demo":
            run_interactive_demo()
        elif command == "benchmark":
            run_performance_benchmark()
        elif command == "hybrid-demo":
            demonstrate_hybrid_advantage()
        else:
            print(f"Unknown command: {command}")
            print("Available commands:")
            print("  python hybrid_db_cli.py demo           - Run interactive demo")
            print("  python hybrid_db_cli.py benchmark      - Performance benchmark")
            print("  python hybrid_db_cli.py hybrid-demo    - Show hybrid advantage")
    else:
        run_interactive_demo()

if __name__ == "__main__":
    main()
