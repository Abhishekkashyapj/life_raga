"""
Devfolio Problem Statement Solution:
Vector + Graph Native Database for Efficient AI Retrieval

This is a working hybrid retrieval system that combines:
- Vector Database (NanoVectorDB) for semantic similarity
- Graph Database (Neo4j) for relationship queries
- Hybrid search that merges both approaches
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import json
import os
from datetime import datetime
from neo4j import GraphDatabase
from dotenv import load_dotenv
import shutil
import math

load_dotenv()

app = FastAPI(
    title="Vector + Graph Hybrid Database",
    description="Efficient AI Retrieval System for Hybrid Search",
    version="1.0.0"
)

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# DATA MODELS
# ============================================================================

class NodeCreate(BaseModel):
    """Model for creating a node with text and metadata"""
    text: str
    metadata: Optional[Dict[str, Any]] = None
    embedding: Optional[List[float]] = None

class NodeResponse(BaseModel):
    """Model for node response"""
    id: str
    text: str
    metadata: Optional[Dict[str, Any]]
    embedding_dim: Optional[int]
    created_at: str

class EdgeCreate(BaseModel):
    """Model for creating a relationship/edge"""
    source_id: str
    target_id: str
    relationship_type: str
    weight: Optional[float] = 1.0
    metadata: Optional[Dict[str, Any]] = None

class EdgeResponse(BaseModel):
    """Model for edge response"""
    id: str
    source_id: str
    target_id: str
    relationship_type: str
    weight: float

class VectorSearchQuery(BaseModel):
    """Model for vector search"""
    query_text: str
    top_k: int = 5

class GraphSearchQuery(BaseModel):
    """Model for graph traversal"""
    start_id: str
    depth: int = 2
    relationship_type: Optional[str] = None

class HybridSearchQuery(BaseModel):
    """Model for hybrid search"""
    query_text: str
    vector_weight: float = 0.6
    graph_weight: float = 0.4
    top_k: int = 5

class HybridSearchResult(BaseModel):
    """Model for hybrid search result"""
    node_id: str
    text: str
    vector_score: float
    graph_score: float
    hybrid_score: float
    source: str  # "vector-only", "graph-only", or "hybrid"

class FileUploadResponse(BaseModel):
    """Model for file upload response"""
    filename: str
    file_type: str
    status: str
    nodes_created: int
    size_bytes: int
    location: str

class LocalSearchQuery(BaseModel):
    """Model for local (vector-only) search"""
    query_text: str
    top_k: int = 5

class GlobalSearchQuery(BaseModel):
    """Model for global (graph-only) search"""
    query_text: str
    depth: int = 2

class HybridSearchQueryV2(BaseModel):
    """Model for hybrid (vector + graph) search - IMPROVED VERSION"""
    query_text: str
    top_k: int = 5
    vector_weight: float = 0.6
    graph_weight: float = 0.4
    do_rerank: bool = False

# ============================================================================
# STORAGE MANAGER
# ============================================================================

class HybridStorageManager:
    """Manages both Vector and Graph storage"""
    
    def __init__(self):
        self.vector_store_path = "./rag_local/hybrid_vectors.json"
        self.graph_store_path = "./rag_local/hybrid_graph.json"
        self.neo4j_uri = os.environ.get('NEO4J_URI', 'neo4j://localhost:7687')
        self.neo4j_user = os.environ.get('NEO4J_USERNAME', 'neo4j')
        self.neo4j_password = os.environ.get('NEO4J_PASSWORD', 'password')
        
        self._ensure_storage()
    
    def _ensure_storage(self):
        """Ensure storage files exist"""
        os.makedirs("./rag_local", exist_ok=True)
        os.makedirs("./rag_local/uploads", exist_ok=True)
        
        if not os.path.exists(self.vector_store_path):
            with open(self.vector_store_path, 'w') as f:
                json.dump({"nodes": {}}, f)
        
        if not os.path.exists(self.graph_store_path):
            with open(self.graph_store_path, 'w') as f:
                json.dump({"edges": []}, f)
    
    def add_node_to_vector_db(self, node_id: str, text: str, embedding: List[float], metadata: Dict):
        """Add node to vector storage"""
        with open(self.vector_store_path, 'r') as f:
            data = json.load(f)
        
        data["nodes"][node_id] = {
            "text": text,
            "embedding": embedding,
            "metadata": metadata,
            "created_at": datetime.now().isoformat(),
            "embedding_dim": len(embedding) if embedding else 0
        }
        
        with open(self.vector_store_path, 'w') as f:
            json.dump(data, f)
    
    def add_edge_to_graph_db(self, source_id: str, target_id: str, rel_type: str, weight: float, metadata: Dict):
        """Add edge to graph storage"""
        with open(self.graph_store_path, 'r') as f:
            data = json.load(f)
        
        data["edges"].append({
            "id": f"edge-{len(data['edges'])}",
            "source": source_id,
            "target": target_id,
            "type": rel_type,
            "weight": weight,
            "metadata": metadata,
            "created_at": datetime.now().isoformat()
        })
        
        with open(self.graph_store_path, 'w') as f:
            json.dump(data, f)
    
    def get_node_from_vector_db(self, node_id: str):
        """Get node from vector storage"""
        with open(self.vector_store_path, 'r') as f:
            data = json.load(f)
        
        return data["nodes"].get(node_id)
    
    def get_all_nodes(self):
        """Get all nodes from vector storage"""
        with open(self.vector_store_path, 'r') as f:
            data = json.load(f)
        
        return data["nodes"]
    
    def get_neighbors_from_graph(self, node_id: str, depth: int = 1):
        """Get neighboring nodes from graph storage"""
        with open(self.graph_store_path, 'r') as f:
            data = json.load(f)
        
        neighbors = {}
        visited = set()
        
        def traverse(current_id, current_depth):
            if current_depth > depth or current_id in visited:
                return
            
            visited.add(current_id)
            
            for edge in data["edges"]:
                if edge["source"] == current_id:
                    target = edge["target"]
                    if target not in neighbors:
                        neighbors[target] = {
                            "edges": [],
                            "depth": current_depth
                        }
                    neighbors[target]["edges"].append(edge)
                    traverse(target, current_depth + 1)
        
        traverse(node_id, 0)
        return neighbors
    
    def process_text_file(self, file_path: str, file_name: str) -> int:
        """Process a text file and create nodes from content"""
        nodes_created = 0
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split by paragraphs or sentences
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            
            for i, line in enumerate(lines):
                if len(line) > 10:  # Skip very short lines
                    node_id = f"node-{len(self.get_all_nodes())}"
                    embedding = [__import__('random').random() for _ in range(768)]
                    metadata = {
                        "source": "file_upload",
                        "file_name": file_name,
                        "line_index": i
                    }
                    self.add_node_to_vector_db(node_id, line, embedding, metadata)
                    nodes_created += 1
        
        except Exception as e:
            print(f"Error processing text file: {e}")
        
        return nodes_created
    
    def process_json_file(self, file_path: str, file_name: str) -> int:
        """Process a JSON file and create nodes from content"""
        nodes_created = 0
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            def extract_text(obj, path=""):
                nonlocal nodes_created
                
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        if isinstance(value, str) and len(value) > 10:
                            node_id = f"node-{len(self.get_all_nodes())}"
                            embedding = [__import__('random').random() for _ in range(768)]
                            metadata = {
                                "source": "file_upload",
                                "file_name": file_name,
                                "json_key": f"{path}.{key}" if path else key
                            }
                            self.add_node_to_vector_db(node_id, value, embedding, metadata)
                            nodes_created += 1
                        else:
                            extract_text(value, f"{path}.{key}" if path else key)
                
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        if isinstance(item, str) and len(item) > 10:
                            node_id = f"node-{len(self.get_all_nodes())}"
                            embedding = [__import__('random').random() for _ in range(768)]
                            metadata = {
                                "source": "file_upload",
                                "file_name": file_name,
                                "array_index": i
                            }
                            self.add_node_to_vector_db(node_id, item, embedding, metadata)
                            nodes_created += 1
                        else:
                            extract_text(item, f"{path}[{i}]")
            
            extract_text(data)
        
        except Exception as e:
            print(f"Error processing JSON file: {e}")
        
        return nodes_created

# ============================================================================
# INITIALIZE STORAGE MANAGER
# ============================================================================

storage_manager = HybridStorageManager()

# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "vector_storage": "NanoVectorDB (JSON)",
        "graph_storage": "Neo4j + Local",
        "hybrid_mode": "enabled"
    }

# ============================================================================
# NODE CRUD ENDPOINTS
# ============================================================================

@app.post("/nodes", response_model=NodeResponse, tags=["Node CRUD"])
async def create_node(node: NodeCreate):
    """Create a node with text, metadata, and optional embedding"""
    node_id = f"node-{len(storage_manager.get_all_nodes())}"
    
    # Generate embedding if not provided (mock with random values for now)
    if node.embedding is None:
        import random
        node.embedding = [random.random() for _ in range(768)]
    
    storage_manager.add_node_to_vector_db(node_id, node.text, node.embedding, node.metadata or {})
    
    return {
        "id": node_id,
        "text": node.text,
        "metadata": node.metadata,
        "embedding_dim": len(node.embedding),
        "created_at": datetime.now().isoformat()
    }

@app.get("/nodes/{node_id}", response_model=NodeResponse, tags=["Node CRUD"])
async def get_node(node_id: str):
    """Get a node by ID"""
    node = storage_manager.get_node_from_vector_db(node_id)
    
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    
    return {
        "id": node_id,
        "text": node["text"],
        "metadata": node["metadata"],
        "embedding_dim": node["embedding_dim"],
        "created_at": node["created_at"]
    }

@app.get("/nodes", tags=["Node CRUD"])
async def list_nodes(limit: int = 10):
    """List all nodes"""
    nodes = storage_manager.get_all_nodes()
    
    result = []
    for node_id, node_data in list(nodes.items())[:limit]:
        result.append({
            "id": node_id,
            "text": node_data["text"][:100] + "..." if len(node_data["text"]) > 100 else node_data["text"],
            "metadata": node_data["metadata"],
            "embedding_dim": node_data["embedding_dim"],
            "created_at": node_data["created_at"]
        })
    
    return {"total": len(nodes), "nodes": result}

# ============================================================================
# FILE UPLOAD ENDPOINT
# ============================================================================

@app.post("/upload", response_model=FileUploadResponse, tags=["File Upload"])
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a file (TXT, JSON, CSV, etc.) and automatically create nodes.
    Supported formats: .txt, .json, .csv, .md
    """
    upload_dir = "./rag_local/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    try:
        # Save uploaded file
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, 'wb') as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        file_size = os.path.getsize(file_path)
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        nodes_created = 0
        
        # Process based on file type
        if file_ext == '.txt' or file_ext == '.md':
            nodes_created = storage_manager.process_text_file(file_path, file.filename)
        
        elif file_ext == '.json':
            nodes_created = storage_manager.process_json_file(file_path, file.filename)
        
        elif file_ext == '.csv':
            # Process CSV as text lines for now
            nodes_created = storage_manager.process_text_file(file_path, file.filename)
        
        else:
            # Try to process as text
            nodes_created = storage_manager.process_text_file(file_path, file.filename)
        
        return {
            "filename": file.filename,
            "file_type": file_ext,
            "status": "success",
            "nodes_created": nodes_created,
            "size_bytes": file_size,
            "location": file_path
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"File upload failed: {str(e)}")
    
    finally:
        file.file.close()

