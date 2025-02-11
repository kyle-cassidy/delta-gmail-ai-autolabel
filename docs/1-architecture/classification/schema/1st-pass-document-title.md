# Document Classification Schema - First Pass

## Overview
Initial classification schema for regulatory documents in Delta's document processing pipeline. This specification defines the top-level classification structure, supporting future expansion for state-specific document handling.

## Filename/classification Schema
```
{YEAR}-{TERM}-{STATE}-{CLIENT}-{BASE_TYPE}[-description]
```

### Field Definitions

#### YEAR (Required)
- 4-digit year
- For renewals/tonnage: Year of requirement/expiration
- For new registrations: Target submission year
- Examples: "2024", "2025"

#### TERM (Required)
- need to decide on Month or Quarter
- Q1-Q4 for quarters (e.g., "Q1")
- M01-M12 for months (e.g., "M03")
- For renewals: Due date term
- For new registrations: Target submission term

#### STATE (Required)
- 2-letter state code
- Special cases for federal agencies use 2 letters
- Examples: "ME", "CA", "EP" (EPA), "US" (USDA)

#### CLIENT (Required)
- 3-letter client identifier
- Must match Delta's client code system
- Examples: "EEA" (Elemental Enzymes), "BOR" (US Borax)

#### BASE_TYPE (Required)
One of five core categories:
- NEW: New product registration application
- RENEW: Renewal application
- TONNAGE: Tonnage reporting
- CERT: Registration certificate/approval
- LABEL: Product label

#### Description (Optional)
- Short descriptive text
- Use hyphens for spaces
- Keep concise and relevant
- Examples: "initial-submission", "revised", "approved"

## Example Filenames
```
2025-Q1-ME-EEA-RENEW-initial-submission     # Maine Q1 renewal application for Elemental Enzymes
2024-M07-IL-BOR-TONNAGE                     # Illinois July tonnage report for US Borax
2025-Q2-CA-EEA-NEW-name-of-fertilizer              # California new product registration for Elemental Enzymes
2024-M03-ME-EEA-CERT-approved              # Maine registration certificate for Elemental Enzymes
```

## Metadata Schema
```json
{
    "filename": "2025-Q1-ME-EEA-RENEW-initial-submission",
    "classification": {
        "year": 2025,
        "term": "Q1",
        "state": "ME",
        "client": "EEA",
        "base_type": "RENEW",
        "description": "initial-submission"
    },
    "state_specific": {
        "form_type": "Feed, Seed & Fertilizer Registration",
        "product_categories": [
            "Plant and Soil Amendments",
            "Commercial Fertilizers"
        ],
        "fee_structure": [
            "$25/product",
            "$125/product"
        ]
    },
    "products": [
        {
            "name": "RES+ 5-0-0",
            "category": "Commercial Fertilizer",
            "state_classification": "Commercial Fertilizers/Materials Registration"
        }
    ],
    "routing": {
        "parser": "maine_registration_parser",
        "storage_paths": [
            "gs://regulatory-docs/renewals/2025/ME/",
            "gdrive://regulatory/active/renewals"
        ],
        "databases": [
            "airtable://registration_tracking"
        ]
    },
    "timestamps": {
        "received": "2024-12-18T10:30:00Z",
        "classified": "2024-12-18T10:30:05Z",
        "processed": "2024-12-18T10:31:00Z"
    }
}
```

## Implementation Notes

### Document Processor Requirements
1. Must extract year and term from document context if not explicitly stated
2. Must validate state code against approved list
3. Must validate client code against Delta's client database
4. Must identify base type from document content and structure
5. Must generate valid metadata structure
6. Must implement error handling for unclassifiable documents
7. Must preserve and normalize optional description if present

### Error Handling
- Documents that cannot be classified should be:
  1. Flagged for manual review
  2. Tagged with attempted classifications
  3. Stored in a separate review queue
  4. Generate notification to appropriate team

### Routing Rules
Base routing determined by BASE_TYPE:
```python
ROUTING_RULES = {
    'NEW': {
        'parsers': ['registration_form_parser'],
        'storage': ['gs://regulatory-docs/registrations/{year}/{state}'],
        'databases': ['airtable://registration_tracking']
    },
    'RENEW': {
        'parsers': ['renewal_form_parser'],
        'storage': ['gs://regulatory-docs/renewals/{year}/{state}'],
        'databases': ['airtable://registration_tracking']
    },
    'TONNAGE': {
        'parsers': ['tonnage_form_parser'],
        'storage': ['gs://regulatory-docs/tonnage/{year}/{state}'],
        'databases': ['airtable://tonnage_tracking']
    },
    'CERT': {
        'parsers': ['certificate_parser'],
        'storage': ['gs://regulatory-docs/certificates/{year}/{state}'],
        'databases': ['airtable://registration_tracking']
    },
    'LABEL': {
        'parsers': ['label_parser'],
        'storage': ['gs://regulatory-docs/labels/{year}/{state}'],
        'databases': ['airtable://label_tracking']
    }
}
```
