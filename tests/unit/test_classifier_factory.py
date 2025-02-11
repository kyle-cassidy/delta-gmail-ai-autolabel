import pytest
from src.classifiers.factory import ClassifierFactory
from src.classifiers.base import BaseDocumentClassifier
from src.classifiers.gemini import GeminiClassifier
from src.classifiers.docling import DoclingClassifier

def test_default_registry():
    """Test the default classifier registry."""
    available = ClassifierFactory.list_available_classifiers()
    assert "gemini" in available
    assert "docling" in available

def test_register_classifier():
    """Test registering a new classifier."""
    # Create a test classifier
    class TestClassifier(BaseDocumentClassifier):
        async def classify_document(self, file_path):
            return None
        
        async def classify_batch(self, file_paths, max_concurrent=5):
            return []
        
        def get_classifier_info(self):
            return {"name": "Test", "version": "1.0.0", "description": "Test classifier"}
    
    # Register the test classifier
    ClassifierFactory.register_classifier("test", TestClassifier)
    
    # Verify it's available
    available = ClassifierFactory.list_available_classifiers()
    assert "test" in available
    
    # Create an instance
    classifier = ClassifierFactory.create_classifier("test")
    assert isinstance(classifier, TestClassifier)

def test_invalid_registration():
    """Test registering an invalid classifier."""
    class InvalidClassifier:
        pass
    
    with pytest.raises(ValueError):
        ClassifierFactory.register_classifier("invalid", InvalidClassifier)

def test_create_unknown_classifier():
    """Test creating a non-existent classifier."""
    with pytest.raises(ValueError):
        ClassifierFactory.create_classifier("unknown")

def test_create_gemini_classifier():
    """Test creating a Gemini classifier."""
    classifier = ClassifierFactory.create_classifier("gemini", api_key="test_key")
    assert isinstance(classifier, GeminiClassifier)

def test_create_docling_classifier():
    """Test creating a Docling classifier."""
    classifier = ClassifierFactory.create_classifier("docling")
    assert isinstance(classifier, DoclingClassifier) 