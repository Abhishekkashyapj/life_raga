"""Quick setup script to install missing Python dependencies.

This script installs all required Python packages for the injection pipeline.

Run:
    python setup_deps.py
"""

import subprocess
import sys


def run_command(cmd, description=""):
    """Run a command and print output."""
    print(f"\n{'='*70}")
    if description:
        print(f"📦 {description}")
    print(f"{'='*70}")
    print(f"Running: {cmd}\n")

    try:
        result = subprocess.run(cmd, shell=True)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Install all dependencies."""
    print("\n" + "*"*70)
    print("HYBRID RAG INJECTION - DEPENDENCY SETUP")
    print("*"*70)

    # Upgrade pip
    run_command(
        f"{sys.executable} -m pip install --upgrade pip",
        "Upgrading pip"
    )

    # Install requirements
    print("\n" + "="*70)
    print("📦 Installing Python packages from requirements.txt")
    print("="*70)

    packages = [
        ("lightrag-hku[api]", "LightRAG (RAG orchestration)"),
        ("chromadb", "ChromaDB (vector storage)"),
        ("neo4j", "Neo4j driver (graph storage)"),
        ("unstructured[all-docs]", "Unstructured (document parsing)"),
        ("sentence-transformers", "Sentence Transformers (embeddings)"),
        ("tiktoken", "Tiktoken (token counting)"),
        ("python-dotenv", "Python-dotenv (config)"),
        ("requests", "Requests (HTTP)"),
        ("aiohttp", "Aiohttp (async HTTP)"),
        ("pytest", "Pytest (testing)"),
        ("pytest-asyncio", "Pytest-asyncio (async tests)"),
        ("pytest-cov", "Pytest-cov (coverage)"),
    ]

    failed = []
    for package, description in packages:
        success = run_command(
            f"{sys.executable} -m pip install '{package}'",
            f"Installing {description}"
        )
        if not success:
            failed.append(package)

    # Summary
    print("\n" + "*"*70)
    print("INSTALLATION SUMMARY")
    print("*"*70)

    if not failed:
        print("\n✅ All Python packages installed successfully!")
        print("\n📋 Next steps:")
        print("   1. Install Docker Desktop (for Neo4j)")
        print("      https://www.docker.com/products/docker-desktop")
        print("\n   2. Install Ollama (for local LLM)")
        print("      https://ollama.com")
        print("\n   3. Run this to verify everything:")
        print("      python check_system.py")
        print("\n   4. Start Neo4j and Ollama, then run:")
        print("      python local_hybrid_rag.py")
    else:
        print(f"\n❌ Failed to install {len(failed)} package(s):")
        for pkg in failed:
            print(f"   - {pkg}")
        print("\n   Try installing manually:")
        print(f"   {sys.executable} -m pip install -r requirements.txt")


if __name__ == "__main__":
    main()
