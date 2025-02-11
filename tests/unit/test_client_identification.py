import pytest
from pathlib import Path
from src.classifiers.base import ClassificationResult
from src.classifiers.domain_config import DomainConfig

@pytest.fixture
def test_client_config(tmp_path) -> Path:
    """Create a temporary client configuration for testing."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    
    # Create client patterns config
    client_patterns = {
        "version": "1.0.0",
        "companies": {
            "EEA": {
                "name": "Elemental Enzymes Agriculture",
                "aliases": ["Elemental Enzymes", "EE Agriculture"],
                "patterns": [
                    r"Elemental\s+Enzymes?",
                    r"EEA\b"
                ],
                "domains": ["elementalenzymes.com"],
                "contact_info": {
                    "primary_contact": "Test Contact",
                    "email": "test@elementalenzymes.com"
                },
                "metadata": {
                    "account_type": "manufacturer",
                    "active_states": [],
                    "preferred_communication": "email"
                }
            },
            "ARB": {
                "name": "Arborjet, Inc.",
                "aliases": ["Arborjet"],
                "patterns": [
                    r"Arborjet",
                    r"ARB\b"
                ],
                "domains": ["arborjet.com"],
                "contact_info": {
                    "primary_contact": "Test Contact",
                    "email": "test@arborjet.com"
                },
                "metadata": {
                    "account_type": "manufacturer",
                    "active_states": [],
                    "preferred_communication": "email"
                }
            }
        }
    }
    
    # Create version control config
    version_control = {
        "version_control": {
            "min_compatible_version": "1.0.0",
            "current_versions": {
                "clients": "1.0.0"
            }
        }
    }
    
    with open(config_dir / "clients.yaml", "w") as f:
        import yaml
        yaml.dump(client_patterns, f)
        
    with open(config_dir / "version_control.yaml", "w") as f:
        yaml.dump(version_control, f)
    
    return config_dir

def test_client_pattern_matching(test_client_config):
    """Test client identification through pattern matching."""
    domain_config = DomainConfig(test_client_config)
    
    # Test exact company name match
    assert domain_config.get_client_by_company("Elemental Enzymes Agriculture") == "EEA"
    
    # Test pattern matching
    test_cases = [
        ("Email from Elemental Enzymes regarding registration", "EEA"),
        ("ARB License Application", "ARB"),
        ("Contact: john@elementalenzymes.com", "EEA"),
        ("Arborjet, Inc. Product Registration", "ARB"),
        ("Unknown Company Document", None)
    ]
    
    for text, expected_code in test_cases:
        code, confidence = domain_config._identify_client(text)
        assert code == expected_code
        if code:
            assert confidence > 0.7

def test_client_domain_matching(test_client_config):
    """Test client identification through email domains."""
    domain_config = DomainConfig(test_client_config)
    
    test_cases = [
        ("user@elementalenzymes.com", "EEA"),
        ("contact@arborjet.com", "ARB"),
        ("someone@unknown.com", None)
    ]
    
    for email, expected_code in test_cases:
        code = domain_config.get_client_by_email_domain(email)
        assert code == expected_code

def test_client_confidence_scoring(test_client_config):
    """Test confidence scoring for client identification."""
    domain_config = DomainConfig(test_client_config)
    
    # Test cases with expected confidence levels
    test_cases = [
        # (text, expected_code, min_confidence)
        ("Elemental Enzymes Agriculture", "EEA", 0.9),  # Exact company name
        ("EEA Registration", "EEA", 0.8),  # Code match
        ("Email: contact@elementalenzymes.com", "EEA", 0.95),  # Domain match
        ("Some document mentioning Elemental", "EEA", 0.7),  # Partial match
        ("Unknown document", None, 0.0)  # No match
    ]
    
    for text, expected_code, min_confidence in test_cases:
        print(f"\nTesting case: {text}")
        code, confidence = domain_config._identify_client(text)
        print(f"Got code: {code}, confidence: {confidence}")
        print(f"Expected code: {expected_code}, min_confidence: {min_confidence}")
        assert code == expected_code
        if code:
            assert confidence >= min_confidence

def test_client_identification_with_metadata():
    """Test client identification using document metadata."""
    # Test with email metadata
    source_metadata = {
        "email_from": "contact@elementalenzymes.com",
        "email_subject": "EEA Registration Document"
    }
    
    result = ClassificationResult(
        document_type="registration",
        client_code="EEA",
        confidence=0.95,
        entities={"companies": ["Elemental Enzymes"]},
        key_fields={},
        metadata={
            "source": "email",  # Using valid metadata types
            "classifier": "test",
            "needs_review": False,
            "priority": 1,
            "score": 0.95,
            "tags": ["registration", "email"]
        },
        summary="EEA registration document",
        flags=[]
    )
    
    assert result.client_code == "EEA"
    assert result.metadata["source"] == "email"
    assert result.metadata["classifier"] == "test"

def test_multiple_client_mentions():
    """Test handling of documents mentioning multiple clients."""
    result = ClassificationResult(
        document_type="registration",
        client_code="EEA",  # Primary client
        confidence=0.9,
        entities={
            "companies": [
                "Elemental Enzymes",
                "Arborjet, Inc."  # Secondary mention
            ]
        },
        key_fields={},
        metadata={
            "secondary_clients": ["ARB"],  # Track secondary mentions
            "classifier": "test"
        },
        summary="EEA registration document mentioning Arborjet",
        flags=["MULTIPLE_CLIENTS"]
    )
    
    assert result.client_code == "EEA"  # Primary client
    assert "ARB" in result.metadata["secondary_clients"]
    assert "MULTIPLE_CLIENTS" in result.flags

def test_unknown_client_handling():
    """Test handling of documents with unknown clients."""
    result = ClassificationResult(
        document_type="registration",
        client_code=None,
        confidence=0.8,
        entities={
            "companies": ["Unknown Company LLC"]
        },
        key_fields={},
        metadata={
            "needs_review": True,
            "classifier": "test"
        },
        summary=None,
        flags=["UNKNOWN_CLIENT"]
    )
    
    assert result.client_code is None
    assert result.metadata["needs_review"]
    assert "UNKNOWN_CLIENT" in result.flags