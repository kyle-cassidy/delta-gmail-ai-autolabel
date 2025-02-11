"""
Shared test configuration and fixtures.
"""
import pytest
from pathlib import Path
import yaml
import sys
from unittest.mock import MagicMock

# Add mocks directory to Python path
MOCKS_DIR = Path(__file__).parent / "mocks"
sys.path.insert(0, str(MOCKS_DIR))

# Mock external dependencies
try:
    import google.generativeai as genai
except ImportError:
    genai = MagicMock()
    sys.modules['google.generativeai'] = genai

@pytest.fixture(scope="session")
def test_config_dir(tmp_path_factory):
    """Create a temporary configuration directory with test configs."""
    config_dir = tmp_path_factory.mktemp("config")
    
    # Create test configuration files
    configs = {
        "product_categories.yaml": {
            "product_categories": {
                "pesticide": {
                    "canonical_name": "pesticide",
                    "patterns": [{"regex": r"pest(?:icide)?s?"}]
                },
                "fertilizer": {
                    "canonical_name": "fertilizer",
                    "patterns": [{"regex": r"fertili[sz]ers?"}]
                }
            }
        },
        "regulatory_actions.yaml": {
            "regulatory_actions": {
                "registration": {
                    "canonical_name": "registration",
                    "patterns": [{"regex": r"(?:new|initial)\s*registration"}]
                },
                "renewal": {
                    "canonical_name": "renewal",
                    "patterns": [{"regex": r"renew(?:al)?"}]
                }
            }
        },
        "state_specific.yaml": {
            "states": {
                "CA": {
                    "patterns": [{"regex": r"california|ca\b"}],
                    "registration_format": "CA-\\d{4}-\\d{2}"
                },
                "NY": {
                    "patterns": [{"regex": r"new\s*york|ny\b"}],
                    "registration_format": "NY\\d{6}"
                }
            }
        },
        "validation_rules.yaml": {
            "registration_numbers": {
                "CA": {"pattern": r"CA-\d{4}-\d{2}"},
                "NY": {"pattern": r"NY\d{6}"}
            }
        },
        "relationships.yaml": {
            "document_relationships": {
                "registration": ["renewal", "amendment"],
                "renewal": ["registration", "amendment"],
                "amendment": ["registration", "renewal"]
            }
        }
    }
    
    # Write configuration files
    for filename, content in configs.items():
        config_file = config_dir / filename
        with open(config_file, "w") as f:
            yaml.dump(content, f)
    
    return config_dir

@pytest.fixture(scope="session")
def test_documents_dir(tmp_path_factory):
    """Create a directory for test documents."""
    return tmp_path_factory.mktemp("documents")

@pytest.fixture(scope="session")
def workspace_root():
    """Get the workspace root directory."""
    return Path(__file__).parents[1]

@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    """Mock environment variables."""
    monkeypatch.setenv("GOOGLE_API_KEY", "test_key")
    monkeypatch.setenv("TESTING", "true") 