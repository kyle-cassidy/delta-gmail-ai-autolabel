# Document Labeling System

A tool for managing and labeling test documents for the classification system.

## Directory Structure

```
tests/fixtures/documents/
├── _to_label/              # Place new documents here for labeling
└── labeled_documents/
    ├── documents/         # Contains labeled documents
    ├── metadata.json      # Stores document metadata
    └── README.md         # This file
```

## Installation

1. Install the package in development mode:
```bash
pip install -e .
```

## Usage

### Basic Commands

1. Label a specific document:
```bash
python src/cli/document_labeler.py label /path/to/your/document.pdf
```

2. Process all documents in _to_label directory:
```bash
python src/cli/document_labeler.py label
```

3. View labeled documents:
```bash
python src/cli/document_labeler.py list
```

4. Check labeling status:
```bash
python src/cli/document_labeler.py status
```

### Workflow

1. **Single Document Labeling**:
   - Run `python src/cli/document_labeler.py label /path/to/document.pdf`
   - Follow prompts to add metadata
   - Document will be copied to labeled directory with standardized name

2. **Batch Labeling**:
   - Copy documents to `_to_label/` directory
   - Run `python src/cli/document_labeler.py label`
   - Documents will be moved to `labeled_documents/documents/` after processing

3. **Verification**:
   - Use `list` command to verify labeled documents
   - Use `status` command to check remaining work

## Document Schema

Each document follows the naming convention:
```
{STATE}-{CLIENT}-{BASE_TYPE}[-description].pdf
```

Example: `ME-EEA-RENEW-initial-submission.pdf`

### Valid Values

#### States
- ME (Maine)
- CA (California)
- EP (EPA)
- US (USDA)
- IL (Illinois)
- AL (Alabama)

#### Base Types
- NEW: New product registration
- RENEW: Renewal application
- TONNAGE: Tonnage reporting
- CERT: Registration certificate
- LABEL: Product label

## Metadata Schema

Each document entry in metadata.json follows this structure:
```json
{
    "state": "ME",
    "client_code": "EEA",
    "base_type": "RENEW",
    "description": "initial-submission",
    "product_categories": ["Commercial Fertilizers"],
    "expected_filename": "ME-EEA-RENEW-initial-submission.pdf",
    "last_updated": "2024-03-20T10:30:00Z"
}
```

## Best Practices

1. Keep test documents small but representative
2. Include edge cases and boundary conditions
3. Use consistent naming for similar documents
4. Update metadata.json whenever adding new test documents
5. Verify that expected values match actual document content 