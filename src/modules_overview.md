# Project Structure and Module Overview

## Core Components

### src/
- **api/** - FastAPI endpoints and request/response schemas
- **client/** - External service integrations (Gmail, Airtable)
- **models/** - Domain models and data structures
- **parsers/** - Specialized document parsing (PDF, Excel, etc.)
- **services/** - Business logic and orchestration
- **utils/** - Shared utilities and helpers
- **logging/** - Logging configuration
- **console.py** - CLI interface
- **main.py** - Application entry point

### Supporting Directories
- **config/** - Configuration management
- **data/clients/** - Client-specific data and mappings
- **docs/** - API and user documentation
- **requirements/** - Environment-specific dependencies
- **secrets/** - Secure credentials (not in VCS)
- **tests/** - Test suite organized by module

## Key Features

### Email Processing Pipeline
1. Email retrieval via client/gmail_client.py
2. Security vetting in services/security_service.py
3. Content extraction through parsers/
4. Classification in services/classification_service.py
5. Data integration via client/airtable_client.py

### Deployment Configuration
- Docker containerization
- Cloud-native design (AWS/GCP/Azure compatible)
- Environment-based configuration
- Structured logging and monitoring

### Security & Scalability
- Secure credential management
- Rate limiting and retry mechanisms
- Async processing where applicable
- Modular design for easy scaling

### Development Workflow
- Make commands for common operations
- Comprehensive test coverage
- API documentation generation
- Development/production parity
