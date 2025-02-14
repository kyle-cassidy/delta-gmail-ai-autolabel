# tests/conftest.py
import os
import pytest
from pathlib import Path
from typing import Dict, List, Optional
import yaml
import sys
import shutil
import json
from unittest.mock import MagicMock
from .utils.document_helpers import update_test_documents

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
def labeled_documents_dir(workspace_root) -> Path:
    """
    Access the labeled documents directory containing real PDFs and their expected classifications.
    The directory structure should be:

    tests/fixtures/labeled_documents/
    ├── metadata.json            # Contains expected classifications for each document
    ├── approvals/              # Documents organized by type
    │   ├── doc1.pdf
    │   └── doc2.pdf
    ├── denials/
    │   └── doc3.pdf
    └── requests/
        └── doc4.pdf
    """
    # Set up directories
    documents_dir = workspace_root / "tests" / "fixtures" / "documents"
    labeled_dir = workspace_root / "tests" / "fixtures" / "labeled_documents"

    if not labeled_dir.exists():
        labeled_dir.mkdir(parents=True)

    # Update test documents and metadata
    update_test_documents(documents_dir, labeled_dir)

    return labeled_dir


@pytest.fixture
def document_metadata(labeled_documents_dir) -> Dict:
    """Get the metadata for labeled test documents."""
    metadata_file = labeled_documents_dir / "metadata.json"
    if metadata_file.exists():
        with open(metadata_file) as f:
            return json.load(f)
    return {}


@pytest.fixture
def test_config_dir(tmp_path) -> Path:
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
                "document_types": "1.0.0",
                "state_patterns": "1.0.0",
                "company_codes": "1.0.0",  # Keep
                "regulatory_actions": "1.0.0",
                "product_categories": "1.0.0",
                "validation_rules": "1.0.0",
                "relationships": "1.0.0",
                "status_workflows": "1.0.0",
                "email_classification": "1.0.0",  # Added, email classification uses many of these rules
                "clients": "1.0.0",  # Added Clients file
            },
            "migrations_required": {},
        }
    }

    with open(config_dir / "version_control.yaml", "w") as f:
        yaml.dump(version_control, f)

    return config_dir


@pytest.fixture
def test_documents_dir(tmp_path) -> Path:
    """Create a temporary directory with test documents."""
    docs_dir = tmp_path / "documents"
    docs_dir.mkdir()

    # Create test documents
    documents = {
        "test_license.txt": """
        ARB License Application
        State of Alabama
        License Number: LIC-2024-001
        Date: 2024-02-11
        """,
        "test_registration.txt": """
        BIN Registration Form
        California Department
        Registration: REG-2024-002
        Amount: $500.00
        """,
    }

    for filename, content in documents.items():
        with open(docs_dir / filename, "w") as f:
            f.write(content)

    return docs_dir


@pytest.fixture
def mock_email_message():
    """Create a mock email message for testing."""
    from email.message import EmailMessage

    msg = EmailMessage()
    msg["Subject"] = "ARB AL License Renewal 2024-25"
    msg["From"] = "test@example.com"
    msg["Date"] = "Mon, 11 Feb 2024 15:30:00 -0500"
    msg["Message-ID"] = "<test123@example.com>"
    msg.set_content(
        """
    Please find attached our license renewal application for Alabama.
    
    Best regards,
    Test Company
    """
    )

    # Add a test attachment
    attachment_content = """
    ARB License Renewal
    State of Alabama
    License Number: LIC-2024-003
    Date: 2024-02-11
    """
    msg.add_attachment(
        attachment_content.encode(),
        maintype="application",
        subtype="pdf",
        filename="renewal.pdf",
    )

    return msg


@pytest.fixture
def mock_gemini_response():
    """Create a mock Gemini API response."""
    return {
        "document_type": "license",
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
def mock_docling_doc():
    """Create a mock Docling document object."""

    class MockDoc:
        def __init__(self):
            self.page_count = 1
            self.has_tables = False
            self.extraction_confidence = 0.85

        def get_text(self):
            return """
            ARB License Application
            State of Alabama
            License Number: LIC-2024-001
            Date: 2024-02-11
            """

        def get_summary(self):
            return "License application for ARB in Alabama"

        def extract_entities(self, entity_type):
            if entity_type == "ORG":
                return ["ARB"]
            elif entity_type == "PRODUCT":
                return ["Fertilizer"]
            return []

        def extract_dates(self):
            return ["2024-02-11"]

        def extract_patterns(self, pattern):
            if "REG-" in pattern or "LIC-" in pattern:
                return ["LIC-2024-001"]
            elif r"\$" in pattern:
                return []
            return []

    return MockDoc()


@pytest.fixture(scope="session")
def workspace_root():
    """Get the workspace root directory."""
    return Path(__file__).parents[1]


@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    """Mock environment variables."""
    monkeypatch.setenv("GOOGLE_API_KEY", "test_key")
    monkeypatch.setenv("TESTING", "true")
