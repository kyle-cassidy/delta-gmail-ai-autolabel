# Document Classification API

This API service provides document classification capabilities using Google's Gemini Flash model. It can process regulatory documents (PDFs, images) and extract structured information about their content, type, and entities.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
Create a `.env` file with:
```
GOOGLE_API_KEY=your_gemini_api_key_here
```

3. Run the service:
```bash
python -m src.api.main
```

The service will start on `http://localhost:8000`

## API Endpoints

### 1. Classify Single Document
**POST** `/classify/`

Upload a single document for classification.

```bash
curl -X POST "http://localhost:8000/classify/" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_document.pdf"
```

### 2. Batch Classification
**POST** `/classify/batch/`

Upload multiple documents for classification.

```bash
curl -X POST "http://localhost:8000/classify/batch/" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@document1.pdf" \
  -F "files=@document2.pdf"
```

### 3. Health Check
**GET** `/health/`

Check if the service is running.

```bash
curl "http://localhost:8000/health/"
```

## Response Format

The API returns JSON responses in the following format:

```json
{
    "file_path": "path/to/document",
    "success": true,
    "classification": {
        "document_type": "registration",
        "confidence": 0.85,
        "entities": {
            "companies": ["Company A", "Company B"],
            "products": ["Product X"],
            "states": ["CA", "NY"]
        },
        "key_fields": {
            "dates": ["2024-02-11"],
            "registration_numbers": ["REG123"],
            "amounts": ["$500"]
        },
        "metadata": {
            "has_tables": true,
            "entity_count": 4,
            "field_count": 3
        },
        "summary": "Document summary...",
        "flags": []
    }
}
```

## Error Handling

Errors are returned with appropriate HTTP status codes and messages:

```json
{
    "detail": "Error message describing what went wrong"
}
```

## Development

The API is built with:
- FastAPI for the web framework
- Google Gemini Flash for document processing
- Async processing for better performance
- Temporary file handling for uploads

## Security Notes

For production deployment:
1. Configure CORS appropriately in `main.py`
2. Use secure environment variable handling
3. Implement authentication/authorization
4. Add rate limiting
5. Configure proper logging 