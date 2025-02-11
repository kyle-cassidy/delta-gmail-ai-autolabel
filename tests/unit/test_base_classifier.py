import pytest
from pathlib import Path
from src.classifiers.base import BaseDocumentClassifier, ClassificationResult

def test_classification_result_model():
    """Test the ClassificationResult model validation."""
    # Test valid result
    valid_result = ClassificationResult(
        document_type="registration",
        confidence=0.95,
        entities={"companies": ["Test Corp"], "products": [], "states": ["CA"]},
        key_fields={"dates": ["2024-02-11"], "registration_numbers": [], "amounts": []},
        metadata={"classifier": "test", "has_tables": False},
        summary="Test document",
        flags=[]
    )
    assert valid_result.document_type == "registration"
    assert valid_result.confidence == 0.95

    # Test optional fields
    null_type_result = ClassificationResult(
        document_type=None,
        confidence=0.0,
        entities={"companies": [], "products": [], "states": []},
        key_fields={"dates": [], "registration_numbers": [], "amounts": []},
        metadata={},
        summary=None,
        flags=["ERROR"]
    )
    assert null_type_result.document_type is None
    assert null_type_result.summary is None

    # Test invalid result should raise validation error
    with pytest.raises(ValueError):
        ClassificationResult(
            document_type="registration",
            confidence="not a float",  # Invalid type
            entities={},
            key_fields={},
            metadata={},
            summary=None,
            flags=[]
        ) 