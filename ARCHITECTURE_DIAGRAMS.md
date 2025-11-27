# RAG System Architecture Diagram & Flow

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     CLIENT / USER APPLICATION                    │
│  (Web Browser, Python Script, API Consumer, etc.)                │
└────────────────────────────┬────────────────────────────────────┘
                             │
                    HTTP/REST API (Port 8001)
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              FASTAPI SERVER (hybrid_db_api.py)                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                 ENDPOINT ROUTING                         │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │  POST /retrieve/local    → LocalSearchQuery              │   │
│  │  POST /retrieve/global   → GlobalSearchQuery             │   │
│  │  POST /retrieve/hybrid   → HybridSearchQueryV2           │   │
│  │  POST /upload            → FileUploadResponse            │   │
│  │  POST /nodes             → NodeCreate                    │   │
│  │  POST /edges             → EdgeCreate                    │   │
│  │  GET  /stats             → SystemStatistics              │   │
│  └──────────────────────────────────────────────────────────┘   │
│                             │                                    │
│                             ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │          HYBRID STORAGE MANAGER                          │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │  • add_node_to_vector_db()                               │   │
│  │  • add_edge_to_graph_db()                                │   │
│  │  • get_all_nodes()                                       │   │
│  │  • get_neighbors_from_graph()                            │   │
│  │  • process_text_file()                                   │   │
│  │  • process_json_file()                                   │   │
│  │  • process_csv_file()                                    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                             │                                    │
│        ┌────────────────────┴────────────────────┐               │
│        ▼                                          ▼              │
│  ┌──────────────────────┐             ┌──────────────────────┐  │
│  │  RETRIEVAL ENGINE    │             │   HELPER FUNCTIONS   │  │
│  ├──────────────────────┤             ├──────────────────────┤  │
│  │                      │             │                      │  │
│  │ LOCAL MODE:          │             │ _cosine_similarity() │  │
│  │  • Vector search     │             │ _get_node_degree()   │  │
│  │  • Embeddings       │             │                      │  │
│  │  • Cosine similarity │             └──────────────────────┘  │
│  │                      │                                       │
│  │ GLOBAL MODE:         │                                       │
│  │  • Graph traversal   │                                       │
│  │  • Keyword match     │                                       │
│  │  • BFS search        │                                       │
│  │                      │                                       │
│  │ HYBRID MODE:         │                                       │
│  │  • Vector scoring    │                                       │
│  │  • Graph scoring     │                                       │
│  │  • Combined ranking  │                                       │
│  │  • Configurable      │                                       │
│  │    weights           │                                       │
│  └──────────────────────┘                                       │
│                                                                   │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                │                           │
                ▼                           ▼
    ┌─────────────────────┐    ┌─────────────────────┐
    │  VECTOR DATABASE    │    │   GRAPH DATABASE    │
    ├─────────────────────┤    ├─────────────────────┤
    │ hybrid_vectors.json │    │  hybrid_graph.json  │
    │                     │    │                     │
    │ Structure:          │    │ Structure:          │
    │ {                   │    │ {                   │
    │  "nodes": {         │    │  "edges": [         │
    │    "node-0": {      │    │    {                │
    │      "text": "...", │    │      "id": "...",   │
    │      "embedding":   │    │      "source": "...",
    │      [768 dims],    │    │      "target": "...",
    │      "metadata": {} │    │      "type": "...", │
    │    }                │    │      "weight": 1.0  │
    │  }                  │    │    }                │
    │ }                   │    │  ]                  │
    │                     │    │ }                   │
    │ • 5 nodes          │    │ • 4 edges           │
    │ • 768 dimensions   │    │ • Relationships     │
    │ • Embeddings       │    │ • Traversable       │
    │ • Metadata         │    │ • Weighted          │
    └─────────────────────┘    └─────────────────────┘
            │                           │
            └─────────────┬─────────────┘
                          │
            ┌─────────────┴─────────────┐
            │                           │
            ▼                           ▼
    ┌──────────────────┐      ┌──────────────────┐
    │  FILE STORAGE    │      │  UPLOADED FILES  │
    ├──────────────────┤      ├──────────────────┤
    │ ./rag_local/     │      │ ./rag_local/     │
    │ (Configuration)  │      │ uploads/         │
    │                  │      │ (User Files)     │
    │ • Contains data  │      │                  │
    │ • Persisted      │      │ • User documents │
    │ • Offline ready  │      │ • Processed      │
    │ • 100MB+ ready   │      │ • Indexed        │
    └──────────────────┘      └──────────────────┘
```

---

## Data Flow Diagram - LOCAL RETRIEVAL

```
USER QUERY
    │
    ▼
