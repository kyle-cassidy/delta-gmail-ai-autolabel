"""
Integration tests for the classification service.
"""
import pytest
from pathlib import Path
from src.services.classification_service import ClassificationService

@pytest.mark.asyncio
async def test_classify_email(test_config_dir, mock_email_message):
    """Test classification of an email message with attachments."""
    service = ClassificationService(config_dir=test_config_dir)
    
    results = await service.classify_email(mock_email_message)
    
    assert len(results) == 2  # One for body, one for attachment
    
    # Check email body classification
    body_result = results[0]
    assert body_result.document_type is not None
    assert body_result.confidence > 0
    assert "ARB" in body_result.entities["companies"]
    assert "AL" in body_result.entities["states"]
    
    # Check attachment classification
    attachment_result = results[1]
    assert attachment_result.document_type == "license"
    assert attachment_result.confidence > 0
    assert "ARB" in attachment_result.entities["companies"]
    assert "LIC-2024-003" in attachment_result.key_fields["registration_numbers"]

@pytest.mark.asyncio
async def test_classify_standalone_document(test_config_dir, test_documents_dir):
    """Test classification of a standalone document."""
    service = ClassificationService(config_dir=test_config_dir)
    
    # Test license document
    license_file = test_documents_dir / "test_license.txt"
    result = await service.classify_document(license_file)
    
    assert result.document_type == "license"
    assert "ARB" in result.entities["companies"]
    assert "AL" in result.entities["states"]
    assert "LIC-2024-001" in result.key_fields["registration_numbers"]
    
    # Test registration document
    reg_file = test_documents_dir / "test_registration.txt"
    result = await service.classify_document(reg_file)
    
    assert result.document_type == "registration"
    assert "BIN" in result.entities["companies"]
    assert "CA" in result.entities["states"]
    assert "REG-2024-002" in result.key_fields["registration_numbers"]
    assert "$500.00" in result.key_fields["amounts"]

@pytest.mark.asyncio
async def test_batch_classification(test_config_dir, test_documents_dir):
    """Test batch classification of multiple documents."""
    service = ClassificationService(config_dir=test_config_dir)
    
    # Get all test documents
    files = list(test_documents_dir.glob("*.txt"))
    assert len(files) > 0
    
    results = await service.classify_batch(files)
    
    assert len(results) == len(files)
    for result in results:
        assert result.document_type in ["license", "registration"]
        assert result.confidence > 0
        assert len(result.entities["companies"]) > 0
        assert len(result.entities["states"]) > 0

@pytest.mark.asyncio
async def test_classifier_selection(test_config_dir, test_documents_dir):
    """Test using different classifiers."""
    # Test with Docling classifier
    service_docling = ClassificationService(
        config_dir=test_config_dir,
        classifier_name="docling"
    )
    
    # Test with Gemini classifier
    service_gemini = ClassificationService(
        config_dir=test_config_dir,
        classifier_name="gemini"
    )
    
    test_file = test_documents_dir / "test_license.txt"
    
    result_docling = await service_docling.classify_document(test_file)
    result_gemini = await service_gemini.classify_document(test_file)
    
    # Both should identify the document type and key entities
    assert result_docling.document_type == "license"
    assert result_gemini.document_type == "license"
    assert "ARB" in result_docling.entities["companies"]
    assert "ARB" in result_gemini.entities["companies"]

@pytest.mark.asyncio
async def test_error_handling(test_config_dir):
    """Test error handling in the service."""
    service = ClassificationService(config_dir=test_config_dir)
    
    # Test with non-existent file
    with pytest.raises(FileNotFoundError):
        await service.classify_document(Path("/nonexistent/file.pdf"))
    
    # Test with invalid classifier name
    with pytest.raises(ValueError):
        ClassificationService(
            config_dir=test_config_dir,
            classifier_name="invalid_classifier"
        )
    
    # Test with invalid email message
    with pytest.raises(AttributeError):
        await service.classify_email("not_an_email_message") 