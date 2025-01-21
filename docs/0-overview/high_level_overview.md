
# System Architecture Overview

## Purpose
Delta Gmail AI Autolabel is an intelligent email management system that automatically categorizes and labels Gmail messages using AI.

## Core Components
1. Gmail Integration Service
   - Handles OAuth authentication
   - Manages email fetching and labeling
   - Real-time email monitoring

2. AI Classification Engine
   - Email content analysis
   - Pattern recognition
   - Label prediction

3. Security Layer
   - OAuth token management
   - Data encryption
   - Access control

4. API Layer
   - RESTful endpoints
   - Rate limiting
   - Error handling

## Data Flow
1. Email Reception → Gmail Webhook
2. Content Processing → AI Analysis
3. Label Application → Gmail/Gmelius API
4. Is Registration/Certificate Identification → Update Airtable Registration Tracking via API
5. Feedback Loop → Model Improvement

## Technology Stack
- Python 3.11+
- Gmail API
- OpenAI API
- FastAPI
- PostgreSQL

## Integration Points
- Gmail API
- Gmelius API
- Google Drive API
- Airtable API
- PDF Parsing (Docling, etc.)
- LLM Providers
- Authentication services 