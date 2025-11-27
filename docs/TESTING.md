# Testing Guide — Dual Ingestion Pipeline

This guide explains how to test and verify your hybrid RAG system with both structured and unstructured data pipelines.

## Overview

The test suite consists of:

1. **`test_ingestion_pipeline.py`** — Integration test with LightRAG (requires Ollama + Neo4j running)
2. **`test_etl_pipeline.py`** — Unit tests for NER and entity/relation extraction
3. **`test_structured_handler.py`** — Unit tests for CSV/JSON ingestion and validation
4. **`test_integration.py`** — Integration tests combining both pipelines

---

## Quick Start

### Install test dependencies

```bash
pip install -r requirements.txt
```

### Run all tests

```bash
pytest tests/ -v
```

### Run specific test file

```bash
pytest tests/test_etl_pipeline.py -v
pytest tests/test_structured_handler.py -v
pytest tests/test_integration.py -v
```

### Run with coverage

```bash
pytest tests/ --cov=. --cov-report=html
```

---

## Test 1: Core LightRAG Integration (`test_ingestion_pipeline.py`)

### Prerequisites

Before running this test, ensure:

1. **Neo4j is running** (via Docker)
   ```bash
   docker compose up -d
   ```

2. **Ollama is running** with models pulled
   ```bash
   ollama serve &  # Background
   ollama pull llama3.1:8b
   ollama pull nomic-embed-text
   ```

3. **.env file is configured**
   ```bash
   cp .env.example .env
   # Update if using non-default credentials
   ```

### Run the test

```bash
python test_ingestion_pipeline.py
```

### What it tests

| Test | Input | Expected | Verifies |
|------|-------|----------|----------|
| **Structured Ingestion** | JSON | ChromaDB vectors only | Vector storage, no NER |
| **Unstructured Ingestion** | TXT | ChromaDB vectors + Neo4j triples | NER extraction, graph storage |
| **Hybrid Fusion** | Combined query | Results from both sources | Fusion and context awareness |
| **Neo4j Verification** | Graph query | Entities and relations | Triple generation |
| **ChromaDB Verification** | Vector query | Embedding vectors | Vector storage |

### Expected Output

```
======================================================================
TEST 1: STRUCTURED DATA INGESTION (JSON → ChromaDB only)
======================================================================
✓ Structured data inserted into RAG
✓ Structured data retrieved from ChromaDB

======================================================================
TEST 2: UNSTRUCTURED DATA INGESTION (TXT → NER + Graph + Vector)
======================================================================
✓ Unstructured data inserted into RAG
✓ Unstructured data retrieved via hybrid query

======================================================================
TEST 3: HYBRID FUSION (Structured + Unstructured)
======================================================================
✓ Hybrid fusion query successful

======================================================================
VERIFICATION: NEO4J GRAPH INSPECTION
======================================================================
Total nodes in Neo4j: 15
Sample entities:
  - Elon Musk (Person)
  - SpaceX (Organization)

Sample relations:
  - (Elon Musk) -[WORKS_AT]-> (SpaceX)
  - (SpaceX) -[LOCATED_IN]-> (Hawthorne)

======================================================================
VERIFICATION: CHROMADB VECTOR STORE INSPECTION
======================================================================
Chroma collections available: 1
  - default (42 vectors)

======================================================================
TEST SUMMARY
======================================================================
structured         ✓ PASS
unstructured       ✓ PASS
hybrid             ✓ PASS

OVERALL: 3/3 tests passed
🎉 ALL TESTS PASSED - Dual ingestion pipeline is working!
```

---

## Test 2: ETL Pipeline Unit Tests (`test_etl_pipeline.py`)

### What it tests

- **NER Extraction**: Person names, organizations, emails, URLs
- **Relation Detection**: WORKS_AT, FOUNDED, MANAGES, OWNS, LOCATED_IN
- **Entity Position Tracking**: Start/end character positions are accurate
- **Text Chunking**: Text is split correctly with overlap
- **Graph Triple Generation**: Triples have correct structure
- **Edge Cases**: Empty text, special characters, Unicode

