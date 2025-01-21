# Email Classification Strategies

## 1. Sender-Based Classification

### State Recognition
- **Domain Matching**: Map state agency domains from our States schema
  ```python
  STATE_DOMAINS = {
      'cdfa.ca.gov': {'state': 'California', 'department': 'Agriculture'},
      'ny.gov': {'state': 'New York'},
      'state.tx.us': {'state': 'Texas'}
  }
  ```

### Department Recognition
- **Email Pattern Analysis**: Identify department/division from email addresses
  ```
  registration@
  fertilizer@
  permits@
  licensing@
  ```

## 2. Subject Line Analysis

### Pattern Matching
- **Registration Status Keywords**:
  ```python
  STATUS_PATTERNS = {
      'approval': [
          r'registration.*approved',
          r'approval.*granted',
          r'license.*issued'
      ],
      'pending': [
          r'additional.*required',
          r'in.*review',
          r'pending.*information'
      ],
      'rejection': [
          r'cannot.*approve',
          r'denied',
          r'rejection'
      ]
  }
  ```

### Registration Number Detection
- **State-Specific Formats**:
  ```python
  REG_NUMBER_PATTERNS = {
      'CA': r'(\d{4}-\d{4})',
      'NY': r'(NY-\d{6})',
      'TX': r'(TXF-\d{5})'
  }
  ```

## 3. Content-Based Classification

### Document Type Detection
- **Form Type Identification**:
  ```python
  DOCUMENT_TYPES = {
      'registration': [
          'product registration',
          'registration certificate',
          'license document'
      ],
      'renewal': [
          'renewal notice',
          'renewal application',
          'annual registration'
      ],
      'tonnage': [
          'tonnage report',
          'quarterly report',
          'sales report'
      ]
  }
  ```

### Response Type Analysis
Map to Airtable "Initial Registration Status" field:
```python
RESPONSE_TYPES = {
    'Approved': {
        'patterns': [
            'has been approved',
            'registration granted',
            'successfully registered'
        ],
        'requires': ['registration_number', 'effective_date']
    },
    'Pending': {
        'patterns': [
            'under review',
            'additional information needed',
            'please provide'
        ],
        'requires': ['due_date', 'requirements']
    }
}
```

## 4. Product-Based Classification

### Product Type Recognition
Based on Airtable schema:
```python
PRODUCT_TYPES = {
    'Fertilizer': [
        'npk', 'fertilizer', 'nutrient', 'plant food'
    ],
    'Soil Amendment': [
        'soil amendment', 'soil conditioner', 'growing media'
    ],
    'Biological': [
        'inoculant', 'microbial', 'bacteria', 'fungi'
    ]
}
```

### Requirement Matching
```python
PRODUCT_REQUIREMENTS = {
    'Fertilizer': [
        'guaranteed analysis',
        'heavy metals',
        'nutrient content'
    ],
    'Biological': [
        'viable cell count',
        'species identification',
        'efficacy data'
    ]
}
```

## 5. Date and Timeline Detection

### Due Date Recognition
- Look for common date patterns with context
  ```python
  DUE_DATE_PATTERNS = [
      r'due by (\w+ \d{1,2}, \d{4})',
      r'deadline[:]? (\d{2}/\d{2}/\d{4})',
      r'submit before (\w+ \d{1,2})'
  ]
  ```

### Timeline Classification
```python
TIMELINE_TYPES = {
    'Urgent': {
        'max_days': 5,
        'patterns': ['immediate attention', 'urgent', 'asap']
    },
    'Standard': {
        'max_days': 30,
        'patterns': ['within 30 days', 'monthly', 'standard processing']
    },
    'Extended': {
        'max_days': 90,
        'patterns': ['quarterly', '90 day', 'extended review']
    }
}
```

## 6. Confidence Scoring

### Score Components
```python
CONFIDENCE_FACTORS = {
    'sender_match': 0.3,      # Recognized state email domain
    'subject_match': 0.2,     # Clear subject line patterns
    'content_match': 0.3,     # Body content patterns
    'data_presence': 0.2      # Required data fields found
}
```

### Threshold Levels
```python
CONFIDENCE_THRESHOLDS = {
    'auto_tag': 0.9,         # Apply tags automatically
    'review_queue': 0.7,     # Queue for human review
    'uncertain': 0.5         # Mark as needs investigation
}
```

## 7. Implementation Approach

### Progressive Classification
1. Start with sender classification (highest confidence)
2. Apply subject line analysis
3. Deep content analysis if needed
4. Cross-reference results

### Weighted Decision Making
```python
def calculate_confidence(matches):
    score = 0
    for match in matches:
        score += match.weight * match.confidence
        if match.required and match.confidence < 0.5:
            return 0  # Required match failed
    return score / sum(match.weight for match in matches)
```

### Rule Chaining
```python
def classify_email(email):
    state = classify_state(email.sender)
    if not state:
        return low_confidence_result()
    
    rules = get_state_rules(state)
    doc_type = classify_document(email, rules)
    response = classify_response(email, doc_type)
    
    return combine_classifications(state, doc_type, response)
```

## 8. Validation and Learning

### Success Metrics
- Track classification accuracy by:
  - State
  - Document type
  - Response type
  - Product category

### Feedback Loop
- Log manual corrections
- Update pattern weights
- Identify new patterns
- Track false positives/negatives

### Continuous Improvement
- Regular pattern analysis
- State-specific rule refinement
- Confidence threshold adjustment
- New pattern discovery