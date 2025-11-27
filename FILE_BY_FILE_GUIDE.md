# 🎯 Quick File-by-File Reference

## Backend Python Files

### `hybrid_db_api.py` (970 lines)
```python
Main Components:
├─ HybridStorageManager class
│  ├─ add_node_to_vector_db()      → Stores text embeddings
│  ├─ add_edge_to_graph_db()       → Stores relationships
│  ├─ process_pdf_file()            → [NEW] Extracts PDF text
│  ├─ process_text_file()           → Handles .txt/.md files
│  ├─ process_json_file()           → Parses JSON files
│  └─ get_neighbors_from_graph()    → Graph traversal
│
├─ API Endpoints (FastAPI)
│  ├─ POST /upload                  → File upload & processing
│  ├─ POST /retrieve/local          → Vector search
│  ├─ POST /retrieve/global         → Graph search
│  ├─ POST /retrieve/hybrid         → Hybrid search [BEST]
│  ├─ GET /stats                    → System statistics
│  └─ POST /demo/populate           → Load sample data
│
└─ Data Models (Pydantic)
   ├─ NodeCreate / NodeResponse
   ├─ EdgeCreate / EdgeResponse
   ├─ VectorSearchQuery
   ├─ GraphSearchQuery
   └─ HybridSearchQuery
```

**What we modified:**
- ✅ Added PDF text extraction using PyPDF2
- ✅ Fixed file encoding issues (UTF-8, Latin-1, CP1252)
- ✅ Added graceful error handling for corrupted files

---

## Frontend React Files

### `ui/src/App.tsx` (214 lines)
```typescript
State Management:
├─ retrievalMode: 'vector' | 'graph' | 'hybrid'
├─ searchQuery: string
├─ searchResults: SearchResult[]
├─ stats: { total_nodes, total_edges, ... }
├─ loading: boolean
├─ selectedResult: SearchResult | null
└─ notification: { type, message }

Functions:
├─ fetchStats()        → Get node/edge counts
├─ handleSearch()      → Execute search query
├─ handleFileUpload()  → Upload files to backend
└─ selectResult()      → Show result details
```

### `ui/src/components/Sidebar.tsx`
```typescript
Renders:
├─ Logo + Title
├─ Retrieval Mode Buttons
│  ├─ Vector Search (Semantic)
│  ├─ Graph Search (Relationships)
│  └─ Hybrid Search (Best) ⭐
├─ Upload Document Area
│  ├─ Drag & drop zone
│  ├─ Browse Files button
│  └─ Supported formats text
└─ Statistics
   ├─ Node count
   └─ Edge count
```

### `ui/src/components/MainContent.tsx`
```typescript
Renders:
├─ Search Header
│  ├─ Mode icon
│  ├─ Mode title
│  └─ Mode description
├─ Search Input
│  ├─ Search field
│  └─ Search button
├─ Metrics Cards
│  ├─ Results Found
│  ├─ Total Candidates
│  ├─ Confidence %
│  └─ Latency (ms)
└─ Results List
   ├─ Node ID badge
   ├─ Source tag
   ├─ Text content
   ├─ Score breakdown
   │  ├─ Vector Score
   │  ├─ Graph Score
   │  └─ Hybrid Score
   └─ Metadata
```

### `ui/vite.config.ts`
```typescript
Config:
├─ React plugin
├─ TypeScript support
├─ Tailwind CSS processing
├─ Dev server on :5173
└─ Build optimizations
```

### `ui/index.html`
```html
<!doctype html>
<html>
  <head>
    <meta charset="UTF-8" />
    <title>Hybrid RAG - Vector + Graph Database</title>
  </head>
  <body>
    <div id="root"></div>  ← React mounts here
    <script src="/src/main.tsx"></script>
  </body>
</html>
```

---

## Configuration Files

### `requirements.txt`
```
fastapi              → Web framework
uvicorn             → ASGI server
pydantic            → Data validation
PyPDF2              → PDF text extraction [ADDED]
python-multipart    → Form data handling
neo4j               → Graph DB (optional)
requests            → HTTP client
```

### `.env`
```
NEO4J_URI=neo4j://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password
```

### `pytest.ini`
```
[pytest]
testpaths = tests
python_files = test_*.py
```

---

## Storage Files (Generated at Runtime)