### Run tests

```bash
pytest tests/test_etl_pipeline.py -v
```

### Sample test output

```
test_etl_pipeline.py::TestSimpleNERExtractor::test_extract_person_names PASSED
test_etl_pipeline.py::TestSimpleNERExtractor::test_extract_organizations PASSED
test_etl_pipeline.py::TestSimpleNERExtractor::test_extract_emails PASSED
test_etl_pipeline.py::TestRelationExtractor::test_works_at_relation PASSED
test_etl_pipeline.py::TestUnstructuredETLPipeline::test_process_simple_text PASSED
test_etl_pipeline.py::TestUnstructuredETLPipeline::test_entity_count_in_metadata PASSED
test_etl_pipeline.py::TestUnstructuredETLPipeline::test_chunking PASSED
test_etl_pipeline.py::TestETLPipelineEdgeCases::test_empty_text PASSED
test_etl_pipeline.py::TestETLPipelineEdgeCases::test_unicode_text PASSED

====== 27 passed in 0.42s ======
```

### Key test scenarios

#### Test 1: Entity Extraction
```python
text = "Alice Johnson works at Acme Corp. Bob Smith is her manager."
# Should extract: Alice, Bob, Acme Corp
```

#### Test 2: Relation Extraction
```python
text = "Alice is a manager at Acme Corp"
# Should extract: Alice -[WORKS_AT]-> Acme Corp
```

#### Test 3: Text Chunking
```python
# Long text (600 words) with chunk_size=512
# Should produce 2+ chunks with overlap
```

#### Test 4: Triple Generation
```python
# For each entity: (entity, HAS_TYPE, entity_type)
# For each relation: (head, relation_type, tail)
# For document link: (entity, MENTIONED_IN, document_id)
```

---

## Test 3: Structured Handler Unit Tests (`test_structured_handler.py`)

### What it tests

- **CSV Ingestion**: Load, parse, handle delimiters
- **JSON Ingestion**: Array, single object, JSONL formats
- **ID Mapping**: Custom ID columns/fields
- **Record Validation**: Check required fields
- **Triple Conversion**: Records to graph triples
- **Edge Cases**: Empty files, special chars, malformed data

### Run tests

```bash
pytest tests/test_structured_handler.py -v
```

### Sample test output

```
test_structured_handler.py::TestStructuredDataHandler::test_csv_ingestion_basic PASSED
test_structured_handler.py::TestStructuredDataHandler::test_csv_with_id_column PASSED
test_structured_handler.py::TestStructuredDataHandler::test_json_array_ingestion PASSED
test_structured_handler.py::TestStructuredDataHandler::test_validate_records_success PASSED
test_structured_handler.py::TestStructuredDataHandler::test_validate_records_missing_field PASSED
test_structured_handler.py::TestStructuredHandlerEdgeCases::test_large_csv PASSED

====== 31 passed in 0.56s ======
```

### Key test scenarios

#### Test 1: CSV with custom ID
```csv
employee_id,name,department
101,Alice,Engineering
102,Bob,Sales
```
→ Records have IDs: "101", "102"

#### Test 2: JSON with nested data
```json
[
  {
    "id": 1,
    "name": "Alice",
    "address": {"city": "NYC", "zip": "10001"}
  }
]
```
→ Nested structure preserved in record data

#### Test 3: Validation with required fields
```python
required_fields=['name', 'email']
# Record without 'email' → rejected
```

#### Test 4: Record to triples
```python
record = {"id": "1", "name": "Alice", "role": "Engineer"}
# Generated triples:
# (1, HAS_TYPE, Record)
# (1, NAME, Alice)
# (1, ROLE, Engineer)
```

---

## Test 4: Integration Tests (`test_integration.py`)

### What it tests

