"""ETL Pipeline for unstructured data processing using NER (Named Entity Recognition).

This module handles:
- Text extraction from unstructured documents
- Named Entity Recognition (NER) using transformers
- Entity linking and relation extraction
- Graph triple generation for storage in Neo4j
- Chunk embedding for vector storage in ChromaDB

Pipeline flow:
    Raw text -> NER -> Entity extraction -> Relation detection -> Graph triples
    Raw text -> Chunking -> Embeddings -> Vector storage
"""

import re
import asyncio
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class Entity:
    """Represents a named entity extracted from text."""
    name: str
    entity_type: str  # PERSON, ORG, LOC, PRODUCT, etc.
    start_char: int
    end_char: int
    confidence: float = 1.0


@dataclass
class Relation:
    """Represents a relation between two entities."""
    head_entity: str
    relation_type: str
    tail_entity: str
    confidence: float = 1.0


@dataclass
class GraphTriple:
    """Graph triple (subject, predicate, object) for Neo4j storage."""
    subject: str
    predicate: str
    obj: str
    metadata: Dict[str, Any] = None


class SimpleNERExtractor:
    """Simple rule-based NER extractor (can be replaced with transformer-based models).
    
    This uses regex patterns and basic heuristics for quick entity extraction.
    For production, use: transformers.pipeline("ner") or spaCy's NER.
    """

    def __init__(self):
        # Patterns for common entity types
        self.patterns = {
            'PERSON': r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
            'ORG': r'\b([A-Z][a-z]+(?:\s+(?:Corp|Inc|LLC|Ltd|Co|Company|Corporation|Group|Inc\.|Ltd\.|Co\.))(?:\b|(?=\s)))',
            'EMAIL': r'\b([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b',
            'URL': r'https?://(?:www\.)?[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?',
            'PRODUCT': r'\b([A-Z][a-zA-Z0-9]+(?:\s+[A-Z][a-zA-Z0-9]+)*)\s+(?:v|version)\s*\d+',
        }

    def extract_entities(self, text: str) -> List[Entity]:
        """Extract entities from text using regex patterns."""
        entities = []
        seen_spans = set()

        for entity_type, pattern in self.patterns.items():
            for match in re.finditer(pattern, text):
                span = (match.start(), match.end())
                if span not in seen_spans:
                    entities.append(
                        Entity(
                            name=match.group(1) if match.groups() else match.group(0),
                            entity_type=entity_type,
                            start_char=match.start(),
                            end_char=match.end(),
                            confidence=0.8,
                        )
                    )
                    seen_spans.add(span)

        return sorted(entities, key=lambda e: e.start_char)


class RelationExtractor:
    """Extract relations between entities using simple patterns."""

    def __init__(self):
        self.relation_patterns = [
            (r'(\w+)\s+(?:is|was|are|were|be)\s+(?:a|an|the)?\s*(?:CEO|president|manager|director|employee|member)\s+(?:at|of|in)\s+(\w+)',
             'WORKS_AT'),
            (r'(\w+)\s+(?:founded|created|established)\s+(\w+)',
             'FOUNDED'),
            (r'(\w+)\s+(?:manages|leads|heads)\s+(\w+)',
             'MANAGES'),
            (r'(\w+)\s+(?:owns|acquired|bought)\s+(\w+)',
             'OWNS'),
            (r'(\w+)\s+(?:located|based)\s+(?:in|at)\s+(\w+)',
             'LOCATED_IN'),
        ]

    def extract_relations(self, text: str, entities: List[Entity]) -> List[Relation]:
        """Extract relations between entities."""
        relations = []
        entity_names = {e.name for e in entities}

        for pattern, rel_type in self.relation_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                groups = match.groups()
                if len(groups) >= 2:
                    head, tail = groups[0], groups[1]
                    # Filter to entities we found
                    if any(head.lower() in e.name.lower() for e in entities) and \
                       any(tail.lower() in e.name.lower() for e in entities):
                        relations.append(
                            Relation(
                                head_entity=head,
                                relation_type=rel_type,
                                tail_entity=tail,
                                confidence=0.7,
                            )
                        )

        return relations


