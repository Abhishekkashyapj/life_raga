#!/usr/bin/env python3
"""
Hybrid Database Retrieval System
Supports 3 modes: Local (Vector), Global (Graph), Hybrid (Both)
"""

import json
import math
import random
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass

# ============================================================================
# DATA MODELS FOR RETRIEVAL
# ============================================================================

@dataclass
class QueryParam:
    """Parameters for retrieval queries"""
    mode: str = "hybrid"  # local, global, or hybrid
    query_text: str = ""
    top_k: int = 5
    vector_weight: float = 0.6
    graph_weight: float = 0.4
    do_rerank: bool = False

@dataclass
class RetrievalResult:
    """Result from a retrieval query"""
    answer: str
    mode: str
    source_nodes: List[Dict[str, Any]]
    confidence: float
    latency_ms: float
    metadata: Dict[str, Any]

# ============================================================================
# RETRIEVAL ENGINE
# ============================================================================

class HybridRetrievalEngine:
    """
    Retrieval engine supporting:
    - Local (Vector-only) search
    - Global (Graph-only) search  
    - Hybrid (Vector + Graph) search
    """
    
    def __init__(self, vector_store_path: str, graph_store_path: str):
        self.vector_store_path = vector_store_path
        self.graph_store_path = graph_store_path
        self.stats = {
            "total_queries": 0,
            "local_queries": 0,
            "global_queries": 0,
            "hybrid_queries": 0,
            "avg_latency_ms": 0.0
        }
    
    # ====================================================================
    # VECTOR SEARCH (LOCAL MODE)
    # ====================================================================
    
    def local_search(self, query_text: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Vector-only search using ChromaDB-like embeddings.
        Pure semantic similarity.
        """
        import time
        start_time = time.time()
        
        try:
            with open(self.vector_store_path, 'r') as f:
                data = json.load(f)
            
            # Generate query embedding (mock - would use real embeddings)
            query_embedding = [random.random() for _ in range(768)]
            
            # Calculate similarity scores
            results = []
            for node_id, node_data in data["nodes"].items():
                similarity = self._cosine_similarity(
                    query_embedding, 
                    node_data["embedding"]
                )
                results.append({
                    "node_id": node_id,
                    "text": node_data["text"],
                    "similarity_score": similarity,
                    "source": "vector_db",
                    "metadata": node_data["metadata"]
                })
            
            # Sort by similarity and get top_k
            results.sort(key=lambda x: x["similarity_score"], reverse=True)
            top_results = results[:top_k]
            
            # Calculate confidence from scores
            confidence = sum(r["similarity_score"] for r in top_results) / len(top_results) if top_results else 0
            
            latency = (time.time() - start_time) * 1000
            
            return {
                "mode": "local",
                "query": query_text,
                "results": top_results,
                "total_found": len(results),
                "confidence": confidence,
                "latency_ms": latency
            }
        
        except Exception as e:
            return {
                "mode": "local",
                "error": str(e),
                "results": []
            }
    
    # ====================================================================
    # GRAPH SEARCH (GLOBAL MODE)
    # ====================================================================
    
    def global_search(self, query_text: str, depth: int = 2) -> Dict[str, Any]:
        """
        Graph-only search using Neo4j-like relationships.
        Entity-based reasoning with graph traversal.
        """
        import time
        start_time = time.time()
        
        try:
            with open(self.graph_store_path, 'r') as f:
                graph_data = json.load(f)
            
            with open(self.vector_store_path, 'r') as f:
                vector_data = json.load(f)
            
            # Find entities mentioned in query
            query_tokens = query_text.lower().split()
            matching_nodes = []
            
            for node_id, node_data in vector_data["nodes"].items():
                node_text_lower = node_data["text"].lower()
                # Simple keyword matching (would use NLP in production)
                matches = sum(1 for token in query_tokens if token in node_text_lower)
                if matches > 0:
                    matching_nodes.append({
                        "node_id": node_id,
                        "text": node_data["text"],
                        "relevance": matches / len(query_tokens),
                        "degree": self._get_node_degree(node_id, graph_data)
                    })
            
            # Traverse graph from matching nodes
            reachable_nodes = self._graph_traversal(matching_nodes, graph_data, vector_data, depth)
            
            # Rank by relevance and connectivity
            for node in reachable_nodes:
                node["score"] = node.get("relevance", 0.5) + (node.get("degree", 0) * 0.1)
            
            reachable_nodes.sort(key=lambda x: x["score"], reverse=True)
            
            # Extract relationships
            relationships = []
            for edge in graph_data["edges"]:
                if any(n["node_id"] == edge["source"] for n in reachable_nodes[:5]):
                    relationships.append({
                        "source": edge["source"],
                        "target": edge["target"],
                        "type": edge["type"],
                        "weight": edge["weight"]
                    })
            
            latency = (time.time() - start_time) * 1000
            confidence = sum(n["score"] for n in reachable_nodes[:3]) / 3 if reachable_nodes else 0
            
            return {
                "mode": "global",
                "query": query_text,
                "entities": reachable_nodes[:5],
                "relationships": relationships,
                "total_reachable": len(reachable_nodes),
                "confidence": min(confidence, 1.0),
                "latency_ms": latency
            }
        
        except Exception as e:
            return {
                "mode": "global",
                "error": str(e),
                "entities": [],
                "relationships": []
            }
    
    # ====================================================================
    # HYBRID SEARCH (BEST MODE)
    # ====================================================================
    
    def hybrid_search(
        self, 
        query_text: str, 
        top_k: int = 5,
        vector_weight: float = 0.6,
        graph_weight: float = 0.4,
        do_rerank: bool = False
    ) -> Dict[str, Any]:
        """
        Hybrid search combining vector and graph retrieval.
        Fuses both signals for best accuracy.
        """
        import time
        start_time = time.time()
        
        try:
            # 1. Get vector search results
            vector_results = self.local_search(query_text, top_k)
            
            # 2. Get graph search results
            graph_results = self.global_search(query_text, depth=2)
            
            # 3. Combine and score
            combined_scores = {}
            
            # Add vector scores
            for result in vector_results.get("results", []):
                node_id = result["node_id"]
                combined_scores[node_id] = {
                    "text": result["text"],
                    "vector_score": result["similarity_score"],
                    "graph_score": 0.0,
                    "source": "vector",
                    "metadata": result.get("metadata", {})
                }
            
            # Add/merge graph scores
            for entity in graph_results.get("entities", []):
                node_id = entity["node_id"]
                if node_id not in combined_scores:
                    combined_scores[node_id] = {
                        "text": entity["text"],
                        "vector_score": 0.0,
                        "source": "graph",
                        "metadata": {}
                    }
                combined_scores[node_id]["graph_score"] = entity["score"]
            
            # 4. Calculate hybrid scores
            hybrid_results = []
            for node_id, scores in combined_scores.items():
                hybrid_score = (
                    scores["vector_score"] * vector_weight +
                    scores["graph_score"] * graph_weight
                )
                hybrid_results.append({
                    "node_id": node_id,
                    "text": scores["text"],
                    "vector_score": scores["vector_score"],
                    "graph_score": scores["graph_score"],
                    "hybrid_score": hybrid_score,
                    "source": "hybrid",
                    "metadata": scores.get("metadata", {})
                })
            
            # 5. Sort and rerank if requested
            hybrid_results.sort(key=lambda x: x["hybrid_score"], reverse=True)
            
            if do_rerank:
                hybrid_results = self._rerank_results(hybrid_results, query_text)
            
            # Get top_k
            final_results = hybrid_results[:top_k]
            
            # Calculate confidence
            confidence = (
                sum(r["hybrid_score"] for r in final_results) / len(final_results)
                if final_results else 0
            )
            
            latency = (time.time() - start_time) * 1000
            
            return {
                "mode": "hybrid",
                "query": query_text,
                "results": final_results,
                "total_candidates": len(hybrid_results),
                "vector_weight": vector_weight,
                "graph_weight": graph_weight,
                "confidence": confidence,
                "latency_ms": latency,
                "relationships": graph_results.get("relationships", [])
            }
        
        except Exception as e:
            return {
                "mode": "hybrid",
                "error": str(e),
                "results": []
            }
    
    # ====================================================================
    # HELPER METHODS
    # ====================================================================
    
    @staticmethod
    def _cosine_similarity(v1: List[float], v2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        dot_product = sum(a * b for a, b in zip(v1, v2))
        magnitude1 = math.sqrt(sum(a ** 2 for a in v1))
        magnitude2 = math.sqrt(sum(b ** 2 for b in v2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def _get_node_degree(self, node_id: str, graph_data: Dict) -> int:
        """Get connectivity degree of a node in the graph"""
        degree = 0
        for edge in graph_data["edges"]:
            if edge["source"] == node_id or edge["target"] == node_id:
                degree += 1
        return degree
    
    def _graph_traversal(
        self, 
        start_nodes: List[Dict], 
        graph_data: Dict, 
        vector_data: Dict,
        depth: int
    ) -> List[Dict[str, Any]]:
        """Traverse graph from start nodes up to specified depth"""
        visited = set()
        reachable = []
        
        def traverse(node_id: str, current_depth: int):
            if current_depth > depth or node_id in visited:
                return
            
            visited.add(node_id)
            
            # Add this node
            if node_id in vector_data["nodes"]:
                node_data = vector_data["nodes"][node_id]
                reachable.append({
                    "node_id": node_id,
                    "text": node_data["text"],
                    "depth": current_depth,
                    "relevance": 1.0 / (current_depth + 1),
                    "degree": self._get_node_degree(node_id, graph_data)
                })
            
            # Traverse to neighbors
            for edge in graph_data["edges"]:
                if edge["source"] == node_id:
                    traverse(edge["target"], current_depth + 1)
        
        for start_node in start_nodes:
            traverse(start_node["node_id"], 0)
        
        return reachable
    
    def _rerank_results(
        self, 
        results: List[Dict], 
        query_text: str
    ) -> List[Dict]:
        """
        Rerank results using semantic relevance.
        (In production, would use BAAI bge-reranker)
        """
        query_tokens = set(query_text.lower().split())
        
        for result in results:
            text_tokens = set(result["text"].lower().split())
            overlap = len(query_tokens & text_tokens) / len(query_tokens | text_tokens)
            result["rerank_score"] = result["hybrid_score"] * (0.7 + 0.3 * overlap)
        
        results.sort(key=lambda x: x["rerank_score"], reverse=True)
        return results
    
    def update_stats(self, mode: str, latency: float):
        """Update retrieval statistics"""
        self.stats["total_queries"] += 1
        self.stats[f"{mode}_queries"] += 1
        
        # Update average latency
        total_latency = self.stats["avg_latency_ms"] * (self.stats["total_queries"] - 1)
        self.stats["avg_latency_ms"] = (total_latency + latency) / self.stats["total_queries"]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get retrieval statistics"""
        return {
            "total_queries": self.stats["total_queries"],
            "local_queries": self.stats["local_queries"],
            "global_queries": self.stats["global_queries"],
            "hybrid_queries": self.stats["hybrid_queries"],
            "avg_latency_ms": f"{self.stats['avg_latency_ms']:.2f}",
            "timestamp": datetime.now().isoformat()
        }

# ============================================================================
# MAIN TEST FUNCTION
# ============================================================================

def test_retrieval_system():
    """Test all three retrieval modes"""
    
    engine = HybridRetrievalEngine(
        vector_store_path="./rag_local/hybrid_vectors.json",
        graph_store_path="./rag_local/hybrid_graph.json"
    )
    
    print("\n" + "="*70)
    print("HYBRID DATABASE RETRIEVAL SYSTEM TEST")
    print("="*70)
    
    # Test queries
    test_queries = [
        "Who founded SpaceX?",
        "What companies are related to Elon Musk?",
        "Where is SpaceX located?"
    ]
    
    for query in test_queries:
        print(f"\n\n{'='*70}")
        print(f"QUERY: {query}")
        print('='*70)
        
        # 1. LOCAL (VECTOR ONLY)
        print("\n1️⃣  LOCAL SEARCH (Vector-only)")
        print("-" * 70)
        local_result = engine.local_search(query, top_k=3)
        engine.update_stats("local", local_result.get("latency_ms", 0))
        
        print(f"Mode: {local_result['mode']}")
        print(f"Confidence: {local_result.get('confidence', 0):.2%}")
        print(f"Latency: {local_result.get('latency_ms', 0):.2f}ms")
        print(f"Results: {len(local_result.get('results', []))} nodes found")
        
        for i, result in enumerate(local_result.get("results", [])[:3], 1):
            print(f"\n  {i}. {result['text'][:80]}")
            print(f"     Score: {result['similarity_score']:.4f}")
        
        # 2. GLOBAL (GRAPH ONLY)
        print("\n2️⃣  GLOBAL SEARCH (Graph-only)")
        print("-" * 70)
        global_result = engine.global_search(query, depth=2)
        engine.update_stats("global", global_result.get("latency_ms", 0))
        
        print(f"Mode: {global_result['mode']}")
        print(f"Confidence: {global_result.get('confidence', 0):.2%}")
        print(f"Latency: {global_result.get('latency_ms', 0):.2f}ms")
        print(f"Entities: {len(global_result.get('entities', []))} found")
        print(f"Relationships: {len(global_result.get('relationships', []))} found")
        
        for i, entity in enumerate(global_result.get("entities", [])[:3], 1):
            print(f"\n  {i}. {entity['text'][:80]}")
            print(f"     Score: {entity['score']:.4f}")
        
        if global_result.get("relationships"):
            print(f"\n  Relationships:")
            for rel in global_result.get("relationships", [])[:3]:
                print(f"    - {rel['source']} --[{rel['type']}]--> {rel['target']}")
        
        # 3. HYBRID (VECTOR + GRAPH)
        print("\n3️⃣  HYBRID SEARCH (Vector + Graph Combined) ⭐")
        print("-" * 70)
        hybrid_result = engine.hybrid_search(query, top_k=5, do_rerank=True)
        engine.update_stats("hybrid", hybrid_result.get("latency_ms", 0))
        
        print(f"Mode: {hybrid_result['mode']}")
        print(f"Confidence: {hybrid_result.get('confidence', 0):.2%}")
        print(f"Latency: {hybrid_result.get('latency_ms', 0):.2f}ms")
        print(f"Vector weight: {hybrid_result.get('vector_weight', 0.6)}")
        print(f"Graph weight: {hybrid_result.get('graph_weight', 0.4)}")
        print(f"Results: {len(hybrid_result.get('results', []))} nodes found")
        
        for i, result in enumerate(hybrid_result.get("results", []), 1):
            print(f"\n  {i}. {result['text'][:80]}")
            print(f"     Hybrid Score: {result['hybrid_score']:.4f}")
            print(f"     Vector: {result['vector_score']:.4f} | Graph: {result['graph_score']:.4f}")
    
    # Final statistics
    print(f"\n\n{'='*70}")
    print("RETRIEVAL STATISTICS")
    print('='*70)
    stats = engine.get_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    test_retrieval_system()
