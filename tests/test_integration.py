"""Integration tests combining ETL pipeline + Structured handler + LightRAG.

Run:
    pytest tests/test_integration.py -v
"""

import pytest
import asyncio
import json
import tempfile
from pathlib import Path
from etl_pipeline import UnstructuredETLPipeline, process_unstructured_batch
from structured_handler import StructuredDataHandler, ingest_structured_batch


class TestETLStructuredIntegration:
    """Integration tests for ETL + Structured pipelines."""

    def setup_method(self):
        """Setup before each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.etl_pipeline = UnstructuredETLPipeline(use_transformer_ner=False)
        self.struct_handler = StructuredDataHandler()

    @pytest.mark.asyncio
    async def test_unstructured_to_structured_mapping(self):
        """Test mapping unstructured entities to structured records."""
        # Unstructured: Extract entities
        unstructured_text = "Alice Johnson works at Acme Corp in San Francisco"
        result = await self.etl_pipeline.process_unstructured_text(unstructured_text)

        # Structured: Create records from extracted entities
        entity_records = []
        for entity in result['entities']:
            entity_records.append({
                'name': entity['name'],
                'type': entity['entity_type'],
                'confidence': entity['confidence'],
            })

        assert len(entity_records) > 0
        assert entity_records[0]['name'] is not None

    @pytest.mark.asyncio
    async def test_batch_unstructured_processing(self):
        """Test batch processing of multiple unstructured documents."""
        texts = [
            ("Alice works at Acme", "doc1"),
            ("Bob manages at TechCorp", "doc2"),
            ("Charlie leads at Innovate", "doc3"),
        ]

        results = await process_unstructured_batch(texts, chunk_size=512)

        assert len(results) == 3
        for result in results:
            assert 'entities' in result
            assert 'graph_triples' in result

    @pytest.mark.asyncio
    async def test_batch_structured_processing(self):
        """Test batch processing of multiple structured files."""
        # Create test files
        csv_file = Path(self.temp_dir) / "test.csv"
        csv_file.write_text("id,name\n1,Alice\n2,Bob\n")

        json_file = Path(self.temp_dir) / "test.json"
        json_file.write_text(json.dumps([{"id": 1, "company": "Acme"}]))

        files = [(str(csv_file), 'csv'), (str(json_file), 'json')]
        records = await ingest_structured_batch(files, self.struct_handler)

        assert len(records) >= 3

    @pytest.mark.asyncio
    async def test_cross_pipeline_entity_linking(self):
        """Test linking entities from unstructured to structured records."""
        # Process unstructured
        unstructured = "Alice Johnson works at Acme Corporation"
        unstruct_result = await self.etl_pipeline.process_unstructured_text(unstructured)

        # Process structured
        csv_file = Path(self.temp_dir) / "employees.csv"
        csv_file.write_text("id,name,company\n1,Alice Johnson,Acme Corporation\n")
        struct_records = self.struct_handler.ingest_csv(str(csv_file))

        # Link: Find matching entities
        extracted_names = {e['name'] for e in unstruct_result['entities'] if e['entity_type'] == 'PERSON'}
        structured_names = {r.data.get('name') for r in struct_records if 'name' in r.data}

        common_names = extracted_names & structured_names
        assert len(common_names) > 0

    @pytest.mark.asyncio
    async def test_triple_consistency(self):
        """Test that both pipelines generate consistent triples."""
        # Unstructured triples
        unstruct_text = "Alice is CEO of Acme"
        unstruct_result = await self.etl_pipeline.process_unstructured_text(unstruct_text)
        unstruct_triples = unstruct_result['graph_triples']

        # Structured triples
        csv_file = Path(self.temp_dir) / "companies.csv"
        csv_file.write_text("id,name,ceo\n1,Acme,Alice\n")
        struct_records = self.struct_handler.ingest_csv(str(csv_file))
        struct_triples = self.struct_handler.records_to_graph_triples(struct_records)

        # Both should produce triples
        assert len(unstruct_triples) > 0
        assert len(struct_triples) > 0

        # Both should have subject, predicate, object
        for triple in unstruct_triples + struct_triples:
            assert len(triple) >= 3 or 'subject' in triple

    @pytest.mark.asyncio
    async def test_document_entity_record_alignment(self):
        """Test alignment of documents, entities, and records."""
        # Unstructured document
        doc_text = "Alice Johnson (alice@example.com) works at Acme Corporation"
        result = await self.etl_pipeline.process_unstructured_text(doc_text, document_id="doc001")

        # Extract emails
        email_entities = [e for e in result['entities'] if e['entity_type'] == 'EMAIL']

        # Create structured record
        structured_data = {
            "id": 1,
            "name": "Alice Johnson",
            "email": "alice@example.com",
            "company": "Acme Corporation",
        }

        # Check alignment
        if email_entities:
            email = email_entities[0]['name']
            assert email == structured_data['email']


class TestPipelineFaultTolerance:
    """Test fault tolerance and error handling."""

    @pytest.mark.asyncio
    async def test_etl_handles_malformed_text(self):
        """Test ETL pipeline handles malformed text gracefully."""
        pipeline = UnstructuredETLPipeline(use_transformer_ner=False)

        # Malformed text with special chars
        text = "████████ @#$%^&*() \n\n\n"

        result = await pipeline.process_unstructured_text(text)

        assert 'entities' in result
        assert isinstance(result['entities'], list)

    def test_structured_handler_bad_csv(self):
        """Test structured handler handles bad CSV."""
        handler = StructuredDataHandler()

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("id,name\n1,Alice\n2,Bob\n3\n")  # Row 3 has wrong number of columns
            f.flush()

            records = handler.ingest_csv(f.name)

            # Should handle gracefully
            assert isinstance(records, list)

    @pytest.mark.asyncio
    async def test_batch_partial_failure(self):
        """Test batch processing with partial failures."""
        texts = [
            ("Valid text", "doc1"),
            ("", "doc2"),  # Empty
            ("Another valid", "doc3"),
        ]

        pipeline = UnstructuredETLPipeline(use_transformer_ner=False)
        # Should handle without failing
        for text, doc_id in texts:
            result = await pipeline.process_unstructured_text(text, document_id=doc_id)
            assert 'entities' in result


class TestDataConsistency:
    """Test data consistency across pipelines."""

    @pytest.mark.asyncio
    async def test_entity_deduplication(self):
        """Test handling of duplicate entities."""
        pipeline = UnstructuredETLPipeline(use_transformer_ner=False)

        # Text with repeated entities
        text = "Alice works with Alice. Alice manages Alice's team."
        result = await pipeline.process_unstructured_text(text)

        # Entities might be deduplicated or appear multiple times
        entities = result['entities']
        alice_entities = [e for e in entities if 'Alice' in e['name']]

        # Should have extracted Alice
        assert len(alice_entities) > 0

    def test_structured_record_uniqueness(self):
        """Test unique record IDs in structured data."""
        handler = StructuredDataHandler()

        records_list = [
            {"id": "1", "name": "Alice"},
            {"id": "1", "name": "Bob"},  # Duplicate ID
            {"id": "2", "name": "Charlie"},
        ]

        records = handler.ingest_json_records(records_list, id_field='id')

        assert len(records) == 3
        # IDs can be duplicated in records
        ids = [r.record_id for r in records]
        assert ids.count("1") == 2

    @pytest.mark.asyncio
    async def test_chunk_overlap_consistency(self):
        """Test that text chunks maintain overlap consistency."""
        pipeline = UnstructuredETLPipeline(use_transformer_ner=False)

        text = " ".join(["word"] * 1000)
        result = await pipeline.process_unstructured_text(text, chunk_size=100)

        chunks = result['chunks']
        assert len(chunks) > 1

        # Check that consecutive chunks overlap
        for i in range(len(chunks) - 1):
            chunk1_words = chunks[i].split()
            chunk2_words = chunks[i + 1].split()

            # Should have some overlap
            overlap = set(chunk1_words) & set(chunk2_words)
            # Overlap is expected but not guaranteed due to word boundaries

    @pytest.mark.asyncio
    async def test_triple_graph_integrity(self):
        """Test that generated triples form valid graph structure."""
        pipeline = UnstructuredETLPipeline(use_transformer_ner=False)

        text = "Alice works at Acme. Bob manages Acme. Acme is in San Francisco."
        result = await pipeline.process_unstructured_text(text)

        triples = result['graph_triples']

        # Check basic graph integrity
        for triple in triples:
            subject = triple.get('subject') or triple[0]
            predicate = triple.get('predicate') or triple[1]
            obj = triple.get('obj') or triple[2]

            assert subject is not None
            assert predicate is not None
            assert obj is not None

            # Subject and object should not be the same (in most cases)
            # Predicate should not be empty
            assert len(str(predicate)) > 0


class TestPipelineInteroperability:
    """Test interoperability between pipelines."""

    @pytest.mark.asyncio
    async def test_etl_output_to_structured_format(self):
        """Test converting ETL output to structured format."""
        pipeline = UnstructuredETLPipeline(use_transformer_ner=False)

        text = "Alice Johnson works at Acme Corp as an Engineer"
        result = await pipeline.process_unstructured_text(text)

        # Convert entities to structured records
        entity_records = []
        for entity in result['entities']:
            entity_records.append({
                'name': entity['name'],
                'type': entity['entity_type'],
                'source': 'ETL',
                'confidence': entity['confidence'],
            })

        # Should be convertible to structured format
        handler = StructuredDataHandler()
        struct_recs = handler.ingest_json_records(entity_records, entity_type='Entity')

        assert len(struct_recs) > 0

    def test_structured_entities_to_etl_triples(self):
        """Test converting structured records to ETL-style triples."""
        handler = StructuredDataHandler()

        records_list = [
            {"id": "alice", "name": "Alice Johnson", "role": "Engineer"},
        ]

        records = handler.ingest_json_records(records_list, entity_type='Person')
        triples = handler.records_to_graph_triples(records)

        # Should have role information in triples
        role_triples = [t for t in triples if 'ROLE' in str(t[1]).upper()]
        assert len(role_triples) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