┌─────────────────────────────────────┐
│  POST /retrieve/local               │
│  {"query_text": "...", "top_k": 3}  │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Generate Query Embedding           │
│  (768-dimensional vector)           │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Load All Nodes From Vector DB      │
│  (hybrid_vectors.json)              │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Calculate Cosine Similarity        │
│  For Each Node:                     │
│   similarity = query_vec · node_vec │
│                ─────────────────── │
│                |query_vec| · |node│
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Score All Results                  │
│  [                                  │
│    {node: 0, score: 0.85},          │
│    {node: 3, score: 0.72},          │
│    {node: 1, score: 0.69},          │
│    ...                              │
│  ]                                  │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Sort by Score (Descending)         │
│  [                                  │
│    {node: 0, score: 0.85},          │
│    {node: 3, score: 0.72},          │
│    {node: 1, score: 0.69},          │
│    ...                              │
│  ]                                  │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Select Top K Results               │
│  (Default: top 5, or user specified)│
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Format Response                    │
│  {                                  │
│    "mode": "local",                 │
│    "results": [...],                │
│    "confidence": 0.75,              │
│    "latency_ms": "3.4"              │
│  }                                  │
└────────────┬────────────────────────┘
             │
             ▼
        RETURN TO USER
```

---

## Data Flow Diagram - GLOBAL RETRIEVAL

```
USER QUERY
    │
    ▼
┌─────────────────────────────────────┐
│  POST /retrieve/global              │
│  {"query_text": "...", "depth": 2}  │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Tokenize Query                     │
│  "Tesla CEO" → ["tesla", "ceo"]     │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Find Matching Entities             │
│  Load All Nodes                     │
│  Match tokens in node text          │
│  Score: matched_tokens / total      │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Graph Traversal (BFS)              │
│  From each matched node:            │
│   - Explore edges (depth limit)     │
│   - Collect reachable nodes         │
│   - Track relationships             │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Build Result Structure             │
│  {                                  │
│    entities: [...],                 │
│    relationships: [...],            │
│    reachable_nodes: {...}           │
│  }                                  │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Format Response                    │
│  {                                  │
│    "mode": "global",                │
│    "entities_found": 2,             │
│    "relationships": [...],          │
│    "latency_ms": "2.6"              │
│  }                                  │
└────────────┬────────────────────────┘
             │
             ▼
        RETURN TO USER
```

---

## Data Flow Diagram - HYBRID RETRIEVAL (RECOMMENDED)

```
USER QUERY
    │
    ▼
┌─────────────────────────────────────┐
│  POST /retrieve/hybrid              │
│  {"query_text": "...", "top_k": 3}  │
│  "vector_weight": 0.6,              │
│  "graph_weight": 0.4}               │
└────────────┬────────────────────────┘
             │
        ┌────┴────┐
        │          │
        ▼          ▼
    VECTOR MODE  GRAPH MODE
    (60% weight) (40% weight)
        │          │
        ▼          ▼
    ┌────┐      ┌────────┐
    │Vec │      │ Graph  │
    │Sim │      │TraverDl│
    └─┬──┘      └─┬──────┘
      │           │
      ▼           ▼
   Vector    Graph Scores
   Scores    {node: 0.8}
   {node:    {node: 0.6}
    0.75}    {...}
   {...}
        │          │
        └────┬─────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Combine Scores                     │
│  hybrid_score =                     │
│    (vector_score × 0.6) +           │
│    (graph_score × 0.4)              │
│                                     │
│  Example:                           │
│  node-0: (0.75 × 0.6) + (0.8 × 0.4)│
│        = 0.45 + 0.32 = 0.77         │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Rank by Hybrid Score               │
│  [                                  │
│    {node: 0, score: 0.77},          │
│    {node: 3, score: 0.71},          │
│    {node: 1, score: 0.69},          │
│  ]                                  │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Select Top K Results               │
│  [                                  │
│    {node: 0, score: 0.77},          │
│    {node: 3, score: 0.71},          │
│    {node: 1, score: 0.69},          │
│  ]                                  │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Add Relationships                  │
│  For each result node, get edges    │
│  Load from hybrid_graph.json        │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Format Response                    │
│  {                                  │
│    "mode": "hybrid",                │
│    "results": [{                    │
│      "node_id": "node-0",           │
│      "vector_score": 0.75,          │
│      "graph_score": 0.8,            │
│      "hybrid_score": 0.77           │
│    }],                              │
│    "relationships": [...],          │
│    "confidence": "0.72",            │
│    "vector_weight": 0.6,            │
│    "graph_weight": 0.4,             │
│    "latency_ms": "3.5"              │
│  }                                  │
└────────────┬────────────────────────┘
             │
             ▼
        RETURN TO USER
