"""Unit tests for structured_handler.py (CSV/JSON ingestion and validation).

Run:
    pytest tests/test_structured_handler.py -v
"""

import pytest
import json
import csv
import tempfile
from pathlib import Path
from structured_handler import StructuredDataHandler, StructuredRecord


class TestStructuredDataHandler:
    """Test suite for StructuredDataHandler."""

    def setup_method(self):
        """Setup before each test."""
        self.handler = StructuredDataHandler()
        self.temp_dir = tempfile.mkdtemp()

    def test_csv_ingestion_basic(self):
        """Test basic CSV ingestion."""
        csv_file = Path(self.temp_dir) / "test.csv"
        csv_file.write_text("id,name,email\n1,Alice,alice@example.com\n2,Bob,bob@example.com\n")

        records = self.handler.ingest_csv(str(csv_file))

        assert len(records) == 2
        assert records[0].data['name'] == 'Alice'
        assert records[1].data['name'] == 'Bob'

    def test_csv_with_id_column(self):
        """Test CSV ingestion with custom ID column."""
        csv_file = Path(self.temp_dir) / "test_id.csv"
        csv_file.write_text("employee_id,name,department\n101,Alice,Engineering\n102,Bob,Sales\n")

        records = self.handler.ingest_csv(str(csv_file), id_column='employee_id')

        assert records[0].record_id == '101'
        assert records[1].record_id == '102'

    def test_csv_with_custom_delimiter(self):
        """Test CSV ingestion with non-standard delimiter."""
        csv_file = Path(self.temp_dir) / "test_delim.csv"
        csv_file.write_text("id|name|age\n1|Alice|30\n2|Bob|25\n")

        handler = StructuredDataHandler(delimiter="|")
        records = handler.ingest_csv(str(csv_file))

        assert len(records) == 2
        assert records[0].data['name'] == 'Alice'
        assert records[0].data['age'] == '30'

    def test_csv_with_entity_type(self):
        """Test CSV ingestion with custom entity type."""
        csv_file = Path(self.temp_dir) / "test_entity.csv"
        csv_file.write_text("id,name\n1,Alice\n")

        records = self.handler.ingest_csv(str(csv_file), entity_type='Employee')

        assert records[0].entity_type == 'Employee'

    def test_json_array_ingestion(self):
        """Test JSON array ingestion."""
        json_file = Path(self.temp_dir) / "test.json"
        data = [
            {"id": 1, "name": "Alice", "role": "Engineer"},
            {"id": 2, "name": "Bob", "role": "Manager"},
        ]
        json_file.write_text(json.dumps(data))

        records = self.handler.ingest_json(str(json_file), is_jsonl=False)

        assert len(records) == 2
        assert records[0].data['name'] == 'Alice'
        assert records[1].data['name'] == 'Bob'

    def test_json_with_id_field(self):
        """Test JSON ingestion with custom ID field."""
        json_file = Path(self.temp_dir) / "test_id.json"
        data = [
            {"employee_id": "E101", "name": "Alice"},
            {"employee_id": "E102", "name": "Bob"},
        ]
        json_file.write_text(json.dumps(data))

        records = self.handler.ingest_json(str(json_file), id_field='employee_id', is_jsonl=False)

        assert records[0].record_id == 'E101'
        assert records[1].record_id == 'E102'

    def test_jsonl_ingestion(self):
        """Test JSONL (newline-delimited JSON) ingestion."""
        jsonl_file = Path(self.temp_dir) / "test.jsonl"
        jsonl_file.write_text(
            json.dumps({"id": 1, "name": "Alice"}) + "\n" +
            json.dumps({"id": 2, "name": "Bob"}) + "\n"
        )

        records = self.handler.ingest_json(str(jsonl_file), is_jsonl=True)

        assert len(records) == 2
        assert records[0].data['name'] == 'Alice'

    def test_json_single_object(self):
        """Test ingestion of single JSON object."""
        json_file = Path(self.temp_dir) / "single.json"
        data = {"company": "Acme Corp", "employees": 500}
        json_file.write_text(json.dumps(data))

        records = self.handler.ingest_json(str(json_file), is_jsonl=False)

        assert len(records) == 1
        assert records[0].data['company'] == 'Acme Corp'

    def test_in_memory_records(self):
        """Test ingestion from in-memory list."""
        records_list = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
        ]

        records = self.handler.ingest_json_records(records_list, entity_type='Person')

        assert len(records) == 2
        assert records[0].entity_type == 'Person'

    def test_records_to_graph_triples(self):
        """Test conversion of records to graph triples."""
        records = [
            StructuredRecord(record_id="1", data={"name": "Alice", "role": "Engineer"}, entity_type="Employee"),
            StructuredRecord(record_id="2", data={"name": "Bob", "role": "Manager"}, entity_type="Employee"),
        ]

        triples = self.handler.records_to_graph_triples(records)

        # Each record should generate multiple triples
        assert len(triples) > 0

        # Check structure
        for triple in triples:
            assert len(triple) == 3
            subject, predicate, obj = triple
            assert subject is not None
            assert predicate is not None
            assert obj is not None

    def test_triples_contain_entity_type(self):
        """Test that triples include entity type information."""
        records = [StructuredRecord(record_id="1", data={"name": "Alice"}, entity_type="Employee")]

        triples = self.handler.records_to_graph_triples(records)

        # Should have HAS_TYPE triple
        type_triples = [t for t in triples if t[1] == 'HAS_TYPE']
        assert len(type_triples) > 0
        assert type_triples[0][2] == 'Employee'

    def test_triples_contain_field_data(self):
        """Test that triples include field values."""
        records = [StructuredRecord(record_id="1", data={"name": "Alice"}, entity_type="Employee")]

        triples = self.handler.records_to_graph_triples(records)

        # Should have NAME triple
        name_triples = [t for t in triples if 'NAME' in t[1].upper()]
        assert len(name_triples) > 0

    def test_validate_records_success(self):
        """Test successful record validation."""
        records = [
            StructuredRecord(record_id="1", data={"name": "Alice", "email": "alice@example.com"}),
            StructuredRecord(record_id="2", data={"name": "Bob", "email": "bob@example.com"}),
        ]

        valid, errors = self.handler.validate_records(records, required_fields=['name', 'email'])

        assert len(valid) == 2
        assert len(errors) == 0

    def test_validate_records_missing_field(self):
        """Test validation with missing required field."""
        records = [
            StructuredRecord(record_id="1", data={"name": "Alice", "email": "alice@example.com"}),
            StructuredRecord(record_id="2", data={"name": "Bob"}),  # Missing email
        ]

        valid, errors = self.handler.validate_records(records, required_fields=['name', 'email'])

        assert len(valid) == 1
        assert len(errors) == 1
        assert 'email' in errors[0].lower()

    def test_validate_records_no_requirements(self):
        """Test validation with no required fields."""
        records = [StructuredRecord(record_id="1", data={"name": "Alice"})]

        valid, errors = self.handler.validate_records(records, required_fields=[])

        assert len(valid) == 1
        assert len(errors) == 0

    def test_source_file_tracking(self):
        """Test that source file is tracked in records."""
        csv_file = Path(self.temp_dir) / "tracked.csv"
        csv_file.write_text("id,name\n1,Alice\n")

        records = self.handler.ingest_csv(str(csv_file))

        assert records[0].source_file == 'tracked.csv'

    def test_nonexistent_file(self):
        """Test handling of non-existent file."""
        records = self.handler.ingest_csv("/nonexistent/file.csv")

        assert len(records) == 0

    def test_csv_empty_file(self):
        """Test handling of empty CSV."""
        csv_file = Path(self.temp_dir) / "empty.csv"
        csv_file.write_text("id,name\n")

        records = self.handler.ingest_csv(str(csv_file))

        assert len(records) == 0

    def test_csv_with_mixed_data_types(self):
        """Test CSV with mixed data types."""
        csv_file = Path(self.temp_dir) / "mixed.csv"
        csv_file.write_text("id,name,age,active\n1,Alice,30,true\n2,Bob,25,false\n")

        records = self.handler.ingest_csv(str(csv_file))

        # All values are strings in CSV
        assert isinstance(records[0].data['age'], str)
        assert records[0].data['age'] == '30'

    def test_json_malformed_jsonl(self):
        """Test handling of malformed JSONL."""
        jsonl_file = Path(self.temp_dir) / "bad.jsonl"
        jsonl_file.write_text(
            json.dumps({"id": 1, "name": "Alice"}) + "\n" +
            "not valid json\n" +
            json.dumps({"id": 2, "name": "Bob"}) + "\n"
        )

        records = self.handler.ingest_json(str(jsonl_file), is_jsonl=True)

        # Should skip invalid line and continue
        assert len(records) == 2

    def test_structured_record_dataclass(self):
        """Test StructuredRecord dataclass."""
        record = StructuredRecord(
            record_id="1",
            data={"name": "Alice"},
            entity_type="Employee",
            source_file="test.csv",
        )

        assert record.record_id == "1"
        assert record.data['name'] == "Alice"
        assert record.entity_type == "Employee"
        assert record.source_file == "test.csv"

    def test_triples_include_source(self):
        """Test that triples include source file information."""
        records = [
            StructuredRecord(
                record_id="1",
                data={"name": "Alice"},
                entity_type="Employee",
                source_file="employees.csv",
            )
        ]

        triples = self.handler.records_to_graph_triples(records)

        # Should have FROM_SOURCE triple
        source_triples = [t for t in triples if t[1] == 'FROM_SOURCE']
        assert len(source_triples) > 0
        assert source_triples[0][2] == 'employees.csv'


