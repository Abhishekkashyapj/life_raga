# Hybrid RAG System - Complete Project Explanation

## 🎯 What You're Getting (Output Explanation)

When you use the system at **http://localhost:5173**, here's what happens:

### **Search Flow:**

```
User Input (Text Query)
    ↓
Frontend (React UI)
    ↓
Backend API (FastAPI on port 8001)
    ↓
Three Search Modes:
    ├─ Vector Search: Semantic similarity using embeddings
    ├─ Graph Search: Relationship traversal through nodes
    └─ Hybrid Search: Combined vector + graph scores (BEST)
    ↓
JSON Storage Files
    ├─ hybrid_vectors.json (vector embeddings)
    └─ hybrid_graph.json (graph relationships)
    ↓
Results Display
    ├─ Node ID
    ├─ Text Content
    ├─ Scores (Vector, Graph, Hybrid)
    └─ Metadata (source file, line number, etc.)
```

---

## 📁 Key Files in This Project

### **1. BACKEND API (Python - FastAPI)**

#### `hybrid_db_api.py` (Main Backend Server)
- **What it does**: REST API server that handles all search and upload operations
- **Port**: 8001
- **Key endpoints**:
  - `POST /upload` - Upload and process files (PDF, TXT, JSON, CSV)
  - `POST /retrieve/local` - Vector-only search
  - `POST /retrieve/global` - Graph-only search
  - `POST /retrieve/hybrid` - Combined search (best results)
  - `GET /stats` - System statistics (node count, etc.)
  - `POST /demo/populate` - Load sample data

**What we added/fixed**:
- ✅ Added `process_pdf_file()` method for PDF text extraction
- ✅ Fixed encoding issues with multiple encoding support (UTF-8, Latin-1, CP1252, etc.)
- ✅ Graceful fallback for corrupted files (errors='ignore')

---

### **2. FRONTEND (React + TypeScript + Vite)**

#### `ui/src/App.tsx` (Main React Component)
- **What it does**: Main application component managing state and search modes
- **Manages**: 
  - Retrieval mode selection (Vector/Graph/Hybrid)
  - Search state and results
  - File upload handling
  - Statistics fetching

#### `ui/src/components/Sidebar.tsx`
- **What it does**: Left sidebar UI
- **Contains**:
  - Retrieval Mode selector (3 buttons)
  - Upload Document area (drag-and-drop)
  - Statistics display (nodes and edges count)

#### `ui/src/components/MainContent.tsx`
- **What it does**: Right side main content area
- **Shows**:
  - Search header (title and description)
  - Search input field
  - Search button
  - Results metrics (Results Found, Total Candidates, Confidence, Latency)
  - Search results list

#### `ui/index.html`
- **What it does**: HTML entry point for the React app
- **Contains**: 
  - `<div id="root"></div>` - Where React mounts
  - Script loader for main.tsx

#### `ui/package.json`
- **Dependencies**:
  - `react` & `react-dom` - UI framework
  - `vite` - Fast dev server
  - `typescript` - Type safety
  - `tailwindcss` - Styling
  - `framer-motion` - Animations
  - `axios` - HTTP client
  - `lucide-react` - Icons

#### `ui/vite.config.ts`
- **What it does**: Vite build configuration
- **Handles**: React plugin, build settings

---

### **3. DATA STORAGE (JSON-based)**

#### `rag_local/hybrid_vectors.json` (Created at runtime)
```json
{
  "nodes": {
    "node-0": {
      "text": "The actual text content from your file",
      "embedding": [0.123, 0.456, ...],  // 768-dimensional vector
      "metadata": {
        "source": "file_upload",
        "file_name": "document.pdf",
        "page_number": 1,
        "line_index": 23
      },
      "created_at": "2025-11-28T...",
      "embedding_dim": 768
    }
  }
}
```
- **What it stores**: All extracted text and their embeddings

#### `rag_local/hybrid_graph.json` (Created at runtime)
```json
{
  "edges": [
    {
      "id": "edge-0",
      "source": "node-1",
      "target": "node-5",
      "type": "related_to",
      "weight": 0.8,
      "metadata": {...},
      "created_at": "2025-11-28T..."
    }
  ]
}
```
- **What it stores**: Relationships between nodes (graph connections)

---

### **4. CONFIGURATION FILES**

#### `.env` (Environment Variables)
```
NEO4J_URI=neo4j://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password
```
- Neo4j connection settings (if you want to use actual Neo4j later)

#### `requirements.txt` (Python Dependencies)
```
fastapi
uvicorn
pydantic
PyPDF2          # PDF processing (we added this)
python-multipart # Form data handling
neo4j          # Graph database (optional)
```

#### `pytest.ini` (Testing Configuration)
- Configuration for pytest test runner

---

### **5. SAMPLE DATA & SCRIPTS**

#### `sample_docs/` (Example Files)
- `employees.csv` - Sample structured data
- `companies.json` - Sample JSON data
- `project_notes.txt` - Sample text file
- `sample.txt` - Generic text sample