```

---

## Similarity Scoring Algorithm (LOCAL MODE)

```
┌─────────────────────────────────────────────────────┐
│         COSINE SIMILARITY CALCULATION                │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Given two vectors v1 and v2 (768 dimensions):     │
│                                                     │
│  1. Calculate dot product:                          │
│     dot = Σ(v1[i] × v2[i]) for i in [0, 768)      │
│                                                     │
│  2. Calculate magnitudes:                           │
│     |v1| = √(Σ(v1[i]²))                           │
│     |v2| = √(Σ(v2[i]²))                           │
│                                                     │
│  3. Calculate cosine similarity:                    │
│     cos_sim = dot / (|v1| × |v2|)                 │
│                                                     │
│  Result range: [-1, 1]                             │
│    • 1.0  = identical direction                    │
│    • 0.5  = moderate similarity                    │
│    • 0.0  = perpendicular (no similarity)          │
│    • -1.0 = opposite direction                     │
│                                                     │
│  For our use case (normalized embeddings):         │
│    Result range: [0, 1]                            │
│    • 1.0  = exact semantic match                   │
│    • 0.7  = strong semantic similarity             │
│    • 0.5  = moderate similarity                    │
│    • 0.0  = no semantic relation                   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## Weight Tuning Guide (HYBRID MODE)

```
┌────────────────────────────────────────────────────┐
│    HYBRID SCORE: (VS × VW) + (GS × GW)            │
│    VS=Vector Score, VW=Vector Weight              │
│    GS=Graph Score,  GW=Graph Weight               │
└────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│           WEIGHT CONFIGURATION OPTIONS              │
├─────────────────────────────────────────────────────┤
│                                                     │
│ BALANCED (Default):                                 │
│   vector_weight: 0.6  (60%)                        │
│   graph_weight:  0.4  (40%)                        │
│   → Best for general use                           │
│   → Balanced semantic + relationships              │
│                                                     │
│ SEMANTIC HEAVY:                                     │
│   vector_weight: 0.8  (80%)                        │
│   graph_weight:  0.2  (20%)                        │
│   → For text-heavy collections                     │
│   → Prioritizes semantic understanding             │
│   → Good for similarity matching                   │
│                                                     │
│ STRUCTURE HEAVY:                                    │
│   vector_weight: 0.4  (40%)                        │
│   graph_weight:  0.6  (60%)                        │
│   → For highly structured data                     │
│   → Prioritizes relationships                      │
│   → Good for knowledge graphs                      │
│                                                     │
│ VECTOR ONLY:                                        │
│   vector_weight: 1.0  (100%)                       │
│   graph_weight:  0.0  (0%)                         │
│   → Use /retrieve/local instead                    │
│                                                     │
│ GRAPH ONLY:                                         │
│   vector_weight: 0.0  (0%)                         │
│   graph_weight:  1.0  (100%)                       │
│   → Use /retrieve/global instead                   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## Component Interaction Diagram

```
    ┌─────────────┐
    │   Browser   │
    │   / CLI     │
    └──────┬──────┘
           │
           │ HTTP REST
           ▼
    ┌──────────────────┐
    │ FastAPI Server   │◄──────┐
    │ (Port 8001)      │       │
    └────────┬─────────┘       │
             │                 │
      ┌──────┴────────┐        │
      │               │        │
      ▼               ▼        │
  ┌────────────┐  ┌────────────────┐
  │ Validator  │  │ Router         │
  │ (Pydantic) │  │ (FastAPI)      │
  └─────┬──────┘  └────────┬───────┘
        │                  │
        └────────┬─────────┘
                 │
                 ▼
        ┌─────────────────┐
        │ Storage Manager │
        └─────────────────┘
                 │
        ┌────────┴──────────┐
        │                   │
        ▼                   ▼
   ┌─────────────┐  ┌──────────────┐
   │   Vector    │  │    Graph     │
   │   Database  │  │   Database   │
   └─────────────┘  └──────────────┘
        │                   │
        ▼                   ▼
   ┌─────────────────────────────┐
   │   Retrieval Engines         │
   │ ┌────────────────────────┐  │
   │ │ Local Mode (Vector)    │  │
   │ ├────────────────────────┤  │
   │ │ Global Mode (Graph)    │  │
   │ ├────────────────────────┤  │
   │ │ Hybrid Mode (Both)     │  │
   │ └────────────────────────┘  │
   └─────────────┬────────────────┘
                 │
                 ▼
        ┌─────────────────┐
        │ Response Builder│
        └────────┬────────┘
                 │
                 ▼
        ┌─────────────────┐
        │   JSON Response │
        └────────┬────────┘
                 │
                 ▼
           Back to User
```

---

This architecture ensures:
✓ Fast response times
✓ Multiple retrieval strategies
✓ Flexible configuration
✓ 100% offline operation
✓ Easy scalability
