# Quick Start Guide - Vector + Graph Hybrid Database

**⏱ Time to working system: 2 minutes**

---

## Installation (1 minute)

### Prerequisites
```bash
# Python 3.11+ with pip
python --version
```

### Install Dependencies
```bash
pip install fastapi uvicorn pydantic tabulate requests
```

---

## Running the System (2 minutes)

### Terminal 1: Start API Server
```bash
python hybrid_db_api.py
```

**Expected output:**
```
======================================================================
Vector + Graph Hybrid Database API
======================================================================

Endpoints:
  POST /nodes                    - Create node
  GET  /nodes/{id}               - Get node
  POST /edges                    - Create relationship
  POST /search/vector            - Vector search
  GET  /search/graph             - Graph traversal
  POST /search/hybrid            - Hybrid search (CORE)
  GET  /stats                    - System statistics
  POST /demo/populate            - Load demo data

Docs: http://localhost:8000/docs
======================================================================

INFO:     Started server process [####]
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

✅ **API is ready!**

### Terminal 2: Run Interactive Demo
```bash
python hybrid_db_cli.py demo
```

**What it does:**
1. Loads 5 sample nodes + 4 relationships
2. Shows vector search (semantic similarity)
3. Shows graph traversal (relationship reasoning)
4. Shows hybrid search (BEST - combines both)
5. Displays comparison with scores

✅ **Demo complete!**

---

## Test API Endpoints

### Option A: Use Swagger UI (Easiest)

Open in browser: **http://localhost:8000/docs**

- Interactive testing
- Auto-generated documentation
- Try-it-out buttons
- Shows request/response format

### Option B: Use curl

**Health check:**
```bash
curl http://localhost:8000/health
```

**Create a node:**
```bash
curl -X POST http://localhost:8000/nodes \
  -H "Content-Type: application/json" \
  -d '{"text":"Your content here","metadata":{"source":"demo"}}'
```

**Vector search:**
```bash
curl -X POST http://localhost:8000/search/vector \
  -H "Content-Type: application/json" \
  -d '{"query_text":"search query","top_k":5}'
```

**Hybrid search (THE CORE FEATURE):**
```bash
curl -X POST http://localhost:8000/search/hybrid \
  -H "Content-Type: application/json" \
  -d '{"query_text":"CEO technology companies","vector_weight":0.6,"graph_weight":0.4,"top_k":5}'
```

---

## Available CLI Commands

### 1. Interactive Demo (Recommended)
```bash
python hybrid_db_cli.py demo
```
Shows all features with formatted output.

### 2. Performance Benchmark
```bash
python hybrid_db_cli.py benchmark
```
Tests query latency and throughput.

### 3. Hybrid Advantage Demo
```bash
python hybrid_db_cli.py hybrid-demo
```
Compares vector-only vs hybrid results.

---

## Core Concepts

### Vector Search
- **What:** Semantic similarity using embeddings
- **Algorithm:** Cosine distance on 768-dimensional vectors
- **Use case:** "Find content similar to my query"
- **Latency:** ~20ms
- **Pros:** Fast, semantic understanding
- **Cons:** Ignores relationships

### Graph Traversal
- **What:** Finding connected nodes
- **Algorithm:** Breadth-first search up to N hops
- **Use case:** "Find all related companies"
- **Latency:** ~8ms
- **Pros:** Perfect relationships
- **Cons:** No semantic understanding

### Hybrid Search ⭐
- **What:** Combined vector + graph scoring
- **Algorithm:** `hybrid_score = (vector_score × 0.6) + (graph_score × 0.4)`
- **Use case:** "Find relevant CEO of technology companies"
- **Latency:** ~30ms
- **Pros:** Best of both worlds!
- **Cons:** Slightly more compute

---

## Example Queries

### Query 1: Find similar content
```
POST /search/vector
{
  "query_text": "space exploration",
  "top_k": 5
}
```
Returns: Most semantically similar nodes.

### Query 2: Find connected nodes
```
GET /search/graph?start_id=node-0&depth=2
```
Returns: All nodes 0-2 hops from starting node.

### Query 3: Find relevant AND connected
```
POST /search/hybrid
{
  "query_text": "CEO technology",
  "vector_weight": 0.6,
  "graph_weight": 0.4,
  "top_k": 5
}
```
Returns: Combines semantic match + relationship signals.

---

## Response Format

### Hybrid Search Response
```json
{
  "query": "CEO technology companies",
  "vector_weight": 0.6,
  "graph_weight": 0.4,
  "results": [
    {
      "node_id": "node-3",
      "text": "Elon Musk is CEO of Tesla",
      "vector_score": 0.7832,
      "graph_score": 0.6000,
      "hybrid_score": 0.7499,
      "source": "hybrid"
    }
  ]
}
```

**Interpretation:**
- `node_id`: Which node this result is
- `vector_score`: How semantically similar (0-1)
- `graph_score`: How connected/central (0-1)
- `hybrid_score`: Combined score (higher = better)
- `source`: Which method contributed most

---

## File Storage

Data automatically persisted in `./rag_local/`:

```
rag_local/
├── hybrid_vectors.json    (Vector embeddings)
└── hybrid_graph.json      (Relationship edges)
```

Both files are JSON, human-readable, and survive server restarts.

---

## Configuration

### Change Hybrid Weights

Default: 60% vector, 40% graph
```bash
curl -X POST http://localhost:8000/search/hybrid \
  -d '{
    "query_text": "your query",
    "vector_weight": 0.7,    # More emphasis on semantics
    "graph_weight": 0.3,     # Less emphasis on relationships
    "top_k": 5
  }'
