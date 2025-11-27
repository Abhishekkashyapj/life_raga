## Local Hybrid RAG — Architecture

High-level components:

- Ollama (LLM + embedding models) — provides completion and embeddings locally.
- LightRAG — ingestion, chunking, entity extraction, orchestration layer.
- ChromaDB — local vector store for dense retrieval.
- Neo4j — local graph DB for entities and relations.

Mermaid diagram (copy this into a mermaid renderer):

```mermaid
flowchart LR
    A[Documents: PDF, DOCX, CSV, TXT] -->|unstructured extraction| B(LightRAG Ingest)
    B -->|chunking| C[Chunks]
    C -->|embed| D[Ollama embeddings]
    D -->|store| E[ChromaDB (Vectors)]
    B -->|entity extraction| F[Entities & Triples]
    F -->|store| G[Neo4j (Graph)]
    E -->|vector search| H[Vector hits]
    G -->|graph traversal| I[Graph neighbors]
    H -->|fusion| J[Hybrid Fusion]
    I -->|fusion| J
    J -->|LLM| K[Ollama completion -> final answer]
```

Notes and tips:

- Use chunk sizes around 512 tokens and overlap ~50 tokens.
- Vector top_k = 10–20 for fusion.
- Graph hops = 1–2 to avoid exploding subgraphs in large datasets.
