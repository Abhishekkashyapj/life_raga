"""Environment checker for hybrid RAG ingestion pipeline.

Verifies all required tools and dependencies are installed and accessible.

Run:
    python check_system.py
"""

import subprocess
import sys
import os
from pathlib import Path


class SystemChecker:
    """Check system for required tools and dependencies."""

    def __init__(self):
        self.checks = []
        self.passed = 0
        self.failed = 0
        self.warnings = 0

    def run_command(self, cmd, shell=False):
        """Run a command and return success status and output."""
        try:
            result = subprocess.run(
                cmd,
                shell=shell,
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0, result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)

    def check_python(self):
        """Check Python version (3.10+)."""
        print("\n[1/12] Checking Python...")
        success, output = self.run_command([sys.executable, "--version"])

        if success:
            try:
                version_str = output.split()[1]
                major, minor = map(int, version_str.split('.')[:2])
                if major >= 3 and minor >= 10:
                    print(f"  ✓ Python {version_str} (OK)")
                    self.passed += 1
                    return True
                else:
                    print(f"  ❌ Python {version_str} (need 3.10+)")
                    self.failed += 1
                    return False
            except:
                print(f"  ⚠ Could not parse version: {output}")
                self.warnings += 1
                return True
        else:
            print(f"  ❌ Python not found")
            self.failed += 1
            return False

    def check_pip(self):
        """Check pip installation."""
        print("\n[2/12] Checking pip...")
        success, output = self.run_command([sys.executable, "-m", "pip", "--version"])

        if success:
            print(f"  ✓ pip available")
            self.passed += 1
            return True
        else:
            print(f"  ❌ pip not found")
            self.failed += 1
            return False

    def check_docker(self):
        """Check Docker installation."""
        print("\n[3/12] Checking Docker...")
        success, output = self.run_command("docker --version", shell=True)

        if success:
            version = output.strip().split('\n')[0]
            print(f"  ✓ Docker {version}")
            self.passed += 1
            return True
        else:
            print(f"  ⚠ Docker not found (needed for Neo4j)")
            print(f"    Install from: https://www.docker.com/products/docker-desktop")
            self.warnings += 1
            return False

    def check_docker_running(self):
        """Check if Docker daemon is running."""
        print("\n[4/12] Checking Docker daemon...")
        success, output = self.run_command("docker ps", shell=True)

        if success:
            print(f"  ✓ Docker daemon is running")
            self.passed += 1
            return True
        else:
            print(f"  ⚠ Docker not running (start Docker Desktop)")
            self.warnings += 1
            return False

    def check_ollama(self):
        """Check Ollama installation."""
        print("\n[5/12] Checking Ollama...")
        success, output = self.run_command("ollama --version", shell=True)

        if success:
            version = output.strip().split('\n')[0]
            print(f"  ✓ Ollama {version}")
            self.passed += 1
            return True
        else:
            print(f"  ⚠ Ollama not found")
            print(f"    Install from: https://ollama.com")
            self.warnings += 1
            return False

    def check_ollama_models(self):
        """Check if required Ollama models are pulled."""
        print("\n[6/12] Checking Ollama models...")
        required_models = ["llama3.1:8b", "nomic-embed-text"]
        missing = []

        success, output = self.run_command("ollama list", shell=True)

        if success:
            for model in required_models:
                if model in output:
                    print(f"  ✓ {model} available")
                    self.passed += 1
                else:
                    print(f"  ❌ {model} not pulled")
                    missing.append(model)
                    self.failed += 1

            if missing:
                print(f"\n    To pull missing models:")
                for model in missing:
                    print(f"      ollama pull {model}")
            return len(missing) == 0
        else:
            print(f"  ⚠ Could not check models (is Ollama running?)")
            self.warnings += 1
            return False

    def check_python_module(self, module_name, package_name=None):
        """Check if a Python module is installed."""
        package = package_name or module_name
        try:
            __import__(module_name)
            return True, None
        except ImportError as e:
            return False, str(e)

    def check_lightrag(self):
        """Check LightRAG installation."""
        print("\n[7/12] Checking LightRAG...")
        success, error = self.check_python_module("lightrag")

        if success:
            print(f"  ✓ LightRAG installed")
            self.passed += 1
            return True
        else:
            print(f"  ❌ LightRAG not installed")
            print(f"    Install: pip install lightrag-hku[api]")
            self.failed += 1
            return False

    def check_chromadb(self):
        """Check ChromaDB installation."""
        print("\n[8/12] Checking ChromaDB...")
        success, error = self.check_python_module("chromadb")

        if success:
            print(f"  ✓ ChromaDB installed")
            self.passed += 1
            return True
        else:
            print(f"  ❌ ChromaDB not installed")
            print(f"    Install: pip install chromadb")
            self.failed += 1
            return False

    def check_neo4j(self):
        """Check Neo4j Python driver."""
        print("\n[9/12] Checking Neo4j driver...")
        success, error = self.check_python_module("neo4j")

        if success:
            print(f"  ✓ Neo4j driver installed")
            self.passed += 1
            return True
        else:
            print(f"  ❌ Neo4j driver not installed")
            print(f"    Install: pip install neo4j")
            self.failed += 1
            return False

    def check_unstructured(self):
        """Check Unstructured library."""
        print("\n[10/12] Checking Unstructured...")
        success, error = self.check_python_module("unstructured")

        if success:
            print(f"  ✓ Unstructured installed")
            self.passed += 1
            return True
        else:
            print(f"  ❌ Unstructured not installed")
            print(f"    Install: pip install unstructured[all-docs]")
            self.failed += 1
            return False

    def check_venv(self):
        """Check if running in a virtual environment."""
        print("\n[11/12] Checking virtual environment...")
        in_venv = hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
        )

        if in_venv:
            print(f"  ✓ Running in virtual environment")
            self.passed += 1
            return True
        else:
            print(f"  ⚠ Not in virtual environment")
            print(f"    Recommended: .venv\\Scripts\\Activate.ps1")
            self.warnings += 1
            return False

    def check_env_file(self):
        """Check if .env file exists."""
        print("\n[12/12] Checking .env configuration...")
        env_path = Path(".env")
        example_path = Path(".env.example")

        if env_path.exists():
            print(f"  ✓ .env file found")
            self.passed += 1
            return True
        elif example_path.exists():
            print(f"  ⚠ .env not found (using defaults from .env.example)")
            print(f"    Create: copy .env.example .env")
            self.warnings += 1
            return True
        else:
            print(f"  ❌ Neither .env nor .env.example found")
            self.failed += 1
            return False

    def check_project_files(self):
        """Check if core project files exist."""
        print("\n[BONUS] Checking project files...")
        required_files = [
            "local_hybrid_rag.py",
            "etl_pipeline.py",
            "structured_handler.py",
            "test_ingestion_pipeline.py",
            "requirements.txt",
        ]

        missing = []
        for file in required_files:
            if not Path(file).exists():
                missing.append(file)

        if not missing:
            print(f"  ✓ All core files present")
            self.passed += 1
            return True
        else:
            print(f"  ⚠ Missing files: {', '.join(missing)}")
            self.warnings += 1
            return False

    def run_all_checks(self):
        """Run all checks."""
        print("\n" + "="*70)
        print("HYBRID RAG INJECTION SYSTEM - ENVIRONMENT CHECK")
        print("="*70)

        # Core system tools
        self.check_python()
        self.check_pip()
        self.check_docker()
        self.check_docker_running()
        self.check_ollama()
        self.check_ollama_models()

        # Python packages
        self.check_lightrag()
        self.check_chromadb()
        self.check_neo4j()
        self.check_unstructured()

        # Environment
        self.check_venv()
        self.check_env_file()

        # Project files
        self.check_project_files()

    def print_summary(self):
        """Print summary of checks."""
        total = self.passed + self.failed + self.warnings

        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)

        print(f"\n✓ Passed:  {self.passed}")
        print(f"⚠ Warnings: {self.warnings}")
        print(f"❌ Failed:  {self.failed}")

        print(f"\nTotal: {total} checks")

        if self.failed == 0:
            print("\n🎉 ALL CRITICAL CHECKS PASSED!")
            print("\n✅ Your system is ready to run the injection pipeline:")
            print("\n   1. Ensure Neo4j is running:        docker compose up -d")
            print("   2. Ensure Ollama is running:       ollama serve (in background)")
            print("   3. Run the ingestion script:       python local_hybrid_rag.py")
            print("   4. Or run with structured data:    python local_hybrid_rag.py --structured data.csv")
            print("   5. Or run with unstructured data:  python local_hybrid_rag.py --unstructured doc.txt")
            return True
        else:
            print(f"\n❌ {self.failed} critical issue(s) need to be resolved")
            print("\n   Please fix the failures above and re-run this check")
            return False

    def suggest_install(self):
        """Suggest install commands."""
        print("\n" + "="*70)
        print("QUICK FIX - Install Missing Components")
        print("="*70)

        if self.failed > 0:
            print("\nRun these commands to fix issues:\n")

            # Python packages
            if any("LightRAG" in str(c) for c in [self.check_lightrag]):
                print("  # Install RAG packages")
                print("  pip install lightrag-hku[api] chromadb neo4j unstructured[all-docs]")

            # System tools
            print("\n  # For Docker (Windows):")
            print("  # Download from: https://www.docker.com/products/docker-desktop")

            print("\n  # For Ollama (Windows):")
            print("  # Download from: https://ollama.com")

            print("\n  # Pull Ollama models:")
            print("  ollama pull llama3.1:8b")
            print("  ollama pull nomic-embed-text")


def main():
    """Main function."""
    checker = SystemChecker()

    try:
        checker.run_all_checks()
        success = checker.print_summary()

        if checker.failed > 0:
            checker.suggest_install()

        sys.exit(0 if success else 1)

    except Exception as e:
        print(f"\n❌ Error during checks: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
