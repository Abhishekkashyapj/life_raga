# Local Hybrid RAG — Hackathon Pitch

## Slide 1 — Problem
- Searching across docs is slow and isolated (vectors or graphs alone are not enough)

## Slide 2 — Our Approach
- Hybrid retrieval combining dense vector search (Chroma) + structured graph relations (Neo4j)
- Local-first. No cloud needed — keep data private and fast.

## Slide 3 — Architecture
- Ingest -> Unstructured text extraction -> Chunking -> Embeddings (Ollama/nomic-embed-text)
- Store embeddings in Chroma + entities/relations in Neo4j
- Query: hybrid fuse vector results + graph traversal -> LLM answer generation

## Slide 4 — Demo
- Show local_hybrid_rag.py ingest + query
- Show LightRAG UI at http://localhost:8000 (optional)

## Slide 5 — Next steps
- Add Dockerized demo orchestrating everything
- Add UI and interactive demo, tweaking context windows
