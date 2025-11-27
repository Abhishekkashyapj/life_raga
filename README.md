# Local Hybrid RAG — ChromaDB + Neo4j + Ollama + LightRAG (Hackathon Scaffold)

This repo is a small, hackathon-friendly starter to build a **local hybrid RAG** system using:

- **ChromaDB** (local vector store)
- **Neo4j** (local graph DB via Docker)
- **Ollama** (local LLM + embeddings)
- **LightRAG** (pipeline orchestration)

### Dual Ingestion Pipelines

This scaffold includes two powerful ingestion pipelines:

1. **Structured Data Pipeline** — CSV/JSON → Direct Neo4j storage (no NER)
2. **Unstructured Data Pipeline** — TXT/PDF → NER → Entity extraction → Graph + Vector storage

Quick highlights

- Fully local — no cloud API keys required.
- **Dual-pipeline ingestion**: Handle both structured and unstructured data
- NER-based entity extraction for text documents
- Minimal runnable examples and docker-compose for dependencies
- Comprehensive test suite (unit + integration tests)
- PowerShell-friendly scripts for Windows

---

## Prerequisites (Windows)

- Install Python 3.10+ (recommended) and add to PATH
- Install Docker Desktop (for Neo4j)
- Install Ollama from https://ollama.com and pull the models below

## Quick setup (PowerShell)

### Step 1: Environment Setup

```powershell
# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip

# Install all dependencies (includes test packages)
pip install -r requirements.txt
```

### Step 2: Start Infrastructure

```powershell
# Start Neo4j in Docker
docker compose up -d

# Install Ollama (manual step from https://ollama.com)
# Then pull models:
ollama pull llama3.1:8b
ollama pull nomic-embed-text
```

### Step 3: Configure Environment

```powershell
# Copy and edit .env
copy .env.example .env
# Edit values if using non-default Neo4j credentials
```

### Step 4: Run Examples

**Default (sample data)**:
```powershell
python local_hybrid_rag.py
```

**Structured data only (CSV/JSON)**:
```powershell
python local_hybrid_rag.py --structured sample_docs/employees.csv
```

**Unstructured data only (TXT)**:
```powershell
python local_hybrid_rag.py --unstructured sample_docs/project_notes.txt
```

**Both pipelines**:
```powershell
python local_hybrid_rag.py `
  --structured sample_docs/employees.csv `
  --unstructured sample_docs/project_notes.txt
```

**Custom query**:
```powershell
python local_hybrid_rag.py --query "Who works where?"
```

---

Files added in this scaffold

- `local_hybrid_rag.py` — main script to ingest and query documents using both pipelines
- `etl_pipeline.py` — NER + entity/relation extraction for unstructured text
- `structured_handler.py` — CSV/JSON ingestion and direct graph storage
- `demo_dual_ingestion.py` — showcase both pipelines working together
- `test_ingestion_pipeline.py` — LightRAG integration test (requires Ollama + Neo4j)
- `tests/test_etl_pipeline.py` — unit tests for NER and extraction
- `tests/test_structured_handler.py` — unit tests for CSV/JSON ingestion
- `tests/test_integration.py` — integration tests combining pipelines
- `docker-compose.yml` — Neo4j service for local graph storage
- `requirements.txt` — dependencies + testing packages
- `.env.example` — config template for LightRAG + Neo4j + Ollama
- `sample_docs/` — sample files (CSV, JSON, TXT)
- `docs/ARCHITECTURE.md` — system architecture with Mermaid diagram
- `docs/DUAL_INGESTION.md` — detailed guide on both ingestion pipelines
- `docs/TESTING.md` — comprehensive testing guide
- `slides.md` — hackathon presentation

---

## Testing

### Run Unit Tests (Fast, no dependencies)

```powershell
pytest tests/test_etl_pipeline.py -v
pytest tests/test_structured_handler.py -v
pytest tests/test_integration.py -v
```

### Run Full Test Suite with Coverage

```powershell
pytest tests/ -v --cov=. --cov-report=term-missing
```

### Run LightRAG Integration Test (requires Ollama + Neo4j)

```powershell
python test_ingestion_pipeline.py
```

### Run Demo (both pipelines in action)

```powershell
python demo_dual_ingestion.py
```

See `docs/TESTING.md` for detailed test documentation.

---

## Tech Stack

### Core Mandatory Components

| Component | Purpose | Installation |
|-----------|---------|--------------|
| **Python 3.10+** | Language runtime | Pre-installed |
| **Ollama** | Local LLM + embeddings | Download from ollama.com |
| **ChromaDB** | Vector database | `pip install chromadb` |
| **Neo4j** | Graph database | `docker compose up -d` |
| **LightRAG** | RAG orchestration | `pip install lightrag-hku[api]` |
| **Unstructured** | Document parsing | `pip install unstructured[all-docs]` |

### Key Python Libraries

```
lightrag-hku[api]      # RAG pipeline orchestration
chromadb               # Vector store for embeddings
neo4j                  # Graph database driver
sentence-transformers  # Embedding fallback
unstructured[all-docs] # PDF/DOCX/HTML parsing
tiktoken               # Token counting for chunks
python-dotenv          # Environment configuration
```

### Testing Dependencies

```
pytest                 # Test framework
pytest-asyncio         # Async test support
pytest-cov             # Coverage reporting
```

---

## Architecture

### Local System Architecture

```
Structured Data               Unstructured Data
(CSV/JSON)                    (TXT/PDF/DOCX)
    ↓                              ↓
[Structured Handler]         [ETL Pipeline]
    ↓                              ↓
[Load & Validate]            [NER Extraction]
    ↓                              ↓
[No NER/Chunking]        [Entity & Relations]
    ↓                              ↓
[Graph Triples]          [Chunking & Triples]
    ↓                              ↓
    └──→ Neo4j Graph ←──┘
         (Entities & Relations)
              ↓
        ChromaDB Vectors
         (Embeddings)
              ↓
      [Hybrid Query]
              ↓
    [LLM Response]
```

---

## Next Steps

1. ✅ Run the default example: `python local_hybrid_rag.py`
2. ✅ Try both pipelines: `python demo_dual_ingestion.py`
3. ✅ Run the test suite: `pytest tests/ -v`
4. ✅ Review docs: `docs/DUAL_INGESTION.md` and `docs/TESTING.md`
5. ✅ Add your own data: CSV + TXT files in `sample_docs/`

---

For hackathon use

- **Speed**: Everything runs locally, no API latency
- **Privacy**: Your data never leaves your machine
- **Extensibility**: Modify NER patterns, entity types, and retrieval logic
- **Demo-ready**: Complete dual-pipeline example with sample data and comprehensive tests

This repo includes a compact hackathon-ready README + architecture notes (see `docs/ARCHITECTURE.md`) and a short slide deck (`slides.md`).

If you want me to produce a polished PowerPoint or an architecture SVG optimized for the hackathon, tell me and I will add it next.
