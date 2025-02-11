# Delta Gmail AI Autolabel - Core Architecture

## Message Queue System
RabbitMQ serves as our central nervous system, coordinating all email processing activities. Like a post office, it accepts incoming email events and ensures reliable delivery to the appropriate processing services. This decoupling allows for scalable, fault-tolerant operations.

## Core Services

### 1. Email Gateway
Acts as the primary entry point for all email traffic. Similar to a building's security desk, it authenticates, logs, and routes all incoming messages while maintaining security protocols and rate limits.

### 2. Classification Engine
Functions like a sophisticated mail sorting facility, using both rule-based and AI-powered systems to categorize content. It maintains a learning feedback loop to improve accuracy over time, similar to how a skilled worker becomes more efficient with experience.

### 3. Document Processor
Operates like a document translation service, converting various formats (PDF, Excel, images) into standardized, searchable content. It maintains the original document's integrity while extracting useful information.

### 4. Storage Orchestrator
Functions as a smart filing system, managing document hierarchies and relationships. Like a library's catalog system, it maintains precise organization while enabling quick retrieval.

## Data Architecture

### 1. Event Stream
The system's lifeblood, carrying messages between services in a standardized format:
```mermaid
graph LR
    Email --> Queue
    Queue --> Processor
    Processor --> Storage
    Storage --> Search
```

### 2. Data Models
- **Documents**: Core content containers
- **Classifications**: Content categorization metadata
- **Relationships**: Inter-document connections
- **Audit Trail**: Complete history tracking

### 3. Search Index
Functions like a library's card catalog system, providing rapid access to content through multiple dimensions: client, state, product, and document type.

## Integration Layer

### 1. External Services
- **Gmail API**: Primary email source
- **Airtable**: Registration tracking
- **Google Cloud**: AI model hosting
- **Document Storage**: Secure file management

### 2. Internal Services
- **Authentication**: Identity management
- **Audit**: Activity tracking
- **Metrics**: System health monitoring
- **Cache**: Performance optimization

## Security Architecture

### 1. Perimeter Security
Like a secure facility's checkpoints, controlling access through multiple authentication layers and monitoring for suspicious activities.

### 2. Data Protection
Implements encryption both in transit and at rest, similar to how valuable documents are protected during transport and storage.

### 3. Access Control
Manages permissions like a building's access card system, ensuring users can only access appropriate resources.

## Observability Stack

### 1. Monitoring
Acts as the system's health dashboard, providing real-time visibility into service performance and processing status.

### 2. Logging
Maintains a detailed system journal, tracking all significant events for troubleshooting and audit purposes.

### 3. Metrics
Measures system vital signs, tracking performance, accuracy, and resource utilization.

---


