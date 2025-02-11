import pytest
from pathlib import Path
from src.classifiers.domain_config import DomainConfig

@pytest.fixture
def domain_config(tmp_path):
    """Create a temporary domain config for testing."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    
    # Create test config files
    product_categories = {
        "product_categories": {
            "pesticide": {
                "canonical_name": "pesticide",
                "patterns": [
                    {"regex": r"pest(?:icide)?s?"}
                ]
            }
        }
    }
    
    regulatory_actions = {
        "regulatory_actions": {
            "registration": {
                "canonical_name": "registration",
                "patterns": [
                    {"regex": r"(?:new|initial)\s*registration"}
                ]
            }
        }
    }
    
    state_patterns = {
        "states": {
            "CA": {
                "name": "California",
                "patterns": [
                    {"regex": r"(?i)\b(CA|California|Calif)\b",
                     "confidence": 0.95}
                ]
            }
        }
    }
    
    validation_rules = {
        "registration_numbers": {
            "CA": {
                "pattern": r"CA-\d{4}-\d{2}"
            }
        }
    }
    
    # Write test configs
    import yaml
    with open(config_dir / "product_categories.yaml", "w") as f:
        yaml.dump(product_categories, f)
    with open(config_dir / "regulatory_actions.yaml", "w") as f:
        yaml.dump(regulatory_actions, f)
    with open(config_dir / "state_patterns.yaml", "w") as f:
        yaml.dump(state_patterns, f)
    with open(config_dir / "validation_rules.yaml", "w") as f:
        yaml.dump(validation_rules, f)
    
    return DomainConfig(config_dir)

def test_get_document_type(domain_config):
    """Test document type detection."""
    # Test valid document type
    text = "This is a new registration application"
    assert domain_config.get_document_type(text) == "registration"
    
    # Test no match
    text = "This is an unrelated document"
    assert domain_config.get_document_type(text) is None

def test_get_product_categories(domain_config):
    """Test product category detection."""
    # Test valid category
    text = "Application for pesticide registration"
    categories = domain_config.get_product_categories(text)
    assert "pesticide" in categories
    
    # Test no match
    text = "Unrelated product document"
    assert len(domain_config.get_product_categories(text)) == 0

def test_get_states(domain_config):
    """Test state detection."""
    # Test valid state
    text = "Application for CA registration"
    states = domain_config.get_states(text)
    assert "CA" in states
    
    # Test full state name
    text = "Application in California"
    states = domain_config.get_states(text)
    assert "CA" in states
    
    # Test no match
    text = "No state mentioned"
    assert len(domain_config.get_states(text)) == 0

def test_validate_registration_number(domain_config):
    """Test registration number validation."""
    # Test valid CA number
    assert domain_config.validate_registration_number("CA-2024-01", "CA")
    
    # Test invalid CA number
    assert not domain_config.validate_registration_number("XX-1234", "CA")
    
    # Test unknown state (should pass)
    assert domain_config.validate_registration_number("XX-1234", "XX") 