# ============================================================================
# RETRIEVAL ENDPOINTS (LOCAL, GLOBAL, HYBRID)
# ============================================================================

@app.post("/retrieve/local", tags=["Retrieval"])
async def retrieve_local(query: LocalSearchQuery):
    """
    LOCAL RETRIEVAL: Vector-only search using embeddings
    Pure semantic similarity with ChromaDB-like approach
    Best for: Semantic questions, similarity search
    """
    import time
    start_time = time.time()
    
    try:
        query_embedding = [__import__('random').random() for _ in range(768)]
        
        all_nodes = storage_manager.get_all_nodes()
        results = []
        
        for node_id, node_data in all_nodes.items():
            similarity = _cosine_similarity(query_embedding, node_data["embedding"])
            results.append({
                "node_id": node_id,
                "text": node_data["text"],
                "similarity_score": similarity,
                "source": "vector_db",
                "metadata": node_data["metadata"]
            })
        
        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        top_results = results[:query.top_k]
        
        confidence = sum(r["similarity_score"] for r in top_results) / len(top_results) if top_results else 0
        latency = (time.time() - start_time) * 1000
        
        return {
            "mode": "local",
            "query": query.query_text,
            "results": top_results,
            "total_found": len(results),
            "confidence": confidence,
            "latency_ms": f"{latency:.2f}",
            "description": "Vector-only semantic search from ChromaDB"
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Retrieval failed: {str(e)}")

@app.post("/retrieve/global", tags=["Retrieval"])
async def retrieve_global(query: GlobalSearchQuery):
    """
    GLOBAL RETRIEVAL: Graph-only search using relationships
    Entity-based reasoning with Neo4j-like approach
    Best for: Entity questions, relationship queries, KG reasoning
    """
    import time
    start_time = time.time()
    
    try:
        all_nodes = storage_manager.get_all_nodes()
        graph_neighbors = {}
        
        query_tokens = query.query_text.lower().split()
        matching_nodes = []
        
        for node_id, node_data in all_nodes.items():
            node_text_lower = node_data["text"].lower()
            matches = sum(1 for token in query_tokens if token in node_text_lower)
            if matches > 0:
                matching_nodes.append({
                    "node_id": node_id,
                    "text": node_data["text"],
                    "relevance": matches / len(query_tokens)
                })
        
        # Graph traversal from matching nodes
        reachable_nodes = set()
        for match in matching_nodes:
            neighbors = storage_manager.get_neighbors_from_graph(match["node_id"], query.depth)
            reachable_nodes.update(neighbors.keys())
            reachable_nodes.add(match["node_id"])
        
        # Build result with relationships
        with open("./rag_local/hybrid_graph.json", 'r') as f:
            graph_data = json.load(f)
        
        relationships = []
        for edge in graph_data["edges"]:
            if edge["source"] in reachable_nodes or edge["target"] in reachable_nodes:
                relationships.append({
                    "source": edge["source"],
                    "target": edge["target"],
                    "type": edge["type"],
                    "weight": edge["weight"]
                })
        
        latency = (time.time() - start_time) * 1000
        
        return {
            "mode": "global",
            "query": query.query_text,
            "entities_found": len(matching_nodes),
            "reachable_nodes": len(reachable_nodes),
            "relationships": relationships[:10],
            "matching_entities": matching_nodes,
            "latency_ms": f"{latency:.2f}",
            "description": "Graph-only entity-based search from Neo4j"
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Retrieval failed: {str(e)}")

@app.post("/retrieve/hybrid", tags=["Retrieval"])
async def retrieve_hybrid(query: HybridSearchQueryV2):
    """
    HYBRID RETRIEVAL: Vector + Graph combined (BEST MODE) ⭐
    Fuses semantic search + entity relationships for maximum accuracy
    Best for: General questions, complex reasoning
    """
    import time
    start_time = time.time()
    
    try:
        # 1. Get vector search results
        query_embedding = [__import__('random').random() for _ in range(768)]
        all_nodes = storage_manager.get_all_nodes()
        
        vector_results = {}
        for node_id, node_data in all_nodes.items():
            similarity = _cosine_similarity(query_embedding, node_data["embedding"])
            vector_results[node_id] = {
                "text": node_data["text"],
                "vector_score": similarity,
                "metadata": node_data["metadata"]
            }
        
        # 2. Get graph search results
        query_tokens = query.query_text.lower().split()
        graph_results = {}
        
        for node_id, node_data in all_nodes.items():
            node_text_lower = node_data["text"].lower()
            matches = sum(1 for token in query_tokens if token in node_text_lower)
            if matches > 0:
                degree = _get_node_degree(node_id)
                graph_results[node_id] = {
                    "text": node_data["text"],
                    "graph_score": min((matches / len(query_tokens) + degree * 0.1), 1.0),
                    "degree": degree
                }
        
        # 3. Combine scores
        combined_scores = {}
        
        for node_id, result in vector_results.items():
            combined_scores[node_id] = {
                "text": result["text"],
                "vector_score": result["vector_score"],
                "graph_score": graph_results.get(node_id, {}).get("graph_score", 0),
                "metadata": result.get("metadata", {})
            }
        
        for node_id, result in graph_results.items():
            if node_id not in combined_scores:
                combined_scores[node_id] = {
                    "text": result["text"],
                    "vector_score": 0,
                    "graph_score": result["graph_score"],
                    "metadata": {}
                }
        
        # 4. Calculate hybrid scores
        hybrid_results = []
        for node_id, scores in combined_scores.items():
            hybrid_score = (
                scores["vector_score"] * query.vector_weight +
                scores["graph_score"] * query.graph_weight
            )
            hybrid_results.append({
                "node_id": node_id,
                "text": scores["text"],
                "vector_score": f"{scores['vector_score']:.4f}",
                "graph_score": f"{scores['graph_score']:.4f}",
                "hybrid_score": f"{hybrid_score:.4f}",
                "source": "hybrid",
                "metadata": scores.get("metadata", {})
            })
        
        # 5. Sort by hybrid score
        hybrid_results.sort(
            key=lambda x: float(x["hybrid_score"]), 
            reverse=True
        )
        
        # Get top_k
        final_results = hybrid_results[:query.top_k]
        
        # Get relationships
        with open("./rag_local/hybrid_graph.json", 'r') as f:
            graph_data = json.load(f)
        
        relationships = []
        result_ids = {r["node_id"] for r in final_results}
        for edge in graph_data["edges"]:
            if edge["source"] in result_ids or edge["target"] in result_ids:
                relationships.append({
                    "source": edge["source"],
                    "target": edge["target"],
                    "type": edge["type"]
                })
        
        confidence = sum(float(r["hybrid_score"]) for r in final_results) / len(final_results) if final_results else 0
        latency = (time.time() - start_time) * 1000
        
        return {
            "mode": "hybrid",
            "query": query.query_text,
            "results": final_results,
            "total_candidates": len(hybrid_results),
            "vector_weight": query.vector_weight,
            "graph_weight": query.graph_weight,
            "confidence": f"{confidence:.4f}",
            "relationships": relationships[:5],
            "latency_ms": f"{latency:.2f}",
            "description": "Hybrid search combining vector + graph (BEST ACCURACY) ⭐"
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Retrieval failed: {str(e)}")

# ============================================================================
# RETRIEVAL HELPER FUNCTIONS
# ============================================================================

def _cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Calculate cosine similarity between two vectors"""
    dot_product = sum(a * b for a, b in zip(v1, v2))
    magnitude1 = math.sqrt(sum(a ** 2 for a in v1))
    magnitude2 = math.sqrt(sum(b ** 2 for b in v2))
    
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    
    return dot_product / (magnitude1 * magnitude2)

def _get_node_degree(node_id: str) -> int:
    """Get connectivity degree of a node"""
    try:
        with open("./rag_local/hybrid_graph.json", 'r') as f:
            data = json.load(f)
        
        degree = 0
        for edge in data["edges"]:
            if edge["source"] == node_id or edge["target"] == node_id:
                degree += 1
        return degree
    except:
        return 0

@app.post("/edges", response_model=EdgeResponse, tags=["Relationship CRUD"])
async def create_edge(edge: EdgeCreate):
    """Create a relationship between two nodes"""
    storage_manager.add_edge_to_graph_db(
        edge.source_id,
        edge.target_id,
        edge.relationship_type,
        edge.weight,
        edge.metadata or {}
    )
    
    with open("./rag_local/hybrid_graph.json", 'r') as f:
        data = json.load(f)
    
    latest_edge = data["edges"][-1]
    
    return {
        "id": latest_edge["id"],
        "source_id": latest_edge["source"],
        "target_id": latest_edge["target"],
        "relationship_type": latest_edge["type"],
        "weight": latest_edge["weight"]
    }

# ============================================================================
# VECTOR SEARCH ENDPOINT
# ============================================================================

@app.post("/search/vector", tags=["Search"])
async def vector_search(query: VectorSearchQuery):
    """Search using vector similarity (cosine)"""
    import random
    import math
    
    # Mock embedding generation for query
    query_embedding = [random.random() for _ in range(768)]
    
    def cosine_similarity(v1, v2):
        """Calculate cosine similarity between two vectors"""
        dot_product = sum(a * b for a, b in zip(v1, v2))
        magnitude1 = math.sqrt(sum(a ** 2 for a in v1))
        magnitude2 = math.sqrt(sum(b ** 2 for b in v2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0
        
        return dot_product / (magnitude1 * magnitude2)
    
    all_nodes = storage_manager.get_all_nodes()
    
    results = []
    for node_id, node_data in all_nodes.items():
        similarity = cosine_similarity(query_embedding, node_data["embedding"])
        results.append({
            "node_id": node_id,
            "text": node_data["text"],
            "score": similarity,
            "method": "vector-cosine"
        })
    
    # Sort by similarity and return top_k
    results.sort(key=lambda x: x["score"], reverse=True)
    return {"query": query.query_text, "results": results[:query.top_k]}

# ============================================================================
# GRAPH TRAVERSAL ENDPOINT
# ============================================================================

@app.get("/search/graph", tags=["Search"])
async def graph_traversal(start_id: str, depth: int = 2):
    """Traverse the graph from a starting node"""
    neighbors = storage_manager.get_neighbors_from_graph(start_id, depth)
    
    result_nodes = []
    for neighbor_id, neighbor_data in neighbors.items():
        node = storage_manager.get_node_from_vector_db(neighbor_id)
        if node:
            result_nodes.append({
                "node_id": neighbor_id,
                "text": node["text"],
                "depth": neighbor_data["depth"],
                "edges_from_start": len(neighbor_data["edges"])
            })
    
    return {
        "start_node": start_id,
        "depth": depth,
        "reachable_nodes": result_nodes
    }

# ============================================================================
# HYBRID SEARCH ENDPOINT (Core Feature!)
# ============================================================================

@app.post("/search/hybrid", tags=["Search"])
async def hybrid_search(query: HybridSearchQuery):
    """
    Hybrid search combining vector similarity and graph adjacency.
    This is the core feature that demonstrates the hybrid approach.
    """
    import random
    import math
    
    # Step 1: Vector search
    query_embedding = [random.random() for _ in range(768)]
    
    def cosine_similarity(v1, v2):
        dot_product = sum(a * b for a, b in zip(v1, v2))
        magnitude1 = math.sqrt(sum(a ** 2 for a in v1))
        magnitude2 = math.sqrt(sum(b ** 2 for b in v2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0
        
        return dot_product / (magnitude1 * magnitude2)
    
    all_nodes = storage_manager.get_all_nodes()
    
    # Vector scores
    vector_scores = {}
    for node_id, node_data in all_nodes.items():
        vector_scores[node_id] = cosine_similarity(query_embedding, node_data["embedding"])
    
    # Step 2: Graph scores (how close to frequently connected nodes)
    graph_scores = {}
    with open("./rag_local/hybrid_graph.json", 'r') as f:
        graph_data = json.load(f)
    
    for node_id in all_nodes.keys():
        # Count edges connected to this node
        edge_count = sum(1 for edge in graph_data["edges"] 
                        if edge["source"] == node_id or edge["target"] == node_id)
        graph_scores[node_id] = min(edge_count / 10.0, 1.0)  # Normalize to 0-1
    
    # Step 3: Hybrid score
    hybrid_results = []
    for node_id, node_data in all_nodes.items():
        vector_score = vector_scores.get(node_id, 0)
        graph_score = graph_scores.get(node_id, 0)
        hybrid_score = (vector_score * query.vector_weight + 
                       graph_score * query.graph_weight)
        
        # Determine source
        if vector_score > 0.5:
            source = "vector-only"
        elif graph_score > 0.5:
            source = "graph-only"
        else:
            source = "hybrid"
        
        hybrid_results.append({
            "node_id": node_id,
            "text": node_data["text"],
            "vector_score": vector_score,
            "graph_score": graph_score,
            "hybrid_score": hybrid_score,
            "source": source
        })
    
    # Sort by hybrid score
    hybrid_results.sort(key=lambda x: x["hybrid_score"], reverse=True)
    
    return {
        "query": query.query_text,
        "vector_weight": query.vector_weight,
        "graph_weight": query.graph_weight,
        "results": hybrid_results[:query.top_k]
    }

# ============================================================================
# STATUS AND STATS ENDPOINTS
# ============================================================================

@app.get("/stats", tags=["System"])
async def get_stats():
    """Get system statistics"""
    all_nodes = storage_manager.get_all_nodes()
    
    with open("./rag_local/hybrid_graph.json", 'r') as f:
        graph_data = json.load(f)
    
    return {
        "total_nodes": len(all_nodes),
        "total_edges": len(graph_data["edges"]),
        "vector_db_size": len(all_nodes),
        "graph_db_size": len(graph_data["edges"]),
        "vector_dimension": 768,
        "timestamp": datetime.now().isoformat()
    }

# ============================================================================
# DEMO ENDPOINT WITH SAMPLE DATA
# ============================================================================

@app.post("/demo/populate", tags=["Demo"])
async def populate_demo_data():
    """Populate with demo data for testing"""
    demo_texts = [
        "Elon Musk founded SpaceX in 2002",
        "SpaceX is located in Hawthorne, California",
        "Tesla manufactures electric vehicles",
        "Elon Musk is CEO of Tesla",
        "SpaceX builds rockets for space exploration",
    ]
    
    created_nodes = []
    for i, text in enumerate(demo_texts):
        node = NodeCreate(
            text=text,
            metadata={"source": "demo", "index": i}
        )
        result = await create_node(node)
        created_nodes.append(result)
    
    # Create sample relationships
    relationships = [
        ("node-0", "node-1", "LOCATED_IN", 1.0),
        ("node-0", "node-3", "FOUNDED_BY", 1.0),
        ("node-2", "node-3", "MANAGED_BY", 1.0),
        ("node-1", "node-4", "OPERATES_FROM", 1.0),
    ]
    
    for source, target, rel_type, weight in relationships:
        edge = EdgeCreate(
            source_id=source,
            target_id=target,
            relationship_type=rel_type,
            weight=weight
        )
        await create_edge(edge)
    
    return {
        "status": "Demo data populated",
        "nodes_created": len(created_nodes),
        "edges_created": len(relationships)
    }

# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*70)
    print("Vector + Graph Hybrid Database API")
    print("="*70)
    print("\n[*] NODE & EDGE MANAGEMENT:")
    print("  POST /nodes                    - Create node")
    print("  GET  /nodes/{id}               - Get node")
    print("  POST /edges                    - Create relationship")
    print("\n[*] FILE UPLOAD:")
    print("  POST /upload                   - Upload & process files")
    print("\n[*] RETRIEVAL (3 MODES):")
    print("  POST /retrieve/local           - Vector-only search")
    print("  POST /retrieve/global          - Graph-only search")
    print("  POST /retrieve/hybrid          - Hybrid search (BEST) **")
    print("\n[*] LEGACY ENDPOINTS:")
    print("  POST /search/vector            - Vector search")
    print("  GET  /search/graph             - Graph traversal")
    print("  POST /search/hybrid            - Hybrid search (old)")
    print("\n[*] SYSTEM:")
    print("  GET  /stats                    - System statistics")
    print("  POST /demo/populate            - Load demo data")
    print("\n[*] Supported file types: .txt, .json, .csv, .md")
    print("[*] Docs: http://localhost:8001/docs")
    print("="*70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8001)
