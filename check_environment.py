"""Complete environment checker for Local Hybrid RAG system.

This script verifies all required tools, services, and Python packages are installed
and properly configured for running the dual ingestion pipeline.

Run:
    python check_environment.py
"""

import sys
import subprocess
import json
from pathlib import Path
from typing import Tuple, Dict, List


class EnvironmentChecker:
    """Comprehensive environment verification."""

    def __init__(self):
        self.results = {
            'python': {},
            'system_tools': {},
            'python_packages': {},
            'services': {},
            'files': {},
            'environment': {},
        }
        self.issues = []
        self.warnings = []

    def check_python_version(self) -> bool:
        """Check Python version (3.10+ required)."""
        version = sys.version_info
        required = (3, 10)
        
        status = version >= required
        self.results['python']['version'] = f"{version.major}.{version.minor}.{version.micro}"
        self.results['python']['required'] = f"{required[0]}.{required[1]}+"
        self.results['python']['status'] = 'OK' if status else 'FAIL'
        
        if not status:
            self.issues.append(f"Python {version.major}.{version.minor} is too old. Need Python 3.10+")
        
        return status

    def check_command_available(self, command: str) -> bool:
        """Check if a command is available in PATH."""
        try:
            result = subprocess.run(
                ['where', command] if sys.platform == 'win32' else ['which', command],
                capture_output=True,
                timeout=5,
            )
            return result.returncode == 0
        except Exception as e:
            return False

    def check_system_tools(self) -> Dict[str, bool]:
        """Check for essential system tools."""
        tools = {
            'python': 'Python interpreter',
            'pip': 'Python package manager',
            'git': 'Version control',
            'docker': 'Docker container runtime',
            'ollama': 'Local LLM engine',
        }

        for tool, desc in tools.items():
            available = self.check_command_available(tool)
            self.results['system_tools'][tool] = {
                'description': desc,
                'available': available,
                'status': '✓' if available else '✗',
            }
            
            if not available and tool in ['python', 'pip', 'docker', 'ollama']:
                self.issues.append(f"Missing: {tool} ({desc})")
            elif not available and tool in ['git']:
                self.warnings.append(f"Missing: {tool} ({desc}) - optional but recommended")

        return {k: v['available'] for k, v in self.results['system_tools'].items()}

    def check_python_packages(self) -> Dict[str, bool]:
        """Check for required Python packages."""
        packages = {
            'lightrag': 'LightRAG framework',
            'chromadb': 'Vector database',
            'neo4j': 'Graph database driver',
            'dotenv': 'Environment configuration',
            'unstructured': 'Document parser',
            'tiktoken': 'Token counter',
            'aiohttp': 'Async HTTP client',
            'pytest': 'Testing framework',
            'pytest_asyncio': 'Async test support',
        }

        for package, desc in packages.items():
            try:
                __import__(package.replace('_', '-').replace('-', '_'))
                available = True
                version = self._get_package_version(package)
                status_msg = f"v{version}" if version else "installed"
            except ImportError:
                available = False
                status_msg = "NOT INSTALLED"

            self.results['python_packages'][package] = {
                'description': desc,
                'available': available,
                'status': '✓' if available else '✗',
                'info': status_msg,
            }

            if not available:
                critical = package in ['lightrag', 'chromadb', 'neo4j', 'unstructured', 'pytest']
                if critical:
                    self.issues.append(f"Missing package: {package} ({desc})")
                else:
                    self.warnings.append(f"Missing package: {package} ({desc}) - optional")

        return {k: v['available'] for k, v in self.results['python_packages'].items()}

    def _get_package_version(self, package: str) -> str:
        """Get installed package version."""
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'show', package],
                capture_output=True,
                text=True,
                timeout=10,
            )
            for line in result.stdout.split('\n'):
                if line.startswith('Version:'):
                    return line.split(':')[1].strip()
        except:
            pass
        return None

    def check_services(self) -> Dict[str, bool]:
        """Check for running services (Neo4j, Ollama)."""
        services = {}

        # Check Neo4j
        try:
            result = subprocess.run(
                ['docker', 'ps', '--format', 'json'],
                capture_output=True,
                text=True,
                timeout=5,
            )
            containers = json.loads(result.stdout) if result.stdout else []
            neo4j_running = any('neo4j' in c.get('Names', '').lower() for c in containers)
        except:
            neo4j_running = False

        services['neo4j'] = {
            'description': 'Neo4j Graph Database',
            'running': neo4j_running,
            'status': '✓ Running' if neo4j_running else '✗ Not running',
            'start_cmd': 'docker compose up -d',
        }

        # Check Ollama
        try:
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True,
                timeout=5,
            )
            ollama_running = result.returncode == 0
        except:
            ollama_running = False

        services['ollama'] = {
            'description': 'Ollama LLM Service',
            'running': ollama_running,
            'status': '✓ Running' if ollama_running else '✗ Not running',
            'start_cmd': 'ollama serve (in background)',
        }

        self.results['services'] = services

        if not neo4j_running:
            self.warnings.append("Neo4j is not running. Start with: docker compose up -d")
        if not ollama_running:
            self.warnings.append("Ollama is not running. Start with: ollama serve")

        return {k: v['running'] for k, v in services.items()}

    def check_project_files(self) -> Dict[str, bool]:
        """Check for essential project files."""
        files = {
            'local_hybrid_rag.py': 'Main ingestion script',
            'etl_pipeline.py': 'ETL/NER pipeline',
            'structured_handler.py': 'Structured data handler',
            'requirements.txt': 'Python dependencies',
            '.env.example': 'Environment template',
            'docker-compose.yml': 'Docker configuration',
            'tests/test_etl_pipeline.py': 'ETL tests',
            'tests/test_structured_handler.py': 'Structured tests',
            'docs/DUAL_INGESTION.md': 'Ingestion documentation',
        }

        root = Path(__file__).parent
        for file, desc in files.items():
            path = root / file
            exists = path.exists()
            self.results['files'][file] = {
                'description': desc,
                'exists': exists,
                'status': '✓' if exists else '✗',
            }

            if not exists and file in ['local_hybrid_rag.py', 'requirements.txt', 'docker-compose.yml']:
                self.issues.append(f"Missing file: {file}")

        return {k: v['exists'] for k, v in self.results['files'].items()}

    def check_environment_config(self) -> Dict[str, bool]:
        """Check environment configuration."""
        env_items = {}

        # Check .env file
        env_file = Path(__file__).parent / '.env'
        env_exists = env_file.exists()
        env_items['env_file'] = {
            'description': '.env configuration file',
            'exists': env_exists,
            'status': '✓' if env_exists else '✗ (copy from .env.example)',
        }

        if not env_exists:
            self.warnings.append("No .env file found. Copy from .env.example and update credentials.")

        # Check .env content if exists
        if env_exists:
            try:
                with open(env_file) as f:
                    content = f.read()
                    has_neo4j = 'NEO4J_URI' in content
                    has_ollama = 'LLM_MODEL_NAME' in content
                    env_items['env_content'] = {
                        'has_neo4j_config': has_neo4j,
                        'has_ollama_config': has_ollama,
                        'status': '✓' if (has_neo4j and has_ollama) else '⚠ Incomplete config',
                    }
            except Exception as e:
                self.warnings.append(f"Could not read .env file: {e}")

        self.results['environment'] = env_items
        return env_items

    def print_report(self):
        """Print formatted environment check report."""
        print("\n" + "="*80)
        print("LOCAL HYBRID RAG - ENVIRONMENT CHECK REPORT")
        print("="*80)

        # Python Version
        print("\n[PYTHON VERSION]")
        py_info = self.results['python']
        print(f"  Current:  {py_info['version']}")
        print(f"  Required: {py_info['required']}")
        print(f"  Status:   {py_info['status']}")

        # System Tools
        print("\n[SYSTEM TOOLS]")
        for tool, info in self.results['system_tools'].items():
            symbol = "[OK]" if info['available'] else "[X]"
            print(f"  {symbol} {tool:12} - {info['description']}")

        # Python Packages
        print("\n[PYTHON PACKAGES]")
        for pkg, info in self.results['python_packages'].items():
            symbol = info['status']
            print(f"  {symbol} {pkg:20} - {info['description']:30} {info['info']}")

        # Services
        print("\n[SERVICES]")
        for service, info in self.results['services'].items():
            status = info['status']
            print(f"  {status:20} - {info['description']}")
            if not info['running']:
                print(f"     Start: {info['start_cmd']}")

        # Project Files
        print("\n[PROJECT FILES]")
        essential = ['local_hybrid_rag.py', 'requirements.txt', 'docker-compose.yml']
        for file, info in self.results['files'].items():
            symbol = info['status']
            indicator = "[ESSENTIAL]" if file in essential else "[optional]"
            print(f"  {symbol} {file:40} {indicator}")

        # Environment Config
        print("\n[ENVIRONMENT CONFIG]")
        for key, info in self.results['environment'].items():
            if key == 'env_file':
                symbol = info['status'].split()[0]
                print(f"  {symbol} {info['description']}")
            elif key == 'env_content':
                print(f"  NEO4J Config:   {'[OK]' if info.get('has_neo4j_config') else '[X]'}")
                print(f"  Ollama Config:  {'[OK]' if info.get('has_ollama_config') else '[X]'}")

        # Issues and Warnings
        if self.issues or self.warnings:
            print("\n" + "="*80)
            print("ISSUES & WARNINGS")
            print("="*80)

            if self.issues:
                print("\n[CRITICAL ISSUES - MUST FIX]:")
                for i, issue in enumerate(self.issues, 1):
                    print(f"  {i}. {issue}")

            if self.warnings:
                print("\n[WARNINGS - Recommended to fix]:")
                for i, warning in enumerate(self.warnings, 1):
                    print(f"  {i}. {warning}")

        # Summary
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)

        all_critical_ok = len(self.issues) == 0
        all_recommended_ok = len(self.warnings) == 0

        if all_critical_ok and all_recommended_ok:
            print("\n[SUCCESS] ALL CHECKS PASSED! System is ready for ingestion.")
            print("\nNext steps:")
            print("  1. Ensure Neo4j is running: docker compose up -d")
            print("  2. Ensure Ollama is running with models pulled")
            print("  3. Run: python local_hybrid_rag.py")
            print("  4. Or run tests: pytest tests/ -v")
            return 0

        elif all_critical_ok:
            print("\n[WARNING] WARNINGS PRESENT - System may work but has missing optional components.")
            print("\nYou can proceed, but consider fixing the warnings above.")
            print("\nTo run injection:")
            print("  1. Make sure services are running (Neo4j, Ollama)")
            print("  2. Run: python local_hybrid_rag.py")
            return 1

        else:
            print("\n[ERROR] CRITICAL ISSUES FOUND - System is NOT ready for ingestion.")
            print("\nPlease fix the issues above before proceeding.")
            print("\nTo install missing packages:")
            print("  pip install -r requirements.txt")
            print("\nTo start services:")
            print("  docker compose up -d")
            print("  ollama serve")
            return 2

    def get_installation_commands(self) -> List[str]:
        """Get commands to install missing dependencies."""
        commands = []

        # Missing Python packages
        missing_packages = [
            pkg for pkg, info in self.results['python_packages'].items()
            if not info['available']
        ]

        if missing_packages:
            commands.append(f"pip install {' '.join(missing_packages)}")

        # Missing services
        if not self.results['services']['neo4j']['running']:
            commands.append("docker compose up -d  # Start Neo4j")

        if not self.results['services']['ollama']['running']:
            commands.append("ollama serve  # Start Ollama (in separate terminal)")

        # Missing system tools
        print("\n" + "="*80)
        print("INSTALLATION GUIDE")
        print("="*80)

        if self.check_command_available('python') and not self.check_command_available('pip'):
            print("\n📌 PYTHON PIP NOT FOUND")
            print("  Fix: python -m ensurepip --upgrade")

        if not self.check_command_available('docker'):
            print("\n🐳 DOCKER NOT INSTALLED")
            print("  Download: https://www.docker.com/products/docker-desktop")
            print("  Or: choco install docker-desktop (if using Chocolatey)")

        if not self.check_command_available('ollama'):
            print("\n🦙 OLLAMA NOT INSTALLED")
            print("  Download: https://ollama.com")
            print("  Or: choco install ollama (if using Chocolatey)")

        if missing_packages:
            print(f"\n📦 INSTALL PYTHON PACKAGES")
            print(f"  pip install -r requirements.txt")
            print(f"  Or: pip install {' '.join(missing_packages)}")

        return commands


def main():
    """Run environment check."""
    checker = EnvironmentChecker()

    # Run all checks
    checker.check_python_version()
    checker.check_system_tools()
    checker.check_python_packages()
    checker.check_services()
    checker.check_project_files()
    checker.check_environment_config()

    # Print report
    exit_code = checker.print_report()

    # Installation commands
    commands = checker.get_installation_commands()

    if commands:
        print("\n" + "="*80)
        print("RUN THESE COMMANDS TO FIX ISSUES")
        print("="*80)
        for cmd in commands:
            print(f"\n  {cmd}")

    print("\n" + "="*80)

    return exit_code


if __name__ == '__main__':
    sys.exit(main())
