import os
import shutil
from pathlib import Path
from typing import List, Dict

PROJECT_STRUCTURE: Dict[str, List[str]] = {
    ".github/workflows": [
        """name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -r requirements/test.txt
      - run: pytest tests/""",
    ],
    "config": [
        """# Default configuration
environment: development
debug: true
api:
  timeout: 30
  retries: 3"""
    ],
    "docs/api": ["# API Documentation\n"],
    "docs/user_guide": ["# User Guide\n"],
    "notebooks": [],
    "output/samples": [],
    "output/visualizations": [],
    "src/sample": [
        """from typing import Optional

def sample_function() -> Optional[str]:
    \"\"\"Sample function with type hints.
    
    Returns:
        Optional[str]: Sample return value
    \"\"\"
    return None"""
    ],
    "src/schema": [],
    "src/utils": [
        """import logging
import structlog

logger = structlog.get_logger()"""
    ],
    "tests": [
        """import pytest

def test_sample():
    assert True"""
    ],
    "requirements": [
        """# Base requirements
requests>=2.28.0
pyyaml>=6.0
structlog>=22.1.0""",
        """# Dev requirements
-r base.txt
black>=22.3.0
flake8>=4.0.1
mypy>=0.961
pre-commit>=2.20.0""",
        """# Test requirements
-r base.txt
pytest>=7.1.2
pytest-cov>=3.0.0"""
    ],
}

FILES: Dict[str, str] = {
    "pyproject.toml": """[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "your-project-name"
version = "0.1.0"
description = "Your project description"
requires-python = ">=3.8"
authors = [
    { name = "Your Name", email = "your.email@example.com" },
]

[tool.pytest.ini_options]
addopts = "-ra -q"
testpaths = ["tests"]

[tool.black]
line-length = 88
target-version = ['py38']
include = '\.pyi?$'

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true""",

    "Makefile": """# Makefile for project management

.PHONY: setup test lint format clean

setup:
	pip install -r requirements/dev.txt

test:
	pytest tests/ --cov=src

lint:
	flake8 src/
	mypy src/

format:
	black src/ tests/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +""",

    ".gitignore": """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
.env
.venv
env/
venv/
ENV/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Testing
.coverage
.pytest_cache/
htmlcov/

# Project specific
output/*
!output/.gitkeep""",

    "README.md": """# Project Name

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```

2. Install dependencies:
```bash
make setup
```

3. Run tests:
```bash
make test
```

## Development

- Format code: `make format`
- Run linters: `make lint`
- Run tests: `make test`

## Project Structure

```
.
├── config/          # Configuration files
├── docs/           # Documentation
├── notebooks/      # Jupyter notebooks
├── output/         # Generated files
├── src/            # Source code
├── tests/          # Test files
└── requirements/   # Dependencies
```
""",

    ".env": """# Environment variables
DEBUG=True
API_KEY=your_key_here""",

    "src/__init__.py": """\"\"\"
Your project description.
\"\"\"

__version__ = "0.1.0"
""",
}

def create_directory_structure() -> None:
    """Creates the project directory structure."""
    for directory, contents in PROJECT_STRUCTURE.items():
        # Create directory
        Path(directory).mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py for Python packages
        if directory.startswith(("src", "tests")):
            Path(f"{directory}/__init__.py").touch()
        
        # Add content if specified
        if contents:
            if directory == "requirements":
                # Special handling for requirements directory
                for i, content in enumerate(["base.txt", "dev.txt", "test.txt"]):
                    with open(f"{directory}/{content}", "w") as f:
                        f.write(contents[i])
            elif directory == ".github/workflows":
                with open(f"{directory}/test.yml", "w") as f:
                    f.write(contents[0])
            else:
                # Default: write to main.py in the directory
                with open(f"{directory}/main.py", "w") as f:
                    f.write(contents[0])

def create_files() -> None:
    """Creates individual files in the project root."""
    for filename, content in FILES.items():
        with open(filename, "w") as f:
            f.write(content)

def main() -> None:
    """Main function to set up the project structure."""
    print("Creating project structure...")
    create_directory_structure()
    create_files()
    
    # Create empty .gitkeep files in empty directories
    for directory in ["output/samples", "output/visualizations"]:
        Path(f"{directory}/.gitkeep").touch()
    
    print("Project structure created successfully!")
    print("\nNext steps:")
    print("1. Create virtual environment: python -m venv venv")
    print("2. Activate virtual environment:")
    print("   - Windows: .\\venv\\Scripts\\activate")
    print("   - Unix/MacOS: source venv/bin/activate")
    print("3. Install dependencies: make setup")
    print("4. Initialize git: git init")
    print("5. Make initial commit: git add . && git commit -m 'Initial commit'")

if __name__ == "__main__":
    main()
