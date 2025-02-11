# Required Classification Mapping Dictionaries
#area/delta-ac
## 1. State Mappings

### State Agency Domain Patterns
```python
STATE_AGENCY_DOMAINS = {
    'ME': {
        'domains': ['maine.gov'],
        'department_names': ['Department of Agriculture, Conservation & Forestry',
                           'Division of Quality Assurance and Regulations'],
        'abbreviations': ['ME', 'Maine']
    },
    'CA': {
        'domains': ['cdfa.ca.gov', 'ca.gov'],
        'department_names': ['California Department of Agriculture'],
        'abbreviations': ['CA', 'Calif', 'California']
    },
    # Add other states...
}
```

### State-Specific Form Types
```python
STATE_FORM_TYPES = {
    'ME': {
        'registration': [
            'Feed, Seed & Fertilizer Registration',
            'Plant & Soil Amendments Registration'
        ],
        'product_categories': [
            'Commercial Fertilizers',
            'Plant and Soil Amendments',
            'Liming Materials'
        ],
        'fee_structure': {
            'Commercial Fertilizers': 125.00,
            'Plant and Soil Amendments': 25.00,
            'Liming Materials': 75.00
        }
    }
    # Add other states...
}
```

### State Registration Number Patterns
```python
REGISTRATION_NUMBER_PATTERNS = {
    'ME': r'^\d{4}$',  # Example: 2919
    'CA': r'^\d{4}-\d{4}$',  # Example: XXXX-XXXX
    'NY': r'^NY-\d{6}$',  # Example: NY-XXXXXX
    # Add other states...
}
```

## 2. Client Mappings

### Client Code Lookup
```python
CLIENT_CODES = {
    'EEA': {
        'name': 'Elemental Enzymes Ag & Turf LLC',
        'variants': [
            'Elemental Enzymes',
            'Elemental Enzymes Ag',
            'Elemental Enzymes Ag & Turf'
        ],
        'usa_plants_id': None,  # Fill in actual value
        'epa_number': None,     # Fill in actual value
        'address': {
            'street': '12510 Prosperity Dr Suite 160',
            'city': 'Silver Spring',
            'state': 'MD',
            'zip': '20904'
        }
    },
    'BOR': {
        'name': 'US Borax Inc',
        'variants': [
            'U.S. BORAX INC',
            'US BORAX INC',
            'U.S. Borax'
        ],
        'usa_plants_id': '000GQ8',
        'epa_number': None,  # Fill in actual value
        'address': {
            'street': '12510 Prosperity Dr Ste 160', 
            'city': 'Silver Springs',
            'state': 'MD',
            'zip': '20904'
        }
    }
    # Add other clients...
}
```

### Product Category Mappings
```python
PRODUCT_CATEGORIES = {
    'fertilizer': {
        'keywords': ['NPK', 'fertilizer', 'nutrient', 'plant food'],
        'state_classifications': {
            'ME': 'Commercial Fertilizers/Materials Registration',
            'CA': 'Conventional Fertilizer'
            # Add other states...
        }
    },
    'soil_amendment': {
        'keywords': ['soil amendment', 'soil conditioner', 'growing media'],
        'state_classifications': {
            'ME': 'Plant and Soil Amendments Registration',
            'CA': 'Specialty Fertilizer'
            # Add other states...
        }
    },
    'biological': {
        'keywords': ['inoculant', 'microbial', 'bacteria', 'fungi'],
        'state_classifications': {
            'ME': 'Plant and Soil Amendments Registration',
            # Add other states...
        }
    }
}
```

## 3. Document Type Patterns

### Document Classification Patterns
```python
DOCUMENT_TYPE_PATTERNS = {
    'NEW': {
        'keywords': [
            'new registration',
            'initial registration',
            'product registration application'
        ],
        'form_titles': [
            'Feed, Seed & Fertilizer Registration Application',
            'Product Registration Form'
        ]
    },
    'RENEW': {
        'keywords': [
            'renewal',
            'annual registration',
            'registration renewal'
        ],
        'form_titles': [
            'License Renewal Form',
            'Annual Registration Renewal'
        ]
    },
    'TONNAGE': {
        'keywords': [
            'tonnage report',
            'quarterly report',
            'semi-annual report'
        ],
        'form_titles': [
            'SEMI-ANNUAL FERTILIZER/SOIL AMENDMENT TONNAGE REPORT',
            'Quarterly Tonnage Report'
        ]
    },
    'CERT': {
        'keywords': [
            'certificate',
            'registration approved',
            'license issued'
        ]
    },
    'LABEL': {
        'keywords': [
            'product label',
            'approved label',
            'label amendment'
        ]
    }
}
```

### Status Pattern Recognition
```python
STATUS_PATTERNS = {
    'approved': {
        'keywords': [
            'registration.*approved',
            'approval.*granted',
            'license.*issued'
        ],
        'airtable_status': 'Approved'
    },
    'pending': {
        'keywords': [
            'additional.*required',
            'in.*review',
            'pending.*information'
        ],
        'airtable_status': 'Pending'
    },
    'pending_response': {
        'keywords': [
            'awaiting.*response',
            'response.*required',
            'additional.*information.*needed'
        ],
        'airtable_status': 'Pending - Response'
    }
}
```

## 4. Date Pattern Recognition

### Date Extraction Patterns
```python
DATE_PATTERNS = {
    'due_date': [
        r'due by (?P<date>\w+ \d{1,2}, \d{4})',
        r'deadline[:]? (?P<date>\d{2}/\d{2}/\d{4})',
        r'submit before (?P<date>\w+ \d{1,2})'
    ],
    'effective_date': [
        r'effective (?P<date>\w+ \d{1,2}, \d{4})',
        r'valid from (?P<date>\d{2}/\d{2}/\d{4})'
    ],
    'expiration_date': [
        r'expires on (?P<date>\w+ \d{1,2}, \d{4})',
        r'valid until (?P<date>\d{2}/\d{2}/\d{4})'
    ]
}
```

## 5. Fee Recognition

### Fee Pattern Recognition
```python
FEE_PATTERNS = {
    'registration_fee': [
        r'\$(\d+(?:\.\d{2})?)\s*(?:per|\/)\s*product',
        r'registration fee[:]\s*\$(\d+(?:\.\d{2})?)'
    ],
    'tonnage_fee': [
        r'\$(\d+(?:\.\d{2})?)\s*(?:per|\/)\s*ton',
        r'tonnage fee[:]\s*\$(\d+(?:\.\d{2})?)'
    ]
}
```

## Implementation Notes

1. These mappings should be maintained in a central configuration system
2. Regular expressions should be compiled at load time for performance
3. State-specific patterns should be loaded dynamically based on active states
4. All pattern matches should include confidence scoring
5. Consider implementing fuzzy matching for company names and products
6. Maintain audit trail of pattern matches for troubleshooting
7. Regular validation and updates of patterns based on match success rates