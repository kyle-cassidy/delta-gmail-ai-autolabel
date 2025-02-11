```
src
├── __init__.py
├── api
├── auto_labeler.py
├── classifiers/
│   ├── __init__.py
│   ├── base.py
│   ├── pattern.py
│   ├── ml.py
│   └── combined.py
├── client/
│   ├── __init__.py 
│   ├── attachment.py
│   ├── gmail.py
│   ├── gmail_client_README.md
│   ├── label.py
│   ├── message.py
│   └── query.py
├── config/
│   ├── __init__.py
│   └── patterns/
│       ├── __init__.py 
│       ├── states.py
│       ├── documents.py
│       ├── clients.py
│       └── dates.py
├── console.py
├── logging/
│   └── logger.py
├── main.py
├── models/
│   ├── __init__.py
│   ├── paligemma/
│   └── classification/
│       ├── __init__.py
│       ├── document.py
│       ├── classification.py
│       └── enums.py
├── parsers/
│   ├── __init__.py
│   ├── base.py
│   ├── state/
│   │   ├── __init__.py
│   │   ├── maine.py
│   │   └── california.py
│   └── document_types/
│       ├── __init__.py
│       ├── registration.py
│       ├── renewal.py
│       └── tonnage.py
├── services/
│   ├── __init__.py
│   ├── attachment_service.py
│   ├── audit_service.py
│   ├── classification_service.py
│   ├── content_extraction_service.py
│   ├── email_processing_service.py
│   ├── notification_service.py
│   ├── security_service.py
│   ├── storage_service.py
│   └── validation_service.py
└── utils/
    ├── __init__.py
    ├── data_extractor.py
    ├── email_labeler.py
    ├── email_sampler.py
    └── main.py
```

Changes:
- Added `classifiers/` for classification components
- Added `config/patterns/` for pattern definitions
- Added `models/classification/` for classification models 
- Enhanced `parsers/` with state and document type specific parsers
- Removed `__pycache__` directories from view
- Removed markdown files for clarity