# Dual Data Ingestion Pipelines — Structured + Unstructured

This guide explains how to use the hybrid ingestion system for both structured and unstructured data.

## Overview

The system provides **two complementary pipelines**:

1. **Unstructured Pipeline** — NER-based ETL for text documents
2. **Structured Pipeline** — Direct ingestion for CSV/JSON data

Both feed into the same hybrid vector + graph storage (ChromaDB + Neo4j).

---

## Pipeline 1: Unstructured Data (NER ETL Pipeline)

### What it does

- **Input**: Raw text (PDF, TXT, DOCX, etc.)
- **Process**:
  1. Named Entity Recognition (NER) — extracts entities (PERSON, ORG, LOC, PRODUCT, etc.)
  2. Relation Extraction — detects relationships between entities
  3. Graph Triple Generation — creates (subject, predicate, object) tuples
  4. Text Chunking — splits text into overlapping chunks for embeddings
- **Output**: 
  - Entities and relations stored in Neo4j
  - Text chunks embedded and stored in ChromaDB
  - Full triples for graph traversal during queries

### Usage

```python
from etl_pipeline import UnstructuredETLPipeline

pipeline = UnstructuredETLPipeline(use_transformer_ner=False)
result = await pipeline.process_unstructured_text(
    text="Alice works at Acme Corp. Bob manages Alice.",
    document_id="doc_001",
    chunk_size=512,
)

# result contains:
# - result['entities']: list of extracted entities
# - result['relations']: list of extracted relations
# - result['graph_triples']: (subject, predicate, object) for Neo4j
# - result['chunks']: text chunks for embedding
```

### Available Entity Types

- `PERSON` — names of people
- `ORG` — organization/company names
- `LOC` — locations
- `EMAIL` — email addresses
- `URL` — web URLs
- `PRODUCT` — product/software names

### Relation Types

- `WORKS_AT` — person works at organization
- `FOUNDED` — person founded organization
- `MANAGES` — person manages another person/entity
- `OWNS` — person/org owns something
- `LOCATED_IN` — entity located in location

### Note on NER

The default uses **rule-based regex patterns** (fast, no model download). For higher accuracy, enable transformer-based NER:

```python
pipeline = UnstructuredETLPipeline(use_transformer_ner=True)
# Downloads BERT multilingual NER model on first use (~200MB)
```

---

## Pipeline 2: Structured Data (Direct Storage)

### What it does

- **Input**: CSV, JSON, or JSONL files
- **Process**:
  1. Load records from file
  2. Validate against optional schema
  3. Convert records to graph triples
  4. Store directly in Neo4j (no embedding needed)
- **Output**: 
  - Records stored as nodes in Neo4j
  - Property relationships for each field
  - Source tracking for audit trails

### Usage

```python
from structured_handler import StructuredDataHandler

handler = StructuredDataHandler()

# Ingest CSV
records = handler.ingest_csv(
    'employees.csv',
    entity_type='Employee',
    id_column='id'
)

# Ingest JSON
records = handler.ingest_json(
    'companies.json',
    entity_type='Company',
    id_field='company_id',
    is_jsonl=False
)

# Convert to graph triples for Neo4j
triples = handler.records_to_graph_triples(records)
# Each triple: (record_id, FIELD_NAME, field_value)

# Validate records against schema
valid_records, errors = handler.validate_records(
    records,
    required_fields=['id', 'name', 'email']
)
```

### CSV Example

```csv
id,name,title,company
1,Alice,Engineering Lead,Acme Corp
2,Bob,Product Manager,Acme Corp
3,Charlie,Data Scientist,TechCorp
```

### JSON Example

```json
[
  {
    "id": "acme-001",
    "name": "Acme Corporation",
    "founded": "2010",
    "industry": "Software"
  }
]
```

### Graph Triples Generated

For a record `Alice (id=1)`:

```
(1, HAS_TYPE, Employee)
(1, NAME, Alice)
(1, TITLE, Engineering Lead)
(1, COMPANY, Acme Corp)
(1, FROM_SOURCE, employees.csv)
```

---

## Integration with LightRAG

### Command-line Usage

```bash
# Unstructured only
python local_hybrid_rag.py --unstructured docs/report.txt

# Structured only
python local_hybrid_rag.py --structured data/employees.csv

# Both pipelines
python local_hybrid_rag.py --structured data/employees.csv --unstructured docs/report.txt

# Custom query
python local_hybrid_rag.py --structured data/employees.csv --query "Who works where?"
```

### Programmatic Usage

