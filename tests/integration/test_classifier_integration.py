import pytest
from pathlib import Path
import os
import PyPDF2
from src.classifiers.factory import ClassifierFactory
from src.classifiers.base import ClassificationResult

# Skip tests if API keys are not available
SKIP_GEMINI = os.getenv("GOOGLE_API_KEY") is None

def validate_pdf(file_path: Path) -> bool:
    """
    Validate PDF file for Gemini API requirements.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        bool: Whether the file is valid for processing
        
    Raises:
        ValueError: If file exceeds size or page limits
    """
    # Check file size (20MB limit)
    file_size = file_path.stat().st_size
    if file_size > 20 * 1024 * 1024:
        raise ValueError(f"File {file_path.name} exceeds 20MB limit")
    
    # Check page count (3600 page limit)
    with open(file_path, 'rb') as f:
        pdf = PyPDF2.PdfReader(f)
        if len(pdf.pages) > 3600:
            raise ValueError(f"File {file_path.name} exceeds 3600 page limit")
    
    return True

@pytest.fixture
def test_documents(tmp_path):
    """Create or load test documents."""
    fixtures_dir = Path(__file__).parents[1] / "fixtures" / "documents"
    if not fixtures_dir.exists():
        pytest.skip("Test documents not available")
    
    # Get all PDF files and validate them
    valid_docs = []
    for doc in fixtures_dir.glob("*.pdf"):
        try:
            if validate_pdf(doc):
                valid_docs.append(doc)
        except ValueError as e:
            print(f"Skipping {doc.name}: {str(e)}")
    
    if not valid_docs:
        pytest.skip("No valid test documents available")
    return valid_docs

@pytest.fixture
def gemini_classifier():
    """Create a Gemini classifier instance."""
    if SKIP_GEMINI:
        pytest.skip("GOOGLE_API_KEY not available")
    return ClassifierFactory.create_classifier("gemini")

@pytest.fixture
def docling_classifier():
    """Create a Docling classifier instance."""
    return ClassifierFactory.create_classifier("docling")

@pytest.mark.asyncio
@pytest.mark.skipif(SKIP_GEMINI, reason="GOOGLE_API_KEY not available")
async def test_gemini_integration(gemini_classifier, test_documents):
    """Test Gemini classifier with real documents."""
    for doc in test_documents:
        result = await gemini_classifier.classify_document(doc)
        assert isinstance(result, ClassificationResult)
        assert result.confidence > 0
        assert result.document_type is not None
        assert "CLASSIFICATION_ERROR" not in result.flags
        
        # Verify Gemini-specific metadata
        assert "model" in result.metadata
        assert "gemini-pro-vision" in result.metadata["model"]

@pytest.mark.asyncio
async def test_docling_integration(docling_classifier, test_documents):
    """Test Docling classifier with real documents."""
    for doc in test_documents:
        result = await docling_classifier.classify_document(doc)
        assert isinstance(result, ClassificationResult)
        assert result.confidence > 0
        assert result.document_type is not None
        assert "CLASSIFICATION_ERROR" not in result.flags

@pytest.mark.asyncio
async def test_classifier_comparison(gemini_classifier, docling_classifier, test_documents):
    """Compare results between different classifiers."""
    if SKIP_GEMINI:
        pytest.skip("GOOGLE_API_KEY not available")
    
    for doc in test_documents:
        gemini_result = await gemini_classifier.classify_document(doc)
        docling_result = await docling_classifier.classify_document(doc)
        
        # Compare document types
        if gemini_result.document_type and docling_result.document_type:
            assert gemini_result.document_type == docling_result.document_type
        
        # Compare entity detection
        for entity_type in ["companies", "products", "states"]:
            gemini_entities = set(gemini_result.entities[entity_type])
            docling_entities = set(docling_result.entities[entity_type])
            common_entities = gemini_entities.intersection(docling_entities)
            
            # At least some entities should match between classifiers
            if gemini_entities and docling_entities:
                assert len(common_entities) > 0

@pytest.mark.asyncio
async def test_batch_processing(gemini_classifier, docling_classifier, test_documents):
    """Test batch processing with both classifiers."""
    if SKIP_GEMINI:
        pytest.skip("GOOGLE_API_KEY not available")
    
    # Process with both classifiers
    gemini_results = await gemini_classifier.classify_batch(test_documents)
    docling_results = await docling_classifier.classify_batch(test_documents)
    
    # Verify results
    assert len(gemini_results) == len(test_documents)
    assert len(docling_results) == len(test_documents)
    
    for gemini_result, docling_result in zip(gemini_results, docling_results):
        assert isinstance(gemini_result, ClassificationResult)
        assert isinstance(docling_result, ClassificationResult)
        assert "CLASSIFICATION_ERROR" not in gemini_result.flags
        assert "CLASSIFICATION_ERROR" not in docling_result.flags

@pytest.mark.asyncio
async def test_large_document_handling(gemini_classifier, tmp_path):
    """Test handling of documents that exceed Gemini API limits."""
    # Create a test document that's too large
    large_doc = tmp_path / "large.pdf"
    with open(large_doc, 'wb') as f:
        f.write(b'0' * (21 * 1024 * 1024))  # 21MB
    
    with pytest.raises(ValueError, match="exceeds 20MB limit"):
        await gemini_classifier.classify_document(large_doc) 