- **Cross-pipeline linking**: Match entities from unstructured to structured
- **Batch processing**: Handle multiple files simultaneously
- **Data consistency**: Entities are consistent across pipelines
- **Triple integrity**: Generated triples form valid graphs
- **Fault tolerance**: Handle malformed data gracefully

### Run tests

```bash
pytest tests/test_integration.py -v
```

### Sample test output

```
test_integration.py::TestETLStructuredIntegration::test_unstructured_to_structured_mapping PASSED
test_integration.py::TestETLStructuredIntegration::test_batch_unstructured_processing PASSED
test_integration.py::TestETLStructuredIntegration::test_cross_pipeline_entity_linking PASSED
test_integration.py::TestDataConsistency::test_entity_deduplication PASSED
test_integration.py::TestPipelineInteroperability::test_structured_entities_to_etl_triples PASSED

====== 23 passed in 1.85s ======
```

---

## Troubleshooting

### LightRAG Test Fails

**Error**: `"Couldn't import LightRAG"`

**Solution**:
```bash
pip install lightrag-hku[api]
```

### Neo4j Connection Error

**Error**: `"Could not connect to Neo4j"`

**Solution**:
```bash
docker compose up -d
# Wait ~10 seconds for Neo4j to start
```

### Ollama Not Found

**Error**: `"Model not found: llama3.1:8b"`

**Solution**:
```bash
ollama pull llama3.1:8b
ollama pull nomic-embed-text
```

### Async Test Fails

**Error**: `"coroutine was never awaited"`

**Solution**: Ensure pytest-asyncio is installed:
```bash
pip install pytest-asyncio
```

### ChromaDB Empty

**Error**: `"ChromaDB is empty"`

**Solution**: This is expected if LightRAG isn't doing automatic embedding. Check that:
- Ollama is running
- nomic-embed-text model is pulled
- LightRAG embedding_func is configured

---

## Coverage Report

Generate a coverage report:

```bash
pytest tests/ --cov=. --cov-report=html
open htmlcov/index.html  # View in browser
```

Expected coverage:

| Module | Coverage |
|--------|----------|
| etl_pipeline.py | 85%+ |
| structured_handler.py | 90%+ |
| local_hybrid_rag.py | 70%+ |
| lightrag_helpers.py | 100% |

---

## Performance Benchmarks

Typical test execution times (on modern laptop):

| Test Suite | Count | Time |
|-----------|-------|------|
| Unit tests (ETL) | 27 | 0.4s |
| Unit tests (Structured) | 31 | 0.6s |
| Integration tests | 23 | 1.9s |
| **Full suite** | **81** | **~3s** |
| LightRAG integration | 3 | 30–60s* |

*Depends on Ollama LLM speed

---

## Running Tests in CI/CD

### GitHub Actions example

```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      neo4j:
        image: neo4j:latest
        env:
          NEO4J_AUTH: neo4j/password
        options: >-
          --health-cmd "cypher-shell -u neo4j -p password 'RETURN 1'"
          --health-interval 10s
          --health-timeout 5s

    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: pytest tests/ --cov=.
```

---

## Continuous Testing

Watch for changes and run tests automatically:

```bash
pip install pytest-watch
ptw tests/ -- -v
```

---

## Next Steps

1. ✅ Run unit tests first (fast, no dependencies)
   ```bash
   pytest tests/test_etl_pipeline.py tests/test_structured_handler.py -v
   ```

2. ✅ Run integration tests (verify pipeline connectivity)
   ```bash
   pytest tests/test_integration.py -v
   ```

3. ✅ Run LightRAG integration test (end-to-end with real storage)
   ```bash
   python test_ingestion_pipeline.py
   ```

4. ✅ Check coverage
   ```bash
   pytest tests/ --cov=. --cov-report=term-missing
   ```

5. ✅ Try with your own data
   ```bash
   python local_hybrid_rag.py --structured data/mydata.csv --unstructured docs/mydoc.txt
   ```

---
