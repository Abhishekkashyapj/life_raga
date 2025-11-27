"""Structured data ingestion handler for CSV, JSON, and other tabular formats.

This module handles:
- CSV ingestion with schema inference
- JSON/JSONL ingestion
- Data validation and normalization
- Direct storage in Neo4j as nodes and relationships
- Integration with LightRAG graph storage
"""

import json
import csv
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class StructuredRecord:
    """Represents a single structured data record."""
    record_id: str
    data: Dict[str, Any]
    entity_type: str = "Record"
    source_file: str = "unknown"


class StructuredDataHandler:
    """Handler for structured data ingestion (CSV, JSON, etc.)."""

    def __init__(self, delimiter: str = ",", json_key_prefix: str = ""):
        """Initialize the handler.

        Args:
            delimiter: CSV delimiter (default: comma)
            json_key_prefix: Prefix for JSON keys to avoid conflicts
        """
        self.delimiter = delimiter
        self.json_key_prefix = json_key_prefix

    def ingest_csv(
        self,
        file_path: str,
        entity_type: str = "Record",
        id_column: Optional[str] = None,
    ) -> List[StructuredRecord]:
        """Ingest CSV file and return structured records.

        Args:
            file_path: Path to CSV file
            entity_type: Type label for records in graph
            id_column: Column name to use as record ID (if None, uses row index)

        Returns:
            List of StructuredRecord objects
        """
        records = []
        file_path = Path(file_path)

        if not file_path.exists():
            logger.error(f"CSV file not found: {file_path}")
            return records

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter=self.delimiter)
                for idx, row in enumerate(reader):
                    if not row:
                        continue

                    record_id = row.get(id_column, f"row_{idx}") if id_column else f"row_{idx}"
                    records.append(
                        StructuredRecord(
                            record_id=str(record_id),
                            data=row,
                            entity_type=entity_type,
                            source_file=file_path.name,
                        )
                    )

            logger.info(f"Ingested {len(records)} records from CSV: {file_path}")
        except Exception as e:
            logger.error(f"Error ingesting CSV {file_path}: {e}")

        return records

    def ingest_json(
        self,
        file_path: str,
        entity_type: str = "Record",
        id_field: Optional[str] = None,
        is_jsonl: bool = False,
    ) -> List[StructuredRecord]:
        """Ingest JSON or JSONL file and return structured records.

        Args:
            file_path: Path to JSON or JSONL file
            entity_type: Type label for records in graph
            id_field: Field name to use as record ID (if None, uses index)
            is_jsonl: If True, parse as JSONL (one JSON object per line)

        Returns:
            List of StructuredRecord objects
        """
        records = []
        file_path = Path(file_path)

        if not file_path.exists():
            logger.error(f"JSON file not found: {file_path}")
            return records

        try:
            if is_jsonl:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for idx, line in enumerate(f):
                        if not line.strip():
                            continue
                        try:
                            obj = json.loads(line)
                            record_id = obj.get(id_field, f"line_{idx}") if id_field else f"line_{idx}"
                            records.append(
                                StructuredRecord(
                                    record_id=str(record_id),
                                    data=obj,
                                    entity_type=entity_type,
                                    source_file=file_path.name,
                                )
                            )
                        except json.JSONDecodeError as e:
                            logger.warning(f"Skipping invalid JSON line {idx}: {e}")
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                    # Handle array of objects
                    if isinstance(data, list):
                        for idx, obj in enumerate(data):
                            if isinstance(obj, dict):
                                record_id = obj.get(id_field, f"item_{idx}") if id_field else f"item_{idx}"
                                records.append(
                                    StructuredRecord(
                                        record_id=str(record_id),
                                        data=obj,
                                        entity_type=entity_type,
                                        source_file=file_path.name,
                                    )
                                )
                    # Handle single object
                    elif isinstance(data, dict):
                        record_id = data.get(id_field, "root") if id_field else "root"
                        records.append(
                            StructuredRecord(
                                record_id=str(record_id),
                                data=data,
                                entity_type=entity_type,
                                source_file=file_path.name,
                            )
                        )

            logger.info(f"Ingested {len(records)} records from JSON: {file_path}")
        except Exception as e:
            logger.error(f"Error ingesting JSON {file_path}: {e}")

        return records

    def ingest_json_records(
        self,
        records_list: List[Dict[str, Any]],
        entity_type: str = "Record",
        id_field: Optional[str] = None,
        source_name: str = "inline",
    ) -> List[StructuredRecord]:
        """Ingest a list of dictionaries directly (in-memory).

        Args:
            records_list: List of dict objects
            entity_type: Type label for records
            id_field: Field to use as record ID
            source_name: Name to tag as source

        Returns:
            List of StructuredRecord objects
        """
        records = []
        for idx, obj in enumerate(records_list):
            if isinstance(obj, dict):
                record_id = obj.get(id_field, f"item_{idx}") if id_field else f"item_{idx}"
                records.append(
                    StructuredRecord(
                        record_id=str(record_id),
                        data=obj,
                        entity_type=entity_type,
                        source_file=source_name,
                    )
                )
        logger.info(f"Ingested {len(records)} in-memory records")
        return records

    def records_to_graph_triples(
        self,
        records: List[StructuredRecord],
    ) -> List[Tuple[str, str, str]]:
        """Convert structured records to graph triples for Neo4j.

        Each record becomes:
        - A node: (record_id, HAS_TYPE, entity_type)
        - Property nodes: (record_id, field_name, field_value) for each field
        - Source link: (record_id, FROM_SOURCE, source_file)

        Args:
            records: List of StructuredRecord objects

        Returns:
            List of (subject, predicate, object) triples
        """
        triples = []

        for record in records:
            # Entity type triple
            triples.append((record.record_id, "HAS_TYPE", record.entity_type))

            # Source file triple
            triples.append((record.record_id, "FROM_SOURCE", record.source_file))

            # Field triples (only for scalar values to keep graph manageable)
            for key, value in record.data.items():
                if isinstance(value, (str, int, float, bool)):
                    # Create a field node or link
                    field_node = f"{record.record_id}_{key}"
                    triples.append((record.record_id, key.upper(), str(value)))

        return triples

    def validate_records(
        self,
        records: List[StructuredRecord],
        required_fields: Optional[List[str]] = None,
    ) -> Tuple[List[StructuredRecord], List[str]]:
        """Validate records against a schema.

        Args:
            records: Records to validate
            required_fields: Fields that must be present in every record

        Returns:
            Tuple of (valid_records, error_messages)
        """
        valid_records = []
        errors = []
        required_fields = required_fields or []

        for idx, record in enumerate(records):
            record_errors = []

            for field in required_fields:
                if field not in record.data or record.data[field] is None:
                    record_errors.append(f"Missing required field: {field}")

            if record_errors:
                errors.append(f"Record {idx} ({record.record_id}): {', '.join(record_errors)}")
            else:
                valid_records.append(record)

        if errors:
            logger.warning(f"Validation failed for {len(errors)} records: {errors[:3]}")

        return valid_records, errors


async def ingest_structured_batch(
    file_paths: List[Tuple[str, str]],
    handler: Optional[StructuredDataHandler] = None,
) -> List[StructuredRecord]:
    """Ingest multiple structured files in batch.

    Args:
        file_paths: List of (file_path, file_type) tuples where file_type is 'csv', 'json', or 'jsonl'
        handler: StructuredDataHandler instance (default: create new)

    Returns:
        List of all StructuredRecord objects from all files
    """
    if handler is None:
        handler = StructuredDataHandler()

    all_records = []

    for file_path, file_type in file_paths:
        if file_type == 'csv':
            records = handler.ingest_csv(file_path)
        elif file_type == 'json':
            records = handler.ingest_json(file_path, is_jsonl=False)
        elif file_type == 'jsonl':
            records = handler.ingest_json(file_path, is_jsonl=True)
        else:
            logger.warning(f"Unknown file type: {file_type}")
            continue

        all_records.extend(records)

    return all_records