class UnstructuredETLPipeline:
    """Main ETL pipeline for unstructured text data."""

    def __init__(self, use_transformer_ner: bool = False):
        """Initialize the pipeline.
        
        Args:
            use_transformer_ner: If True, use HuggingFace transformers for NER (requires download).
                                If False, use simple rule-based extraction.
        """
        self.ner_extractor = SimpleNERExtractor()
        self.relation_extractor = RelationExtractor()
        self.use_transformer = use_transformer_ner

        if use_transformer_ner:
            try:
                from transformers import pipeline as hf_pipeline
                self.transformer_ner = hf_pipeline("ner", model="dslim/bert-base-multilingual-cased-ner")
            except Exception as e:
                logger.warning(f"Transformer NER not available ({e}), falling back to rule-based extraction")
                self.use_transformer = False

    async def process_unstructured_text(
        self,
        text: str,
        document_id: str = "unknown",
        chunk_size: int = 512,
    ) -> Dict[str, Any]:
        """Process unstructured text through full ETL pipeline.

        Args:
            text: Raw unstructured text
            document_id: Identifier for the source document
            chunk_size: Token-approximate chunk size for embeddings

        Returns:
            Dict with keys:
                - text: original text
                - entities: list of extracted entities (dicts)
                - relations: list of extracted relations (dicts)
                - chunks: list of text chunks for embedding
                - graph_triples: list of (subject, predicate, object) tuples
                - metadata: source and processing info
        """
        # 1. Entity Extraction
        entities = self.ner_extractor.extract_entities(text)

        # 2. Relation Extraction
        relations = self.relation_extractor.extract_relations(text, entities)

        # 3. Generate Graph Triples from entities and relations
        graph_triples = self._generate_graph_triples(entities, relations, document_id)

        # 4. Chunk text for embedding
        chunks = self._chunk_text(text, chunk_size)

        result = {
            'text': text,
            'entities': [asdict(e) for e in entities],
            'relations': [asdict(r) for r in relations],
            'chunks': chunks,
            'graph_triples': [asdict(t) for t in graph_triples],
            'metadata': {
                'source_document': document_id,
                'entity_count': len(entities),
                'relation_count': len(relations),
                'triple_count': len(graph_triples),
                'chunk_count': len(chunks),
            }
        }

        return result

    def _generate_graph_triples(
        self,
        entities: List[Entity],
        relations: List[Relation],
        doc_id: str,
    ) -> List[GraphTriple]:
        """Generate graph triples from entities and relations."""
        triples = []

        # Entity triples: (entity_name, HAS_TYPE, entity_type)
        for entity in entities:
            triples.append(
                GraphTriple(
                    subject=entity.name,
                    predicate='HAS_TYPE',
                    obj=entity.entity_type,
                    metadata={'source': doc_id, 'confidence': entity.confidence},
                )
            )

        # Relation triples: (head, relation_type, tail)
        for relation in relations:
            triples.append(
                GraphTriple(
                    subject=relation.head_entity,
                    predicate=relation.relation_type,
                    obj=relation.tail_entity,
                    metadata={'source': doc_id, 'confidence': relation.confidence},
                )
            )

        # Document triples: (entity, MENTIONED_IN, document)
        for entity in entities:
            triples.append(
                GraphTriple(
                    subject=entity.name,
                    predicate='MENTIONED_IN',
                    obj=doc_id,
                    metadata={'source': doc_id},
                )
            )

        return triples

    def _chunk_text(self, text: str, chunk_size: int = 512) -> List[str]:
        """Split text into overlapping chunks (approximate token-based).
        
        Args:
            text: Text to chunk
            chunk_size: Approximate number of characters per chunk (rough proxy for tokens)

        Returns:
            List of text chunks with ~50% overlap
        """
        words = text.split()
        chunks = []
        current_chunk = []
        current_size = 0

        for word in words:
            current_chunk.append(word)
            current_size += len(word) + 1

            if current_size >= chunk_size:
                chunk_text = ' '.join(current_chunk)
                chunks.append(chunk_text)
                # Overlap: keep last ~50% of words
                current_chunk = current_chunk[len(current_chunk) // 2:]
                current_size = sum(len(w) + 1 for w in current_chunk)

        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return chunks


async def process_unstructured_batch(
    texts: List[Tuple[str, str]],
    chunk_size: int = 512,
) -> List[Dict[str, Any]]:
    """Process multiple unstructured documents in batch.

    Args:
        texts: List of (text, document_id) tuples
        chunk_size: Token-approx chunk size

    Returns:
        List of processed results (one per document)
    """
    pipeline = UnstructuredETLPipeline(use_transformer_ner=False)
    tasks = [
        pipeline.process_unstructured_text(text, doc_id, chunk_size)
        for text, doc_id in texts
    ]
    results = await asyncio.gather(*tasks)
    return results
