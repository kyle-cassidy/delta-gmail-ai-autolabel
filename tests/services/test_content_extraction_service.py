import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.services.content_extraction_service import ContentExtractionService

@pytest.fixture
def mock_response():
    response = MagicMock()
    response.text = """{
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
        "summary": "Test document"
    }"""
    return response

@pytest.fixture
def mock_genai():
    with patch('google.generativeai') as mock:
        mock_model = MagicMock()
        mock.GenerativeModel.return_value = mock_model
        yield mock

@pytest.fixture
def content_extraction_service(mock_genai, mock_response):
    with patch('google.generativeai.GenerativeModel.generate_content', return_value=mock_response):
        service = ContentExtractionService(api_key="test_key")
        yield service

@pytest.mark.asyncio
async def test_extract_content(content_extraction_service, mock_response, tmp_path):
    # Create a test file
    test_file = tmp_path / "test.pdf"
    test_file.write_bytes(b"Test content")
    
    # Extract content
    result = await content_extraction_service.extract_content(test_file)
    
    # Verify structure
    assert "document_type" in result
    assert "entities" in result
    assert "key_fields" in result
    assert "tables" in result
    assert "summary" in result
    
    # Verify content
    assert result["document_type"] == "registration"
    assert "Test Corp" in result["entities"]["companies"]
    assert "CA" in result["entities"]["states"]
    assert "CA-2024-01" in result["key_fields"]["registration_numbers"]

@pytest.mark.asyncio
async def test_batch_extract(content_extraction_service, mock_response, tmp_path):
    # Create test files
    files = []
    for i in range(3):
        test_file = tmp_path / f"test_{i}.pdf"
        test_file.write_bytes(b"Test content")
        files.append(test_file)
    
    # Extract content from batch
    results = await content_extraction_service.batch_extract(files)
    
    # Verify results
    assert len(results) == 3
    for result in results:
        assert result["success"]
        assert result["data"]["document_type"] == "registration"
        assert "Test Corp" in result["data"]["entities"]["companies"]

@pytest.mark.asyncio
async def test_error_handling(content_extraction_service, tmp_path):
    # Test with non-existent file
    with pytest.raises(Exception) as exc_info:
        await content_extraction_service.extract_content("nonexistent.pdf")
    assert "File not found" in str(exc_info.value)
    
    # Test with invalid JSON response
    test_file = tmp_path / "test.pdf"
    test_file.write_bytes(b"Test content")
    
    with patch('google.generativeai.GenerativeModel.generate_content') as mock_generate:
        mock_generate.return_value = MagicMock(text="Invalid JSON")
        with pytest.raises(Exception) as exc_info:
            await content_extraction_service.extract_content(test_file)
        assert "Failed to parse" in str(exc_info.value)