import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_readme_exists():
    assert (ROOT / 'README.md').exists(), 'README.md should exist in the project root'


def test_requirements():
    assert (ROOT / 'requirements.txt').exists(), 'requirements.txt is required'


def test_sample_docs():
    sample = ROOT / 'sample_docs' / 'sample.txt'
    assert sample.exists(), 'sample_docs/sample.txt should exist'
    text = sample.read_text(encoding='utf-8').strip()
    assert len(text) > 10, 'sample text must contain some content'


def test_env_example_has_keys():
    e = (ROOT / '.env.example').read_text(encoding='utf-8')
    for key in ('LLM_MODEL_NAME', 'NEO4J_URI', 'NEO4J_PASSWORD'):
        assert key in e, f'{key} should be present in .env.example'