These are used to test the system with known data.

#### `check_environment.py`
- Verifies all dependencies are installed
- Checks Python version compatibility

#### `check_system.py`
- System health check script

---

### **6. DOCUMENTATION FILES**

#### `README.md`
- Project overview and setup instructions

#### `QUICK_START.md`
- Fast 2-minute setup guide

#### `ARCHITECTURE_DIAGRAMS.md`
- Visual diagrams of the system

#### `API_DOCUMENTATION.md`
- Detailed API endpoint documentation

#### `docs/ARCHITECTURE.md`
- Technical architecture details

---

### **7. TEST FILES**

#### `tests/test_integration.py`
- Integration tests for the full system

#### `test_retrieval.py`, `test_rag_system.py`
- Individual component tests

---

## 🔄 How the System Works (Step by Step)

### **Step 1: User Uploads File**
```
User clicks "Browse Files" or drags PDF
    ↓
Frontend sends: POST /upload with file
    ↓
Backend receives file
    ↓
hybrid_db_api.process_pdf_file() is called
    ↓
Text extracted from PDF
    ↓
Lines split into nodes
    ↓
Random 768-dim embeddings created
    ↓
Saved to hybrid_vectors.json
    ↓
Response: "5 nodes created"
```

### **Step 2: User Searches**
```
User types "elon musk"
    ↓
Frontend sends: POST /retrieve/hybrid?query=elon+musk
    ↓
Backend calculates:
    - Vector similarity (embedding distance)
    - Graph score (node connectivity)
    - Hybrid score (weighted combination)
    ↓
Sorts results by hybrid score
    ↓
Returns top 5 results with:
    - Node ID
    - Text snippet
    - Three scores
    - Metadata
    ↓
Frontend displays results
```

### **Step 3: Three Search Modes Explained**

#### **Vector Search (Local/Semantic)**
- **How it works**: Compares query embedding to all node embeddings
- **Similarity metric**: Cosine similarity
- **Best for**: Finding semantically similar content
- **Example**: "CEO of Tesla" would match "Elon Musk founded Tesla"

#### **Graph Search (Global/Relationships)**
- **How it works**: Traverses connections between nodes using BFS
- **Best for**: Finding related information through relationships
- **Example**: Find all nodes connected to a specific node

#### **Hybrid Search (BEST ACCURACY)**
- **How it works**: Combines both with weights
- **Formula**: `hybrid_score = 0.6 * vector_score + 0.4 * graph_score`
- **Best for**: Most accurate results combining semantics + relationships

---

## 📊 What Each File Type Processes

| File Type | Process | Result |
|-----------|---------|--------|
| `.pdf` | PyPDF2 extracts text → Split into lines | Text nodes with page numbers |
| `.txt` | Read file → Split by newlines | Text nodes with line indices |
| `.json` | Parse JSON → Extract string values → Recursive walk | Nodes from each text value |
| `.csv` | Treat as text file → Split by lines | Line-based text nodes |
| `.md` | Treat as text → Split by paragraphs | Markdown nodes |

---

## 🚀 What We Fixed/Added Recently

1. **PDF Support**
   - Added `process_pdf_file()` method
   - Uses PyPDF2 for text extraction
   - Preserves page numbers in metadata

2. **Encoding Fixes**
   - Multiple encoding support (UTF-8, Latin-1, CP1252, ISO-8859-1)
   - Graceful degradation with `errors='ignore'`
   - No more hexadecimal/corrupted output

3. **File Cleanup**
   - Removed temporary log files
   - Kept essential test/data files
   - Clean git history

---

## 🔧 Key Technologies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Backend | FastAPI + Uvicorn | REST API server |
| Frontend | React 19 + TypeScript | Web UI |
| Build | Vite | Fast development |
| Styling | Tailwind CSS | Modern CSS framework |
| Icons | Lucide React | UI icons |
| Animation | Framer Motion | Smooth animations |
| HTTP | Axios | API communication |
| Storage | JSON files | Vector & graph persistence |
| PDF | PyPDF2 | PDF text extraction |

---

## 📈 Performance Metrics You'll See

When you search, you'll see:
- **Results Found**: Number of matching nodes
- **Total Candidates**: All nodes checked
- **Confidence**: Average score of results (0-100%)
- **Latency**: Search time in milliseconds (typically 10-50ms)

---

## 🎯 Summary

Your system is a **complete hybrid retrieval system** that:
1. ✅ Stores documents as vector embeddings
2. ✅ Creates graph relationships between related content
3. ✅ Supports 3 search modes (Vector, Graph, Hybrid)
4. ✅ Handles multiple file formats (PDF, TXT, JSON, CSV, MD)
5. ✅ Provides real-time statistics and metrics
6. ✅ Runs completely locally (no cloud APIs)

The **Hybrid Search** gives the best results because it combines semantic understanding (vectors) with relationship knowledge (graphs).

