import pytest
from pathlib import Path
import json
from unittest.mock import patch, MagicMock
from src.classifiers.gemini import GeminiClassifier
from src.classifiers.base import ClassificationResult
import io

@pytest.fixture
def mock_response():
    """Create a mock Gemini API response."""
    response = MagicMock()
    response.text = json.dumps({
        "document_type": "registration",
        "entities": {
            "companies": ["Test Corp"],
            "products": ["Test Product"],
            "states": ["CA"]
        },
        "key_fields": {
            "dates": ["2024-02-11"],
            "registration_numbers": ["CA-2024-01"],
            "amounts": ["$1000.00"]
        },
        "tables": [],
        "summary": "Test document summary"
    })
    return response

@pytest.fixture
def mock_state_patterns():
    """Create mock state patterns configuration."""
    return {
        "states": {
            "CA": {
                "name": "California",
                "patterns": [
                    {"regex": r"(?i)\bCA\b"}
                ]
            }
        }
    }

@pytest.fixture
def gemini_classifier(mock_response, mock_state_patterns, tmp_path):
    """Create a Gemini classifier instance with mocked API."""
    # Create a temporary config directory
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    
    # Write mock state patterns
    with open(config_dir / "state_patterns.yaml", "w") as f:
        import yaml
        yaml.dump(mock_state_patterns, f)
    
    with patch('google.generativeai.configure'), \
         patch('google.generativeai.GenerativeModel') as mock_model_class:
        # Set up the mock model
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        classifier = GeminiClassifier(api_key="test_key", config_dir=config_dir)
        classifier.model = mock_model  # Replace the model with our mock
        yield classifier

@pytest.mark.asyncio
async def test_classify_document(gemini_classifier, tmp_path):
    """Test document classification."""
    # Create a test document
    test_file = tmp_path / "test.pdf"
    test_file.write_bytes(b"Test PDF content with CA registration")
    
    # Mock PDF reader to avoid actual PDF parsing
    with patch('PyPDF2.PdfReader') as mock_reader:
        mock_reader.return_value.pages = [None] * 10  # Mock 10 pages
        
        # Classify the document
        result = await gemini_classifier.classify_document(test_file)
        
        # Verify the result
        assert isinstance(result, ClassificationResult)
        assert result.document_type == "registration"
        assert result.entities["companies"] == ["Test Corp"]
        assert result.entities["states"] == ["CA"]
        assert result.key_fields["registration_numbers"] == ["CA-2024-01"]
        assert result.confidence > 0

@pytest.mark.asyncio
async def test_file_size_limit(gemini_classifier, tmp_path):
    """Test file size limit handling."""
    # Create a large test document (>20MB)
    test_file = tmp_path / "large.pdf"
    with open(test_file, 'wb') as f:
        f.write(b'0' * (21 * 1024 * 1024))  # 21MB
    
    # Should raise an error for large file
    with pytest.raises(ValueError, match="File size exceeds 20MB limit"):
        await gemini_classifier.classify_document(test_file)

@pytest.mark.asyncio
async def test_page_limit(gemini_classifier, tmp_path):
    """Test page limit handling."""
    # Create a test PDF
    test_file = tmp_path / "test.pdf"
    test_file.write_bytes(b"Test PDF content")
    
    with patch('PyPDF2.PdfReader') as mock_reader:
        # Mock a PDF with too many pages
        mock_reader.return_value.pages = [None] * 4000  # More than 3600 pages
        
        with pytest.raises(ValueError, match="Document exceeds 3600 page limit"):
            await gemini_classifier.classify_document(test_file)

@pytest.mark.asyncio
async def test_classify_batch(gemini_classifier, tmp_path):
    """Test batch classification."""
    # Create test documents
    files = []
    for i in range(3):
        test_file = tmp_path / f"test_{i}.pdf"
        test_file.write_bytes(b"Test PDF content with CA registration")
        files.append(test_file)
    
    # Mock PDF reader for all files
    with patch('PyPDF2.PdfReader') as mock_reader:
        mock_reader.return_value.pages = [None] * 10  # Mock 10 pages
        
        # Classify batch
        results = await gemini_classifier.classify_batch(files, max_concurrent=2)
        
        # Verify results
        assert len(results) == 3
        for result in results:
            assert isinstance(result, ClassificationResult)
            assert result.document_type == "registration"
            assert result.entities["states"] == ["CA"]

@pytest.mark.asyncio
async def test_error_handling(gemini_classifier, tmp_path):
    """Test error handling."""
    # Test with non-existent file
    with pytest.raises(FileNotFoundError):
        await gemini_classifier.classify_document("nonexistent.pdf")
    
    # Create a test file for invalid JSON response
    test_file = tmp_path / "test.pdf"
    test_file.write_bytes(b"Test PDF content")
    
    # Test with invalid API response
    with patch('PyPDF2.PdfReader') as mock_reader, \
         patch.object(gemini_classifier.model, 'generate_content') as mock_generate:
        mock_reader.return_value.pages = [None] * 10
        mock_response = MagicMock()
        mock_response.text = "Invalid JSON"
        mock_generate.return_value = mock_response
        
        result = await gemini_classifier.classify_document(test_file)
        assert "CLASSIFICATION_ERROR" in result.flags
        assert "Failed to parse Gemini response as JSON" in result.metadata["error"]

def test_classifier_info(gemini_classifier):
    """Test classifier information."""
    info = gemini_classifier.get_classifier_info()
    assert "name" in info
    assert "version" in info
    assert "Gemini" in info["name"]
    assert "Flash" in info["name"]  # Ensure we're using Gemini Flash 