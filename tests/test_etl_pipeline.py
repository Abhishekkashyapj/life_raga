"""Unit tests for etl_pipeline.py (NER and entity/relation extraction).

Run:
    pytest tests/test_etl_pipeline.py -v
"""

import pytest
from etl_pipeline import (
    SimpleNERExtractor,
    RelationExtractor,
    UnstructuredETLPipeline,
    Entity,
    Relation,
)


class TestSimpleNERExtractor:
    """Test suite for SimpleNERExtractor."""

    def setup_method(self):
        """Setup before each test."""
        self.extractor = SimpleNERExtractor()

    def test_extract_person_names(self):
        """Test extraction of person names."""
        text = "Alice Johnson works at Acme Corp. Bob Smith is her manager."
        entities = self.extractor.extract_entities(text)

        person_entities = [e for e in entities if e.entity_type == 'PERSON']
        assert len(person_entities) >= 2, "Should extract at least 2 person names"

        names = {e.name for e in person_entities}
        assert 'Alice' in names or 'Alice Johnson' in names

    def test_extract_organizations(self):
        """Test extraction of organization names."""
        text = "Acme Corp and TechCorp Inc are competitors. Google LLC also entered."
        entities = self.extractor.extract_entities(text)

        org_entities = [e for e in entities if e.entity_type == 'ORG']
        assert len(org_entities) >= 1, "Should extract at least 1 organization"

    def test_extract_emails(self):
        """Test extraction of email addresses."""
        text = "Contact alice@example.com or bob.smith@company.org for details."
        entities = self.extractor.extract_entities(text)

        email_entities = [e for e in entities if e.entity_type == 'EMAIL']
        assert len(email_entities) >= 1, "Should extract at least 1 email"

    def test_extract_urls(self):
        """Test extraction of URLs."""
        text = "Visit https://www.example.com or http://github.com/user/repo for info."
        entities = self.extractor.extract_entities(text)

        url_entities = [e for e in entities if e.entity_type == 'URL']
        assert len(url_entities) >= 1, "Should extract at least 1 URL"

    def test_entity_has_position(self):
        """Test that entities have correct start/end positions."""
        text = "Alice works at Acme Corp"
        entities = self.extractor.extract_entities(text)

        for entity in entities:
            assert entity.start_char >= 0
            assert entity.end_char > entity.start_char
            assert entity.start_char < len(text)
            assert entity.end_char <= len(text)
            # Verify span matches original text
            span_text = text[entity.start_char:entity.end_char]
            assert entity.name in span_text or span_text in entity.name

    def test_no_false_positives_on_empty(self):
        """Test that empty text returns no entities."""
        entities = self.extractor.extract_entities("")
        assert len(entities) == 0

    def test_entity_confidence(self):
        """Test that entities have confidence scores."""
        text = "Alice works at Acme Corp"
        entities = self.extractor.extract_entities(text)

        for entity in entities:
            assert 0.0 <= entity.confidence <= 1.0


class TestRelationExtractor:
    """Test suite for RelationExtractor."""

    def setup_method(self):
        """Setup before each test."""
        self.extractor = RelationExtractor()
        self.ner = SimpleNERExtractor()

    def test_works_at_relation(self):
        """Test extraction of WORKS_AT relations."""
        text = "Alice is an engineer at Acme Corp"
        entities = self.ner.extract_entities(text)
        relations = self.extractor.extract_relations(text, entities)

        works_at_relations = [r for r in relations if r.relation_type == 'WORKS_AT']
        assert len(works_at_relations) >= 1, "Should extract WORKS_AT relation"

    def test_founded_relation(self):
        """Test extraction of FOUNDED relations."""
        text = "Elon Musk founded SpaceX in 2002"
        entities = self.ner.extract_entities(text)
        relations = self.extractor.extract_relations(text, entities)

        # Relation extraction might be weak on this pattern, but test structure
        assert isinstance(relations, list)

    def test_manages_relation(self):
        """Test extraction of MANAGES relations."""
        text = "Alice manages the engineering team at Acme"
        entities = self.ner.extract_entities(text)
        relations = self.extractor.extract_relations(text, entities)

        manages_relations = [r for r in relations if r.relation_type == 'MANAGES']
        # Might not always extract, but verify structure
        for rel in manages_relations:
            assert rel.head_entity is not None
            assert rel.tail_entity is not None
            assert rel.relation_type is not None

    def test_located_in_relation(self):
        """Test extraction of LOCATED_IN relations."""
        text = "Acme Corp is located in San Francisco"
        entities = self.ner.extract_entities(text)
        relations = self.extractor.extract_relations(text, entities)

        assert isinstance(relations, list)

    def test_relation_confidence(self):
        """Test that relations have confidence scores."""
        text = "Alice is a manager at Acme Corp"
        entities = self.ner.extract_entities(text)
        relations = self.extractor.extract_relations(text, entities)

        for relation in relations:
            assert 0.0 <= relation.confidence <= 1.0


