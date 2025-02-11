"""
Integration tests using labeled PDF documents.
"""
import pytest
from pathlib import Path
from src.services.classification_service import ClassificationService
from src.client.attachment import extract_text_from_attachment
import os

@pytest.mark.asyncio
async def test_labeled_documents(labeled_documents_dir, document_metadata, test_config_dir):
    """Test classification of labeled PDF documents."""
    service = ClassificationService(config_dir=test_config_dir)
    
    # Track overall accuracy metrics
    total_docs = 0
    correct_types = 0
    correct_clients = 0
    correct_states = 0
    
    # Process each document in the labeled directory
    for doc_type in ["approvals", "denials", "requests"]:
        doc_dir = labeled_documents_dir / doc_type
        if not doc_dir.exists():
            continue
            
        for pdf_file in doc_dir.glob("*.pdf"):
            if pdf_file.name not in document_metadata:
                print(f"Warning: No metadata found for {pdf_file.name}")
                continue
                
            total_docs += 1
            expected = document_metadata[pdf_file.name]
            
            # Extract text from PDF
            with open(pdf_file, "rb") as f:
                pdf_bytes = f.read()
            document_text = extract_text_from_attachment(pdf_bytes, "pdf")
            
            # Classify the document
            result = await service.classify_document(document_text)
            
            # Compare with expected results
            if result.document_type == expected["document_type"]:
                correct_types += 1
            if result.entities["companies"] == expected["expected_entities"]["companies"]:
                correct_clients += 1
            if result.entities["states"] == expected["expected_entities"]["states"]:
                correct_states += 1
                
            # Print detailed results for this document
            print(f"\nResults for {pdf_file.name}:")
            print(f"Document Type: {result.document_type} (Expected: {expected['document_type']})")
            print(f"Client: {result.entities['companies']} (Expected: {expected['expected_entities']['companies']})")
            print(f"State: {result.entities['states']} (Expected: {expected['expected_entities']['states']})")
            print(f"Confidence: {result.confidence}")
            
            # Assert key expectations
            assert result.confidence >= 0.5, f"Low confidence ({result.confidence}) for {pdf_file.name}"
            
            # Check for required fields
            assert result.document_type is not None, f"Missing document type for {pdf_file.name}"
            assert result.entities["companies"], f"No companies found for {pdf_file.name}"
            assert result.entities["states"], f"No states found for {pdf_file.name}"
            
            # Verify key fields are present if expected
            if "expected_key_fields" in expected:
                for field_type, expected_values in expected["expected_key_fields"].items():
                    if expected_values:
                        assert result.key_fields.get(field_type), \
                            f"Missing expected key field {field_type} in {pdf_file.name}"
    
    # Print overall accuracy metrics
    if total_docs > 0:
        print("\nOverall Accuracy Metrics:")
        print(f"Document Type Accuracy: {correct_types/total_docs:.2%}")
        print(f"Client Detection Accuracy: {correct_clients/total_docs:.2%}")
        print(f"State Detection Accuracy: {correct_states/total_docs:.2%}")
    else:
        print("\nNo labeled documents found to test.")

@pytest.mark.asyncio
async def test_specific_document(labeled_documents_dir, document_metadata, test_config_dir):
    """
    Test a specific labeled document. Useful for debugging classification issues.
    Set the DOC_NAME environment variable to test a specific document.
    """
    doc_name = os.getenv("DOC_NAME")
    if not doc_name:
        pytest.skip("No document specified. Set DOC_NAME environment variable to test a specific document.")
        
    service = ClassificationService(config_dir=test_config_dir)
    
    # Find the document
    pdf_file = None
    for doc_type in ["approvals", "denials", "requests"]:
        potential_file = labeled_documents_dir / doc_type / doc_name
        if potential_file.exists():
            pdf_file = potential_file
            break
    
    if not pdf_file:
        pytest.fail(f"Document {doc_name} not found in labeled documents directory.")
        
    if doc_name not in document_metadata:
        pytest.fail(f"No metadata found for {doc_name}")
        
    # Extract and classify
    with open(pdf_file, "rb") as f:
        pdf_bytes = f.read()
    document_text = extract_text_from_attachment(pdf_bytes, "pdf")
    result = await service.classify_document(document_text)
    
    # Print detailed results
    print(f"\nDetailed results for {doc_name}:")
    print(f"Document Type: {result.document_type}")
    print(f"Confidence: {result.confidence}")
    print("\nEntities:")
    for entity_type, entities in result.entities.items():
        print(f"  {entity_type}: {entities}")
    print("\nKey Fields:")
    for field_type, fields in result.key_fields.items():
        print(f"  {field_type}: {fields}")
    if result.flags:
        print("\nFlags:", result.flags)
    if result.summary:
        print("\nSummary:", result.summary)
        
    # Compare with expected results
    expected = document_metadata[doc_name]
    assert result.document_type == expected["document_type"], \
        f"Wrong document type. Got {result.document_type}, expected {expected['document_type']}"
    assert set(result.entities["companies"]) == set(expected["expected_entities"]["companies"]), \
        "Company mismatch"
    assert set(result.entities["states"]) == set(expected["expected_entities"]["states"]), \
        "State mismatch" 