"""
Tests for document helper utilities.
"""
import pytest
from pathlib import Path
from datetime import datetime
from ..utils.document_helpers import (
    parse_document_filename,
    generate_document_metadata,
    update_test_documents
)

def test_parse_document_filename():
    """Test parsing document filenames."""
    # Test basic filename
    result = parse_document_filename("AL-ARB-RENEW.pdf")
    assert result["state"] == "AL"
    assert result["client"] == "ARB"
    assert result["base_type"] == "RENEW"
    assert result["description"] is None
    
    # Test filename with description
    result = parse_document_filename("IL-ARB-NEW-nutriroot.pdf")
    assert result["state"] == "IL"
    assert result["client"] == "ARB"
    assert result["base_type"] == "NEW"
    assert result["description"] == "nutriroot"
    
    # Test invalid filename
    with pytest.raises(ValueError):
        parse_document_filename("invalid-filename.pdf")

def test_generate_document_metadata():
    """Test metadata generation."""
    # Create test file
    test_file = Path("test.pdf")
    creation_date = datetime(2024, 2, 11)
    
    metadata = generate_document_metadata(
        "AL-ARB-RENEW.pdf",
        test_file,
        creation_date
    )
    
    assert metadata["document_type"] == "renewal"
    assert metadata["workflow_state"] == "submitted"
    assert metadata["base_type"] == "RENEW"
    assert metadata["client"] == "ARB"
    assert metadata["state"] == "AL"
    assert metadata["creation_date"] == "2024-02-11T00:00:00"
    assert metadata["expected_entities"]["companies"] == ["ARB"]
    assert metadata["expected_entities"]["states"] == ["AL"]
    assert "2024-02-11" in metadata["expected_key_fields"]["dates"]

def test_update_test_documents(tmp_path):
    """Test document organization and metadata updates."""
    # Create test document structure
    documents_dir = tmp_path / "documents"
    documents_dir.mkdir()
    (documents_dir / "PDF").mkdir()
    
    # Create test PDF files
    test_files = [
        "AL-ARB-RENEW.pdf",
        "IL-ARB-NEW-nutriroot.pdf"
    ]
    
    for filename in test_files:
        with open(documents_dir / "PDF" / filename, "wb") as f:
            f.write(b"Test PDF content")
    
    # Create labeled documents directory
    labeled_dir = tmp_path / "labeled_documents"
    
    # Update documents
    update_test_documents(documents_dir, labeled_dir)
    
    # Verify directory structure
    assert (labeled_dir / "renewals").exists()
    assert (labeled_dir / "requests").exists()
    assert (labeled_dir / "approvals").exists()
    assert (labeled_dir / "metadata.json").exists()
    
    # Verify metadata
    with open(labeled_dir / "metadata.json") as f:
        metadata = json.load(f)
    
    assert len(metadata) == len(test_files)
    for entry in metadata.values():
        assert "document_type" in entry
        assert "workflow_state" in entry
        assert "expected_entities" in entry 