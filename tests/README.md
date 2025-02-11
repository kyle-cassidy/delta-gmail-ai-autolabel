# Document Classification Test Suite

This directory contains the test suite for the document classification system. The tests are organized into unit tests and integration tests to ensure both individual components and the system as a whole work correctly.

## Directory Structure

```
tests/
├── unit/                 # Unit tests for individual components
│   ├── test_base_classifier.py
│   ├── test_domain_config.py
│   ├── test_classifier_factory.py
│   ├── test_gemini_classifier.py
│   └── test_docling_classifier.py
├── integration/          # Integration tests for end-to-end functionality
│   └── test_classifier_integration.py
├── fixtures/            # Test data and fixtures
│   └── documents/       # Test PDF documents
└── conftest.py         # Shared test configuration and fixtures
```

## Test Data

To run the integration tests, you need to add test PDF documents to the `fixtures/documents/` directory. These documents should represent various types of regulatory documents that the system needs to classify.

Example document types:
- Registration applications
- Renewal forms
- Amendments
- Tonnage reports

## Running Tests

### Prerequisites

1. Install test dependencies:
```bash
pip install -r requirements/requirements-dev.txt
```

2. Set up environment variables:
```bash
export GOOGLE_API_KEY=your_api_key  # Required for Gemini classifier tests
```

### Running All Tests

```bash
pytest tests/
```

### Running Specific Test Categories

Run unit tests only:
```bash
pytest tests/unit/
```

Run integration tests only:
```bash
pytest tests/integration/
```

Run tests for a specific classifier:
```bash
pytest tests/unit/test_gemini_classifier.py
pytest tests/unit/test_docling_classifier.py
```

### Test Configuration

The test suite uses a temporary configuration directory with test-specific domain rules and patterns. You can modify these configurations in `conftest.py` if needed.

## Adding New Tests

When adding new test cases:

1. Unit tests:
   - Add test files to the `unit/` directory
   - Focus on testing individual components in isolation
   - Use mocking for external dependencies

2. Integration tests:
   - Add test files to the `integration/` directory
   - Test end-to-end workflows
   - Use real PDF documents from the fixtures directory

3. Test data:
   - Add test documents to `fixtures/documents/`
   - Include a variety of document types
   - Document the expected classification results

## Test Coverage

To generate a test coverage report:

```bash
pytest --cov=src tests/
```

## Continuous Integration

The test suite is integrated with our CI/CD pipeline. The following checks are performed:

1. All unit tests must pass
2. Integration tests must pass when API keys are available
3. Code coverage must meet minimum thresholds
4. Code style must follow project guidelines

## Contributing

When contributing new features or bug fixes:

1. Add appropriate test cases
2. Ensure all tests pass locally
3. Maintain or improve code coverage
4. Follow existing test patterns and naming conventions 