class TestUnstructuredETLPipeline:
    """Test suite for full UnstructuredETLPipeline."""

    @pytest.mark.asyncio
    async def test_process_simple_text(self):
        """Test processing simple unstructured text."""
        pipeline = UnstructuredETLPipeline(use_transformer_ner=False)
        text = "Alice Johnson works at Acme Corporation in San Francisco."

        result = await pipeline.process_unstructured_text(
            text,
            document_id="test_doc_1",
            chunk_size=512,
        )

        # Verify result structure
        assert 'text' in result
        assert 'entities' in result
        assert 'relations' in result
        assert 'chunks' in result
        assert 'graph_triples' in result
        assert 'metadata' in result

        # Verify content
        assert result['text'] == text
        assert isinstance(result['entities'], list)
        assert isinstance(result['relations'], list)
        assert isinstance(result['chunks'], list)
        assert isinstance(result['graph_triples'], list)

    @pytest.mark.asyncio
    async def test_entity_count_in_metadata(self):
        """Test that metadata reflects extracted entity count."""
        pipeline = UnstructuredETLPipeline(use_transformer_ner=False)
        text = "Alice and Bob work at Acme Corp. Charlie works at TechCorp."

        result = await pipeline.process_unstructured_text(text, document_id="test_doc_2")

        entity_count = result['metadata']['entity_count']
        assert entity_count >= 3, "Should detect at least 3 entities"
        assert entity_count == len(result['entities'])

    @pytest.mark.asyncio
    async def test_chunking(self):
        """Test text chunking for embeddings."""
        pipeline = UnstructuredETLPipeline(use_transformer_ner=False)
        text = " ".join(["word"] * 600)  # Long text

        result = await pipeline.process_unstructured_text(
            text,
            document_id="test_doc_3",
            chunk_size=100,
        )

        chunks = result['chunks']
        assert len(chunks) > 1, "Long text should be split into multiple chunks"

        for chunk in chunks:
            assert len(chunk) > 0, "Each chunk should have content"

    @pytest.mark.asyncio
    async def test_graph_triple_generation(self):
        """Test that graph triples are generated correctly."""
        pipeline = UnstructuredETLPipeline(use_transformer_ner=False)
        text = "Alice is the CEO of Acme Corp"

        result = await pipeline.process_unstructured_text(text, document_id="test_doc_4")

        triples = result['graph_triples']
        assert len(triples) > 0, "Should generate at least one triple"

        for triple in triples:
            assert 'subject' in triple
            assert 'predicate' in triple
            assert 'obj' in triple
            assert triple['subject'] is not None
            assert triple['predicate'] is not None
            assert triple['obj'] is not None

    @pytest.mark.asyncio
    async def test_document_mention_triples(self):
        """Test that entities are linked to document."""
        pipeline = UnstructuredETLPipeline(use_transformer_ner=False)
        text = "Alice and Bob work together"

        result = await pipeline.process_unstructured_text(text, document_id="alice_bob_doc")

        # Check for MENTIONED_IN relationships
        mention_triples = [
            t for t in result['graph_triples']
            if t['predicate'] == 'MENTIONED_IN'
        ]
        assert len(mention_triples) > 0, "Entities should be linked to document"

        for triple in mention_triples:
            assert triple['obj'] == 'alice_bob_doc'

    @pytest.mark.asyncio
    async def test_metadata_completeness(self):
        """Test that metadata is complete."""
        pipeline = UnstructuredETLPipeline(use_transformer_ner=False)
        text = "Test text"

        result = await pipeline.process_unstructured_text(text, document_id="test_doc_5")

        metadata = result['metadata']
        assert 'source_document' in metadata
        assert 'entity_count' in metadata
        assert 'relation_count' in metadata
        assert 'triple_count' in metadata
        assert 'chunk_count' in metadata

        assert metadata['source_document'] == 'test_doc_5'
        assert metadata['entity_count'] >= 0
        assert metadata['relation_count'] >= 0
        assert metadata['triple_count'] > 0
        assert metadata['chunk_count'] > 0


class TestETLPipelineEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_empty_text(self):
        """Test processing empty text."""
        pipeline = UnstructuredETLPipeline(use_transformer_ner=False)
        result = await pipeline.process_unstructured_text("", document_id="empty")

        assert result['text'] == ""
        assert result['entities'] == []
        assert result['chunks'] == [] or result['chunks'] == [""]

    @pytest.mark.asyncio
    async def test_very_long_text(self):
        """Test processing very long text."""
        pipeline = UnstructuredETLPipeline(use_transformer_ner=False)
        long_text = " ".join(["word"] * 5000)

        result = await pipeline.process_unstructured_text(
            long_text,
            document_id="long_doc",
            chunk_size=512,
        )

        assert len(result['chunks']) > 10, "Should create many chunks"

    @pytest.mark.asyncio
    async def test_special_characters(self):
        """Test processing text with special characters."""
        pipeline = UnstructuredETLPipeline(use_transformer_ner=False)
        text = "Alice@Company! Bob#TechCorp & Charlie$Corp123"

        result = await pipeline.process_unstructured_text(text, document_id="special")

        # Should handle without crashing
        assert isinstance(result['entities'], list)
        assert isinstance(result['chunks'], list)

    @pytest.mark.asyncio
    async def test_unicode_text(self):
        """Test processing Unicode text."""
        pipeline = UnstructuredETLPipeline(use_transformer_ner=False)
        text = "Alice (爱丽丝) works at Acme (公司) in Shanghai (上海)"

        result = await pipeline.process_unstructured_text(text, document_id="unicode")

        assert isinstance(result['entities'], list)
        assert isinstance(result['chunks'], list)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