class TestStructuredHandlerEdgeCases:
    """Test edge cases and error handling."""

    def setup_method(self):
        """Setup before each test."""
        self.handler = StructuredDataHandler()
        self.temp_dir = tempfile.mkdtemp()

    def test_csv_special_characters(self):
        """Test CSV with special characters."""
        csv_file = Path(self.temp_dir) / "special.csv"
        csv_file.write_text('id,name,description\n1,Alice,"Hello, world!"\n2,Bob,"Quote: ""yes"""\n', encoding='utf-8')

        records = self.handler.ingest_csv(str(csv_file))

        assert len(records) == 2
        # CSV should handle quoted fields correctly

    def test_json_nested_structure(self):
        """Test JSON with nested structure."""
        json_file = Path(self.temp_dir) / "nested.json"
        data = [
            {
                "id": 1,
                "name": "Alice",
                "address": {"city": "NYC", "zip": "10001"},
            }
        ]
        json_file.write_text(json.dumps(data))

        records = self.handler.ingest_json(str(json_file), is_jsonl=False)

        assert len(records) == 1
        assert isinstance(records[0].data['address'], dict)

    def test_large_csv(self):
        """Test handling of large CSV."""
        csv_file = Path(self.temp_dir) / "large.csv"

        # Create CSV with 1000 rows
        with open(csv_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'name', 'value'])
            writer.writeheader()
            for i in range(1000):
                writer.writerow({'id': i, 'name': f'Record{i}', 'value': i * 100})

        records = self.handler.ingest_csv(str(csv_file))

        assert len(records) == 1000

    def test_null_values_in_json(self):
        """Test JSON with null values."""
        json_file = Path(self.temp_dir) / "null.json"
        data = [
            {"id": 1, "name": "Alice", "middle_name": None},
            {"id": 2, "name": "Bob", "middle_name": None},
        ]
        json_file.write_text(json.dumps(data))

        records = self.handler.ingest_json(str(json_file), is_jsonl=False)

        assert len(records) == 2
        assert records[0].data['middle_name'] is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