```

### Tune for Your Domain

- **E-commerce:** 70% vector, 30% graph (semantics > relationships)
- **Social networks:** 40% vector, 60% graph (relationships > keywords)
- **Knowledge graphs:** 50% vector, 50% graph (balanced)
- **Research:** 80% vector, 20% graph (semantic search priority)

---

## API Reference (Quick)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Check API status |
| `/nodes` | POST | Create a node |
| `/nodes/{id}` | GET | Retrieve a node |
| `/nodes` | GET | List all nodes |
| `/edges` | POST | Create relationship |
| `/search/vector` | POST | Vector search |
| `/search/graph` | GET | Graph traversal |
| `/search/hybrid` | POST | **Hybrid search** ⭐ |
| `/stats` | GET | System statistics |
| `/demo/populate` | POST | Load demo data |

**Full docs:** http://localhost:8000/docs

---

## Troubleshooting

### "Connection refused" on localhost:8000
```bash
# Make sure API is running in another terminal:
python hybrid_db_api.py
```

### "No module named 'fastapi'"
```bash
# Install dependencies:
pip install fastapi uvicorn pydantic tabulate requests
```

### "Port 8000 already in use"
```bash
# Kill existing process or use different port:
uvicorn hybrid_db_api:app --port 8001
```

### "No data in storage"
```bash
# Populate demo data:
python hybrid_db_cli.py demo
# or
curl -X POST http://localhost:8000/demo/populate
```

---

## Performance Targets

All operations should complete in <40ms:

| Query | Typical | Peak |
|-------|---------|------|
| Vector Search | 20-25ms | <40ms |
| Graph Traversal | 8-10ms | <40ms |
| Hybrid Search | 28-35ms | <40ms |

**Test:** `python hybrid_db_cli.py benchmark`

---

## Key Takeaway

**Why is hybrid search better than either alone?**

```
Vector-only: "Find semantically similar items"
  └─ Gets content about the topic ✓
  └─ But misses related items in the graph ✗

Graph-only: "Find connected items"
  └─ Gets all relationships ✓
  └─ But doesn't understand semantics ✗

Hybrid: "Find relevant items that are also connected"
  └─ Gets both semantic match + relationship signals ✓✓
  └─ Better ranking = happier users ✓
```

---

## Next Steps

1. **Start the system** (2 commands, see top)
2. **Run the demo** (`python hybrid_db_cli.py demo`)
3. **Try different queries** (modify search params)
4. **Adjust weights** (experiment with 0.5/0.5, 0.7/0.3, etc)
5. **Review code** (only 500 lines in API!)
6. **Read docs** (http://localhost:8000/docs)

---

## Get Help

- **API Docs:** http://localhost:8000/docs
- **Implementation:** See `hybrid_db_api.py` (well-commented)
- **Examples:** See `hybrid_db_cli.py` for client usage
- **Deep dive:** Read `API_DOCUMENTATION.md`

---

**Ready? Start with:** `python hybrid_db_api.py` 🚀
