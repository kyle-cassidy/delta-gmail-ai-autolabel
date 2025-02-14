"""
Test configuration and fixtures for the document classification system.
"""

import os
import pytest
from pathlib import Path
from typing import Dict, List, Optional, Any
import yaml
import sys
import shutil
import json
from unittest.mock import MagicMock
from .utils.document_helpers import update_test_documents
from email.message import EmailMessage

# Add mocks directory to Python path
MOCKS_DIR = Path(__file__).parent / "mocks"
sys.path.insert(0, str(MOCKS_DIR))

# Mock external dependencies
try:
    import google.generativeai as genai
except ImportError:
    genai = MagicMock()
    sys.modules["google.generativeai"] = genai


@pytest.fixture
def labeled_documents_dir(tmp_path: Path) -> Path:
    """Create a temporary directory for labeled documents."""
    labeled_dir = tmp_path / "labeled_documents"
    labeled_dir.mkdir()
    return labeled_dir


@pytest.fixture
def document_metadata(labeled_documents_dir: Path) -> Dict[str, Any]:
    """Load document metadata from the labeled documents directory."""
    metadata_file = labeled_documents_dir / "metadata.json"
    try:
        with open(metadata_file) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


@pytest.fixture
def test_config_dir(tmp_path: Path) -> Path:
    """Create a temporary config directory with actual configuration files."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()

    # Get the actual config directory path
    src_config_dir = Path(__file__).parents[1] / "src" / "config"

    # Copy all YAML files from the actual config directory
    for yaml_file in src_config_dir.glob("*.yaml"):
        if yaml_file.is_file():
            # Read the original file
            with open(yaml_file) as f:
                config = yaml.safe_load(f) or {}

            # Add version if it doesn't exist
            if "version" not in config:
                config["version"] = "1.0.0"

            # Write to the test directory
            with open(config_dir / yaml_file.name, "w") as f:
                yaml.dump(config, f)

    # Create version control file
    version_control = {
        "version_control": {
            "min_compatible_version": "1.0.0",
            "current_versions": {
                "regulatory_actions": "1.0.0",
                "product_categories": "1.0.0",
                "validation_rules": "1.0.0",
                "relationships": "1.0.0",
                "status_workflows": "1.0.0",
                "email_classification": "1.0.0",
                "clients": "1.0.0",
            },
            "migrations_required": {},
        }
    }

    with open(config_dir / "version_control.yaml", "w") as f:
        yaml.dump(version_control, f)

    return config_dir


@pytest.fixture
def test_documents_dir(tmp_path: Path) -> Path:
    """Create a temporary directory with test documents."""
    docs_dir = tmp_path / "documents"
    docs_dir.mkdir()

    documents = {
        "test_doc1.txt": """
        License Application
        State: Alabama
        Company: ARB
        Registration: REG-2024-001
        Amount: $1000.00
        """,
        "test_doc2.txt": """
        Renewal Form
        State: California
        Company: COR
        Registration: REG-2024-002
        Amount: $500.00
        """,
    }

    for filename, content in documents.items():
        with open(docs_dir / filename, "w") as f:
            f.write(content)

    return docs_dir


@pytest.fixture
def mock_email_message() -> EmailMessage:
    """Create a mock email message."""
    msg = EmailMessage()
    msg["Subject"] = "License Renewal Application - Alabama"
    msg["From"] = "test@example.com"
    msg["To"] = "regulatory@example.com"
    msg["Date"] = "Mon, 11 Feb 2024 15:30:00 -0500"
    msg["Message-ID"] = "<test123@example.com>"
    msg.set_content(
        """
    Please find attached our license renewal application for Alabama.
    
    Best regards,
    Test Company
    """
    )
    return msg


@pytest.fixture
def mock_gemini_response() -> Dict[str, Any]:
    """Create a mock Gemini response."""
    return {
        "entities": {
            "companies": ["ARB"],
            "products": ["Fertilizer"],
            "states": ["AL"],
        },
        "key_fields": {
            "dates": ["2024-02-11"],
            "registration_numbers": ["LIC-2024-001"],
            "amounts": [],
        },
        "summary": "License application for ARB in Alabama",
        "text": "Full document text would go here",
    }


@pytest.fixture
def mock_docling_doc() -> Any:
    """Create a mock Docling document object."""

    class MockDoc:
        def __init__(self) -> None:
            self.page_count = 1
            self.has_tables = False
            self.extraction_confidence = 0.95

        def get_text(self) -> str:
            return "Mock document text"

        def extract_entities(self, entity_type: str) -> List[str]:
            return ["Mock entity"]

        def extract_dates(self) -> List[str]:
            return ["2024-02-11"]

        def get_summary(self) -> str:
            return "Mock document summary"

    return MockDoc()


@pytest.fixture(scope="session")
def workspace_root() -> Path:
    """Get the workspace root directory."""
    return Path(__file__).parents[1]


@pytest.fixture(autouse=True)
def mock_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock environment variables."""
    monkeypatch.setenv("GOOGLE_API_KEY", "test_key")
    monkeypatch.setenv("TESTING", "true")