```python
import asyncio
from local_hybrid_rag import process_unstructured_data, process_structured_data

async def main():
    # Initialize RAG
    from lightrag import LightRAG
    rag = LightRAG(...)
    
    # Process structured data
    struct_result = await process_structured_data('data.csv', rag)
    
    # Process unstructured data
    unstruct_result = await process_unstructured_data('docs/text.txt', rag)
    
    # Query both
    answer = await rag.aquery(
        "Find relationships between people and companies",
        param=QueryParam(mode="hybrid", top_k=20)
    )
```

---

## Storage Architecture

### Neo4j Graph Structure

```
Nodes:
  - Entities from unstructured (PERSON, ORG, LOC)
  - Records from structured (Employee, Company)
  - Document references
  - Entity types and relations

Relationships:
  - HAS_TYPE (entity has type)
  - WORKS_AT (from unstructured relations)
  - MANAGES, OWNS, LOCATED_IN, etc.
  - FROM_SOURCE (which file/document)
  - MENTIONED_IN (entities in documents)
```

### ChromaDB Vector Index

```
Vectors:
  - Chunks from unstructured text only
  - Embedded using nomic-embed-text
  - No embedding for structured data (stays in graph)
```

---

## Data Flow Diagram

```
Structured Data (CSV/JSON)     Unstructured Data (TXT/PDF)
       |                                    |
       v                                    v
[Load]                                   [Extract Text]
  |                                        |
  v                                        v
[Ingest]                              [NER Pipeline]
  |                                        |
  v                                        v
[Validate Schema]              [Entity/Relation Extract]
  |                                        |
  v                                        v
[Generate Triples]            [Triple Generation]
  |                            [Chunk & Embed]
  |                                    |
  +-------- Neo4j Graph DB ----------+
  |                                    |
  +---- ChromaDB (vectors only) ------+
           |
           v
      [Hybrid Query]
           |
           v
      [LLM Fusion]
           |
           v
      [Answer]
```

---

## Best Practices

### For Structured Data

- Use CSV for tabular data (employees, transactions, etc.)
- Use JSON for hierarchical/nested data (configs, metadata)
- Always specify an `id_column` or `id_field` for unique tracking
- Validate schema for data quality

### For Unstructured Data

- Use rule-based NER (default) for speed; transformer NER for accuracy
- Chunk size ~512 chars ≈ 100–150 tokens
- Keep chunk overlap ~50% for better retrieval
- Consider preprocessing (lowercase, remove special chars) for better NER

### For Hybrid Queries

- Use `mode="hybrid"` to fuse vector + graph results
- Set `top_k=20` for balanced coverage
- Graph traversal uses 1–2 hops by default
- Entity-centric queries perform best (e.g., "Find all people and their companies")

---

## Example: E2E Workflow

```python
import asyncio
from pathlib import Path

async def e2e_demo():
    # 1. Initialize pipelines
    from etl_pipeline import UnstructuredETLPipeline
    from structured_handler import StructuredDataHandler
    
    unstructured_pipeline = UnstructuredETLPipeline()
    structured_handler = StructuredDataHandler()
    
    # 2. Process structured data
    employees = structured_handler.ingest_csv('employees.csv', entity_type='Employee')
    emp_triples = structured_handler.records_to_graph_triples(employees)
    print(f"Structured: {len(employees)} employees → {len(emp_triples)} triples")
    
    # 3. Process unstructured data
    with open('project_notes.txt') as f:
        text = f.read()
    result = await unstructured_pipeline.process_unstructured_text(text)
    print(f"Unstructured: {len(result['entities'])} entities, {len(result['chunks'])} chunks")
    
    # 4. Store in graph + vector DB
    # [LightRAG handles this]
    
    # 5. Query
    # "Who works where?" → finds Employee nodes + WORKS_AT relations
    # "What are the key projects?" → finds entities in documents + relationships
```

---

## Troubleshooting

### NER gives poor results

- Switch to transformer-based: `UnstructuredETLPipeline(use_transformer_ner=True)`
- Pre-process text: lowercase, remove extra whitespace
- Add domain-specific patterns to `SimpleNERExtractor`

### Structured data validation fails

- Check required fields: `validate_records(records, required_fields=['id', 'name'])`
- Inspect sample records: `print(records[0].data)`
- Use try/except for malformed files

### Graph gets too large

- Limit NER entity types to relevant ones
- Use 1 hop instead of 2 for graph traversal
- Archive old documents to separate Neo4j instance

---

## Next Steps

1. Run the demo:
   ```bash
   python demo_dual_ingestion.py
   ```

2. Try both pipelines:
   ```bash
   python local_hybrid_rag.py --structured sample_docs/employees.csv --unstructured sample_docs/project_notes.txt
   ```

3. Customize entity types and relations in `etl_pipeline.py`

4. Add your own CSV/JSON + documents and query

---
