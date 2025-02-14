"""
Test document management utilities.
"""
import re
from datetime import datetime
from pathlib import Path
import shutil
import json
from typing import Dict, Optional

def parse_document_filename(filename: str) -> Dict:
    """
    Parse a document filename following the convention:
    {STATE}-{CLIENT}-{BASE_TYPE}[-description]
    
    Example: AL-ARB-RENEW.pdf -> 
    {
        "state": "AL",
        "client": "ARB",
        "base_type": "RENEW"
    }
    """
    # Remove file extension and split by hyphens
    name = Path(filename).stem
    parts = name.split('-')
    
    if len(parts) < 3:
        raise ValueError(f"Invalid filename format: {filename}")
        
    metadata = {
        "state": parts[0],
        "client": parts[1],
        "base_type": parts[2],
        "description": "-".join(parts[3:]) if len(parts) > 3 else None
    }
    
    return metadata

def generate_document_metadata(filename: str, 
                             document_path: Path,
                             creation_date: Optional[datetime] = None) -> Dict:
    """
    Generate metadata for a test document based on its filename and attributes.
    
    Args:
        filename: Document filename following our naming convention
        document_path: Path to the actual document
        creation_date: Optional creation date (defaults to file creation time)
        
    Returns:
        Dictionary of metadata suitable for metadata.json
    """
    # Parse basic info from filename
    parsed = parse_document_filename(filename)
    
    # Get document creation date
    if not creation_date:
        creation_date = datetime.fromtimestamp(document_path.stat().st_ctime)
    
    # Map BASE_TYPE to workflow state and document type
    type_to_state = {
        "NEW": "submitted",
        "RENEW": "submitted",
        "TONNAGE": "submitted",
        "CERT": "approved",
        "LABEL": "submitted"
    }
    
    type_to_doc = {
        "NEW": "registration",
        "RENEW": "renewal",
        "TONNAGE": "tonnage",
        "CERT": "approval",
        "LABEL": "amendment"
    }
    
    # Generate metadata structure
    metadata = {
        "document_type": type_to_doc.get(parsed["base_type"], "unknown"),
        "workflow_state": type_to_state.get(parsed["base_type"], "unknown"),
        "base_type": parsed["base_type"],
        "client": parsed["client"],
        "state": parsed["state"],
        "confidence": 1.0,
        "creation_date": creation_date.isoformat(),
        "expected_entities": {
            "companies": [parsed["client"]],
            "states": [parsed["state"]],
            "products": []  # To be filled based on document content
        },
        "expected_key_fields": {
            "registration_numbers": [],  # To be extracted from document
            "dates": [creation_date.strftime("%Y-%m-%d")],
            "amounts": []  # To be extracted from document
        },
        "expected_flags": []
    }
    
    return metadata

def update_test_documents(documents_dir: Path, labeled_dir: Path):
    """
    Update test document organization and metadata.
    
    Args:
        documents_dir: Source directory containing test documents
        labeled_dir: Target directory for labeled documents
    """
    # Ensure labeled documents directory structure exists
    for doc_type in ["approvals", "denials", "requests", "renewals", "tonnage"]:
        (labeled_dir / doc_type).mkdir(parents=True, exist_ok=True)
    
    # Load existing metadata if any
    metadata_file = labeled_dir / "metadata.json"
    if metadata_file.exists():
        with open(metadata_file) as f:
            metadata = json.load(f)
    else:
        metadata = {}
    
    # Process all PDF files in the source directory
    for pdf_file in documents_dir.rglob("*.pdf"):
        # Skip files that are in nested target directories
        if str(labeled_dir) in str(pdf_file):
            print(f"Skipping file in nested target directory: {pdf_file}")
            continue
            
        try:
            # Generate unique filename with date prefix
            creation_date = datetime.fromtimestamp(pdf_file.stat().st_ctime)
            date_prefix = creation_date.strftime("%Y%m%d")
            parsed = parse_document_filename(pdf_file.name)
            
            new_filename = f"{date_prefix}-{pdf_file.name}"
            doc_type_dir = {
                "NEW": "requests",
                "RENEW": "renewals",
                "CERT": "approvals",
                "TONNAGE": "tonnage"
            }.get(parsed["base_type"], "requests")
            
            # Copy file to appropriate directory
            target_path = labeled_dir / doc_type_dir / new_filename
            shutil.copy2(pdf_file, target_path)
            
            # Generate and store metadata
            metadata[new_filename] = generate_document_metadata(
                new_filename, 
                target_path,
                creation_date
            )
            
        except Exception as e:
            print(f"Error processing {pdf_file}: {e}")
            continue
    
    # Save updated metadata
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2) 