### `rag_local/hybrid_vectors.json`
```json
{
  "nodes": {
    "node-0": {
      "text": "The extracted text content",
      "embedding": [0.1, 0.2, ..., 0.5],  ← 768 dimensions
      "metadata": {
        "source": "file_upload",
        "file_name": "document.pdf",
        "page_number": 1
      },
      "created_at": "ISO-8601 timestamp",
      "embedding_dim": 768
    },
    "node-1": { ... },
    "node-2": { ... }
  }
}
```
**Size grows with**: Each node + its 768-dimensional vector

### `rag_local/hybrid_graph.json`
```json
{
  "edges": [
    {
      "id": "edge-0",
      "source": "node-1",
      "target": "node-5",
      "type": "related_to",
      "weight": 0.85,
      "metadata": { ... },
      "created_at": "ISO-8601 timestamp"
    }
  ]
}
```
**What it represents**: Connections between related nodes

---

## Test Files

### `tests/test_integration.py`
```python
Tests:
├─ test_vector_storage()     → Node storage
├─ test_graph_storage()      → Edge storage
├─ test_full_pipeline()      → End-to-end
└─ test_retrieval_modes()    → All 3 search types
```

### `test_rag_system.py`
```python
Tests:
├─ test_api_endpoints()
├─ test_file_upload()
├─ test_vector_search()
├─ test_graph_search()
└─ test_hybrid_search()
```

---

## Documentation Files

| File | Purpose |
|------|---------|
| `README.md` | Project overview & setup |
| `QUICK_START.md` | 2-minute quick start |
| `API_DOCUMENTATION.md` | All API endpoints |
| `ARCHITECTURE_DIAGRAMS.md` | System diagrams |
| `docs/ARCHITECTURE.md` | Deep dive architecture |
| `docs/TECH_STACK.md` | Technology details |
| `docs/TESTING.md` | Testing guide |

---

## Sample Data Files

| File | Contains | Used for |
|------|----------|----------|
| `sample_docs/employees.csv` | Employee records | CSV testing |
| `sample_docs/companies.json` | Company data | JSON testing |
| `sample_docs/project_notes.txt` | Project notes | Text testing |
| `sample_docs/sample.txt` | Generic text | Demo data |

---

## Helper Scripts

### `check_environment.py`
```python
Checks:
├─ Python version (3.10+)
├─ Installed packages
├─ Database connectivity
└─ Required dependencies
```

### `check_system.py`
```python
Reports:
├─ System OS
├─ Python path
├─ Installed versions
└─ Environment status
```

---

## Directory Structure

```
life_raga/
├─ hybrid_db_api.py              ← Main backend [MODIFIED]
├─ requirements.txt              ← Python dependencies
├─ pytest.ini                    ← Test config
├─ .env                          ← Environment variables
│
├─ ui/                           ← Frontend React app
│  ├─ src/
│  │  ├─ App.tsx                 ← Main component
│  │  ├─ main.tsx               ← React entry
│  │  └─ components/
│  │     ├─ Sidebar.tsx          ← Left panel
│  │     └─ MainContent.tsx      ← Right panel
│  ├─ index.html                 ← HTML entry
│  ├─ package.json               ← JS dependencies
│  └─ vite.config.ts             ← Build config
│
├─ rag_local/                    ← [Created at runtime]
│  ├─ hybrid_vectors.json        ← All embeddings
│  ├─ hybrid_graph.json          ← All relationships
│  └─ uploads/                   ← Uploaded files
│
├─ sample_docs/                  ← Demo files
│  ├─ employees.csv
│  ├─ companies.json
│  └─ project_notes.txt
│
├─ tests/                        ← Test files
│  ├─ test_integration.py
│  └─ ...
│
└─ docs/                         ← Documentation
   ├─ ARCHITECTURE.md
   └─ TECH_STACK.md
```

---

## 🚀 Data Flow Summary

```
User → Frontend (React)
        ↓
        HTTP Request (Axios)
        ↓
Backend (FastAPI on :8001)
        ├─ If Upload: Save → Extract Text → Create Embeddings → Store in JSON
        └─ If Search: Query Vectors → Query Graph → Combine Results
        ↓
Response JSON
        ↓
Frontend Display (React Components)
        ↓
User sees Results
```

---

## 💡 Key Concepts

| Concept | What It Is | Where Used |
|---------|-----------|-----------|
| **Vector Embedding** | 768-dim float array | hybrid_vectors.json |
| **Cosine Similarity** | Vector distance metric | Vector search mode |
| **Node** | Text chunk with embedding | Vector database |
| **Edge** | Connection between nodes | Graph database |
| **BFS Traversal** | Find connected nodes | Graph search mode |
| **Hybrid Score** | 60% vector + 40% graph | Best search mode |

