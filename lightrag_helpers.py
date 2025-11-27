"""LightRAG helpers for creating a configured LightRAG instance when available.

This module wraps imports so it can be imported safely in environments without LightRAG installed.
"""
import os

def get_rag_ctor_kwargs_from_env():
    """Return a dict with a few default kwargs for LightRAG constructor (not importing LightRAG itself).

    This keeps the sample script cleaner and centralizes environment-driven defaults.
    """
    return {
        'working_dir': os.environ.get('WORKING_DIR', './rag_local'),
        'llm_model_name': os.environ.get('LLM_MODEL_NAME', 'llama3.1:8b'),
        'embedding_model': os.environ.get('EMBEDDING_MODEL', 'nomic-embed-text'),
        'neo4j_uri': os.environ.get('NEO4J_URI', 'neo4j://localhost:7687'),
        'neo4j_user': os.environ.get('NEO4J_USERNAME', 'neo4j'),
        'neo4j_password': os.environ.get('NEO4J_PASSWORD', 'password'),
    }
