import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.classifiers.docling import DoclingClassifier
from src.classifiers.base import ClassificationResult

@pytest.fixture
def mock_doc():
    """Create a mock Docling document."""
    doc = MagicMock()
    doc.get_text.return_value = "Test document for registration in California"
    doc.extract_entities.side_effect = lambda entity_type: {
        "ORG": ["Test Corp"],
        "PRODUCT": ["Test Product"]
    }[entity_type]
    doc.extract_dates.return_value = ["2024-02-11"]
    doc.extract_patterns.side_effect = lambda pattern: {
        r"REG-?\d+|LIC-?\d+": ["REG-12345"],
        r"\$?\d+(?:,\d{3})*(?:\.\d{2})?": ["$1000.00"]
    }[pattern]
    doc.page_count = 1
    doc.has_tables = False
    doc.extraction_confidence = 0.95
    doc.get_summary.return_value = "Test document summary"
    return doc

@pytest.fixture
def mock_domain_config():
    """Create a mock domain configuration."""
    config = MagicMock()
    config.get_states.return_value = ["CA"]  # Mock state extraction
    config.get_document_type.return_value = "registration"
    config.get_product_categories.return_value = ["fertilizer"]
    config.get_related_documents.return_value = []
    config.validate_registration_number.return_value = True
    return config

@pytest.fixture
def docling_classifier(mock_doc, mock_domain_config, tmp_path):
    """Create a Docling classifier instance with mocked components."""
    with patch('docling.DocProcessor') as mock_processor, \
         patch('docling.TableFormer') as mock_table_former, \
         patch('src.classifiers.docling.DomainConfig') as mock_domain_config_cls:
        # Configure mock processor
        processor_instance = mock_processor.return_value
        processor_instance.process_document.return_value = mock_doc
        
        # Configure mock table former
        table_former_instance = mock_table_former.return_value
        table_former_instance.extract_tables.return_value = []
        
        # Configure mock domain config
        mock_domain_config_cls.return_value = mock_domain_config
        
        classifier = DoclingClassifier(config_dir=tmp_path)
        yield classifier

@pytest.mark.asyncio
async def test_classify_document(docling_classifier, tmp_path):
    """Test document classification."""
    # Create a test document
    test_file = tmp_path / "test.pdf"
    test_file.write_bytes(b"Test PDF content")
    
    # Classify the document
    result = await docling_classifier.classify_document(test_file)
    
    # Verify the result
    assert isinstance(result, ClassificationResult)
    assert result.entities["companies"] == ["Test Corp"]
    assert result.entities["products"] == ["Test Product"]
    assert "CA" in result.entities["states"]
    assert result.key_fields["dates"] == ["2024-02-11"]
    assert result.key_fields["registration_numbers"] == ["REG-12345"]
    assert result.confidence > 0.9

@pytest.mark.asyncio
async def test_classify_batch(docling_classifier, tmp_path):
    """Test batch classification."""
    # Create test documents
    files = []
    for i in range(3):
        test_file = tmp_path / f"test_{i}.pdf"
        test_file.write_bytes(b"Test PDF content")
        files.append(test_file)
    
    # Classify batch
    results = await docling_classifier.classify_batch(files, max_concurrent=2)
    
    # Verify results
    assert len(results) == 3
    for result in results:
        assert isinstance(result, ClassificationResult)
        assert result.confidence > 0.9

@pytest.mark.asyncio
async def test_error_handling(docling_classifier):
    """Test error handling."""
    # Test with non-existent file
    with pytest.raises(FileNotFoundError):
        await docling_classifier.classify_document("nonexistent.pdf")
    
    # Test with processing error
    with patch.object(docling_classifier.processor, 'process_document') as mock_process:
        mock_process.side_effect = Exception("Processing failed")
        result = await docling_classifier.classify_document(Path("test.pdf"))
        assert "CLASSIFICATION_ERROR" in result.flags

def test_classifier_info(docling_classifier):
    """Test classifier information."""
    info = docling_classifier.get_classifier_info()
    assert "name" in info
    assert "version" in info
    assert "Docling" in info["name"]
    assert "features" in info

def test_docling_classifier_initialization(test_config_dir):
    """Test that the DoclingClassifier initializes correctly."""
    classifier = DoclingClassifier(config_dir=test_config_dir)
    assert classifier is not None
    assert classifier.domain_config is not None

@pytest.mark.asyncio
async def test_classify_text_document(test_config_dir, mock_docling_doc, monkeypatch):
    """Test classification of a text document."""
    # Mock the DocProcessor to return our mock document
    class MockProcessor:
        def process_text(self, text):
            return mock_docling_doc
            
    classifier = DoclingClassifier(config_dir=test_config_dir)
    classifier.processor = MockProcessor()
    
    # Test document text
    doc_text = """
    ARB License Application
    State of Alabama
    License Number: LIC-2024-001
    Date: 2024-02-11
    """
    
    result = await classifier.classify_document(
        doc_text,
        source_type="text"
    )
    
    assert isinstance(result, ClassificationResult)
    assert result.document_type == "license"
    assert "ARB" in result.entities["companies"]
    assert "AL" in result.entities["states"]
    assert result.confidence > 0.5
    assert "LIC-2024-001" in result.key_fields["registration_numbers"]

@pytest.mark.asyncio
async def test_classify_batch_documents(test_config_dir, mock_docling_doc, monkeypatch):
    """Test batch classification of documents."""
    # Mock the DocProcessor
    class MockProcessor:
        def process_text(self, text):
            return mock_docling_doc
            
    classifier = DoclingClassifier(config_dir=test_config_dir)
    classifier.processor = MockProcessor()
    
    # Test documents
    documents = [
        "Document 1 content",
        "Document 2 content"
    ]
    
    results = await classifier.classify_batch(
        documents,
        source_type="text"
    )
    
    assert len(results) == 2
    for result in results:
        assert isinstance(result, ClassificationResult)
        assert result.document_type == "license"
        assert result.confidence > 0.5

@pytest.mark.asyncio
async def test_error_handling(test_config_dir):
    """Test error handling in the classifier."""
    classifier = DoclingClassifier(config_dir=test_config_dir)
    
    # Test with invalid source type
    with pytest.raises(ValueError):
        await classifier.classify_document(
            "test content",
            source_type="invalid_type"
        )
    
    # Test with non-existent file
    with pytest.raises(FileNotFoundError):
        await classifier.classify_document(
            Path("/nonexistent/file.pdf"),
            source_type="file"
        )

def test_metadata_enhancement(test_config_dir, mock_docling_doc, monkeypatch):
    """Test that metadata enhances classification results."""
    # Mock the DocProcessor
    class MockProcessor:
        def process_text(self, text):
            return mock_docling_doc
            
    classifier = DoclingClassifier(config_dir=test_config_dir)
    classifier.processor = MockProcessor()
    
    # Create a test document result
    doc_result = {
        "document_type": "license",
        "entities": {
            "companies": ["ARB"],
            "states": ["AL"]
        },
        "key_fields": {
            "dates": ["2024-02-11"],
            "registration_numbers": ["LIC-2024-001"]
        },
        "metadata": {
            "confidence": 0.85
        }
    }
    
    # Test metadata
    metadata = {
        "email_subject": "ARB CA License Application",
        "email_from": "test@example.com"
    }
    
    enhanced = classifier._enhance_with_metadata(doc_result, metadata)
    
    assert "CA" in enhanced["entities"]["states"]
    assert enhanced["metadata"]["source_metadata"] == metadata 