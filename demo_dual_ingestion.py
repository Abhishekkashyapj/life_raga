"""Demo script showing both structured and unstructured data ingestion pipelines.

This script demonstrates:
1. Processing structured data (CSV, JSON) → direct Neo4j storage
2. Processing unstructured text → NER ETL pipeline → entity/relation extraction → storage
3. Hybrid querying across both data types

Run:
    python demo_dual_ingestion.py

"""

import asyncio
import os
from pathlib import Path
from etl_pipeline import UnstructuredETLPipeline, process_unstructured_batch
from structured_handler import StructuredDataHandler, ingest_structured_batch


async def demo_unstructured_etl():
    """Demo: Process unstructured text through NER ETL pipeline."""
    print("\n" + "="*70)
    print("DEMO 1: UNSTRUCTURED DATA ETL PIPELINE (NER + Entity Extraction)")
    print("="*70)

    # Sample text
    text = """
    Alice Johnson is the Engineering Lead at Acme Corporation. She manages Bob Smith, 
    who is a Senior Software Engineer. Together they built the hybrid RAG system.
    
    Charlie Brown from TechCorp Inc contributed to the project. The project was led 
    by Diana Prince, the CTO of TechCorp.
    
    The system is deployed on-premise using Ollama for local LLM inference.
    """

    pipeline = UnstructuredETLPipeline(use_transformer_ner=False)
    result = await pipeline.process_unstructured_text(
        text,
        document_id="project_notes_v1",
        chunk_size=512,
    )

    print("\n[ENTITIES EXTRACTED]")
    for entity in result['entities']:
        print(f"  - {entity['name']:20} ({entity['entity_type']:10}) | confidence: {entity['confidence']}")

    print("\n[RELATIONS EXTRACTED]")
    for relation in result['relations']:
        print(f"  - {relation['head_entity']:15} --[{relation['relation_type']}]--> {relation['tail_entity']:15}")

    print("\n[GRAPH TRIPLES] (sample)")
    for triple in result['graph_triples'][:10]:
        print(f"  - ({triple['subject']}) --[{triple['predicate']}]--> ({triple['obj']})")

    print(f"\n[METADATA]")
    for key, val in result['metadata'].items():
        print(f"  - {key}: {val}")

    return result


async def demo_structured_csv():
    """Demo: Process CSV structured data."""
    print("\n" + "="*70)
    print("DEMO 2: STRUCTURED DATA INGESTION (CSV)")
    print("="*70)

    csv_path = Path(__file__).parent / 'sample_docs' / 'employees.csv'

    if not csv_path.exists():
        print(f"Sample CSV not found at {csv_path}")
        return None

    handler = StructuredDataHandler()
    records = handler.ingest_csv(csv_path, entity_type="Employee", id_column="id")

    print(f"\n[LOADED {len(records)} RECORDS]")
    for record in records[:3]:
        print(f"  - ID: {record.record_id}, Data: {record.data}")

    # Validate
    valid_records, errors = handler.validate_records(records)
    print(f"\n[VALIDATION] Valid: {len(valid_records)}, Errors: {len(errors)}")

    # Convert to triples
    triples = handler.records_to_graph_triples(valid_records)
    print(f"\n[GRAPH TRIPLES GENERATED] {len(triples)} triples")
    for triple in triples[:10]:
        print(f"  - {triple}")

    return records


async def demo_structured_json():
    """Demo: Process JSON structured data."""
    print("\n" + "="*70)
    print("DEMO 3: STRUCTURED DATA INGESTION (JSON)")
    print("="*70)

    json_path = Path(__file__).parent / 'sample_docs' / 'companies.json'

    if not json_path.exists():
        print(f"Sample JSON not found at {json_path}")
        return None

    handler = StructuredDataHandler()
    records = handler.ingest_json(json_path, entity_type="Company", id_field="company_id", is_jsonl=False)

    print(f"\n[LOADED {len(records)} RECORDS]")
    for record in records:
        print(f"  - ID: {record.record_id}, Name: {record.data.get('company_name')}")

    # Convert to triples
    triples = handler.records_to_graph_triples(records)
    print(f"\n[GRAPH TRIPLES GENERATED] {len(triples)} triples")
    for triple in triples[:10]:
        print(f"  - {triple}")

    return records


async def demo_batch_processing():
    """Demo: Process multiple files in batch."""
    print("\n" + "="*70)
    print("DEMO 4: BATCH PROCESSING (Multiple files)")
    print("="*70)

    base_path = Path(__file__).parent / 'sample_docs'
    csv_path = base_path / 'employees.csv'
    json_path = base_path / 'companies.json'

    if csv_path.exists() and json_path.exists():
        handler = StructuredDataHandler()
        file_list = [
            (str(csv_path), 'csv'),
            (str(json_path), 'json'),
        ]

        all_records = await ingest_structured_batch(file_list, handler)
        print(f"\n[BATCH RESULT] Total records ingested: {len(all_records)}")
        for record in all_records[:3]:
            print(f"  - {record.record_id} ({record.entity_type}) from {record.source_file}")
    else:
        print("Sample files not available for batch processing demo")


async def main():
    """Run all demos."""
    print("\n" + "*"*70)
    print("HYBRID RAG - DUAL INGESTION PIPELINE DEMO")
    print("*"*70)

    # Demo 1: Unstructured ETL
    result_unstructured = await demo_unstructured_etl()

    # Demo 2: CSV Structured
    result_csv = await demo_structured_csv()

    # Demo 3: JSON Structured
    result_json = await demo_structured_json()

    # Demo 4: Batch Processing
    await demo_batch_processing()

    print("\n" + "*"*70)
    print("SUMMARY")
    print("*"*70)
    print("""
    This demo showed:
    
    1. UNSTRUCTURED PIPELINE:
       - NER-based entity extraction from raw text
       - Relation detection between entities
       - Automatic graph triple generation
       - Text chunking for embedding storage
       
    2. STRUCTURED PIPELINE:
       - CSV/JSON ingestion with schema validation
       - Direct graph storage (no embedding needed)
       - Bulk record processing
       - Flexible ID and entity type mapping
       
    3. BATCH PROCESSING:
       - Multiple file formats in one pass
       - Consolidated result aggregation
       
    Next steps:
    - Use local_hybrid_rag.py --structured <file> --unstructured <file>
    - Query the hybrid system with both entity and relation context
    - Export graph visualization from Neo4j
    """)


if __name__ == '__main__':
    asyncio.run(main())
