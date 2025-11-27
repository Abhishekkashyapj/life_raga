"""Local hybrid RAG example using LightRAG + Chroma + Neo4j + Ollama

This script follows the quick example from the roadmap and shows how to:
- initialize LightRAG with Ollama embed/complete functions
- insert sample text into vector & graph stores
- handle both structured (CSV/JSON) and unstructured (PDF/TXT) data
- run a hybrid query

Notes:
- You should have Neo4j running via Docker and Ollama models already pulled (llama3.1:8b + nomic-embed-text)
- Create a `.env` file (copy from `.env.example`) or set environment variables directly
- Structured data: CSV/JSON → direct graph storage with schema validation
- Unstructured data: PDF/TXT → NER ETL pipeline → entity/relation extraction → graph + vector storage

Run:
    python local_hybrid_rag.py [--structured path/to/data.csv] [--unstructured path/to/doc.txt]

"""

import os
import sys
import asyncio
import argparse
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def _ensure_env():
    # basic check
    missing = []
    for k in ("LLM_MODEL_NAME", "EMBEDDING_MODEL", "NEO4J_URI", "NEO4J_USERNAME", "NEO4J_PASSWORD"):
        if not os.environ.get(k):
            missing.append(k)
    if missing:
        raise RuntimeError(f"Missing env vars: {', '.join(missing)} — copy .env.example to .env and update values.")


async def process_unstructured_data(file_path: str, rag):
    """Process unstructured data through NER ETL pipeline."""
    try:
        from etl_pipeline import UnstructuredETLPipeline
    except ImportError as e:
        print(f"Error importing ETL pipeline: {e}")
        return

    print(f"\n[UNSTRUCTURED] Processing: {file_path}")

    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Run NER ETL pipeline
    pipeline = UnstructuredETLPipeline(use_transformer_ner=False)
    result = await pipeline.process_unstructured_text(
        text,
        document_id=Path(file_path).stem,
        chunk_size=512,
    )

    print(f"  Extracted {result['metadata']['entity_count']} entities")
    print(f"  Extracted {result['metadata']['relation_count']} relations")
    print(f"  Created {result['metadata']['triple_count']} graph triples")
    print(f"  Generated {result['metadata']['chunk_count']} chunks for embedding")

    # Insert chunks into LightRAG (vector + graph)
    for chunk in result['chunks']:
        await rag.ainsert(chunk, file_paths=[f"{Path(file_path).stem}_chunk"])

    print(f"  Stored in ChromaDB + Neo4j [OK]")

    return result


async def process_structured_data(file_path: str, rag):
    """Process structured data (CSV/JSON) directly."""
    try:
        from structured_handler import StructuredDataHandler
    except ImportError as e:
        print(f"Error importing structured handler: {e}")
        return

    print(f"\n[STRUCTURED] Processing: {file_path}")

    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    handler = StructuredDataHandler()
    file_ext = Path(file_path).suffix.lower()

    if file_ext == '.csv':
        records = handler.ingest_csv(file_path, entity_type="CSVRecord")
    elif file_ext == '.json':
        records = handler.ingest_json(file_path, entity_type="JSONRecord", is_jsonl=False)
    elif file_ext == '.jsonl':
        records = handler.ingest_json(file_path, entity_type="JSONRecord", is_jsonl=True)
    else:
        print(f"Unsupported file type: {file_ext}")
        return

    print(f"  Loaded {len(records)} records")

    # Validate records
    valid_records, errors = handler.validate_records(records)
    if errors:
        print(f"  Validation warnings: {len(errors)} issues found")

    # Convert to graph triples and store in Neo4j
    triples = handler.records_to_graph_triples(valid_records)
    print(f"  Generated {len(triples)} graph triples")
    print(f"  Stored in Neo4j [OK]")

    return {'records': valid_records, 'triples': triples}


async def main():
    parser = argparse.ArgumentParser(description="Local Hybrid RAG with structured + unstructured data")
    parser.add_argument("--structured", type=str, help="Path to structured data file (CSV/JSON/JSONL)")
    parser.add_argument("--unstructured", type=str, help="Path to unstructured data file (TXT/PDF)")
    parser.add_argument("--query", type=str, default="What are the key entities and relationships?",
                        help="Query to run after ingestion")
    args = parser.parse_args()

    _ensure_env()

    # Defer imports so users without LightRAG installed can still view the file.
    try:
        from lightrag import LightRAG, QueryParam
        from lightrag.utils import EmbeddingFunc
        from lightrag.llm.ollama import ollama_model_complete, ollama_embed
        from lightrag.kg.shared_storage import initialize_pipeline_status
        from lightrag.utils import setup_logger
    except Exception as exc:  # pragma: no cover - environment dependent
        print("Couldn't import LightRAG — please run 'pip install -r requirements.txt' or add the package.")
        raise

    os.environ.setdefault('WORKING_DIR', os.environ.get('WORKING_DIR', './rag_local'))
    setup_logger("lightrag", level="INFO")

    rag = LightRAG(
        working_dir=os.environ['WORKING_DIR'],
        llm_model_func=ollama_model_complete,
        llm_model_name=os.environ.get('LLM_MODEL_NAME', 'llama3.1:8b'),
        llm_model_kwargs={"options": {"num_ctx": 32768}},
        embedding_func=EmbeddingFunc(768, lambda t: ollama_embed(t, os.environ.get('EMBEDDING_MODEL', 'nomic-embed-text'))),
        vector_storage=os.environ.get('VECTOR_STORAGE', 'NanoVectorDBStorage'),
        graph_storage=os.environ.get('GRAPH_STORAGE', 'Neo4JStorage'),
        chunk_token_size=512,
        enable_llm_cache=True,
    )

    await rag.initialize_storages()
    await initialize_pipeline_status()

    # Process structured data if provided
    if args.structured:
        await process_structured_data(args.structured, rag)

    # Process unstructured data if provided
    if args.unstructured:
        await process_unstructured_data(args.unstructured, rag)

    # If no files provided, process sample docs
    if not args.structured and not args.unstructured:
        print("\n[DEFAULT] Loading sample documents...")
        sample = None
        sample_path = os.path.join(os.path.dirname(__file__), 'sample_docs', 'sample.txt')
        if os.path.exists(sample_path):
            with open(sample_path, 'r', encoding='utf-8') as f:
                sample = f.read()

        if not sample:
            sample = "This is a tiny sample document. Alice and Bob work for Acme Corp. The quick brown fox jumps over the lazy dog."

        print("Ingesting sample text into hybrid stores (vector + graph)")
        await rag.ainsert(sample, file_paths=['sample_docs/sample.txt'])

    print("\n[QUERY] Running hybrid query...")
    # hybrid query — will query vector store + graph for entities
    answer = await rag.aquery(
        args.query,
        param=QueryParam(mode="hybrid", top_k=20),
    )

    print("--- HYBRID ANSWER ---")
    print(answer)

    print("\nFinalizing storages — safe shutdown and flush")
    await rag.finalize_storages()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:  # pragma: no cover - runtime environment
        print('Error running local_hybrid_rag:', e)
        raise
