# System Architecture and Component Integration

## System Overview

### Core Architecture

#### Service Layer
```mermaid
graph LR
    EPS[Email Processing Service] --> |Content| CES[Content Extraction]
    EPS --> |Security| SS[Security Service]
    CES --> |Classification| CS[Classification Service]
    CS --> |Storage| StS[Storage Service]
    StS --> |Audit| AS[Audit Service]
    CS --> |Notifications| NS[Notification Service]
    CS --> |Validation| VS[Validation Service]
```

#### Client Layer
```mermaid
graph LR
    GC[Gmail Client] --> |Messages| MC[Message Client]
    MC --> |Attachments| AC[Attachment Client]
    GC --> |Organization| LC[Label Client]
    GC --> |Search| QC[Query Client]
```

#### System Integration
```mermaid
graph TB
    Gmail[Gmail API] --> |Fetch Emails| Client[Client Layer]
    Client --> |Process Messages| Services[Service Layer]
    Services --> |Store Documents| Storage[Storage Layer]
    Services --> |Update Records| Airtable[Airtable Integration]
```

## Core Services

### 1. Email Processing Service
```mermaid
graph TB
    Email[Email Input] --> Validate[Input Validation]
    Validate --> Queue[Processing Queue]
    Queue --> Process[Process Email]
    Process --> Extract[Extract Content]
    Process --> Retry[Retry Mechanism]
    Extract --> Coordinate[Service Coordination]
    
    subgraph Error Handling
        Retry --> MaxRetries[Max Retries]
        MaxRetries --> Alert[Alert System]
    end
```

- Orchestrates the email processing pipeline
- Coordinates between different services
- Handles error recovery and retries
- Manages processing queues
  
#### Email Processing Pipeline
```mermaid
sequenceDiagram
    participant Gmail
    participant EP as Email Processor
    participant CE as Content Extractor
    participant CL as Classifier
    participant ST as Storage
    participant AU as Audit

    Gmail->>EP: New Email
    EP->>CE: Extract Content
    CE->>CL: Classify Content
    CL->>ST: Store Documents
    ST->>AU: Log Operations
```

### 2. Content Extraction Service
```mermaid
graph LR
    Input[Raw Content] --> Parser[Content Parser]
    Parser --> Text[Text Extraction]
    Parser --> Meta[Metadata Extraction]
    Text --> PDF[PDF Processing]
    Text --> Doc[Document Processing]
    Meta --> Structure[Structure Analysis]
```

- Parses email content and attachments
- Extracts text from PDFs and documents
- Identifies document structure and metadata
- Handles multiple document formats

### 3. Classification Service
```mermaid
graph TB
    Input[Document] --> Rules[Rule Engine]
    Rules --> Patterns[Pattern Matching]
    Patterns --> ML[ML Classification]
    ML --> Confidence[Confidence Score]
    Confidence --> Decision[Decision Engine]
    
    subgraph Classification Rules
        Types[Document Types]
        Patterns[Pattern Library]
        History[Historical Data]
    end
```

- Determines document types
- Applies classification rules
- Maintains classification patterns
- Machine learning integration

### 4. Storage Service
```mermaid
graph LR
    Input[Document] --> Version[Version Control]
    Version --> Meta[Metadata Store]
    Version --> Files[File Storage]
    Meta --> Index[Search Index]
    Files --> Hierarchy[Document Hierarchy]
    
    subgraph Management
        Access[Access Control]
        Audit[Audit Logs]
        Backup[Backup System]
    end
```

- Manages document hierarchy
- Handles file organization
- Maintains document relationships
- Version control and metadata



## Implementation Details

### Client Layer (`src/client/`)
The client layer manages external service interactions:

```python
src/client/
├── gmail.py         # Gmail API interaction
├── message.py       # Email message handling
├── attachment.py    # Attachment processing
├── label.py        # Gmail label management
└── query.py        # Search functionality
```

## Document Processing Flow
```mermaid
graph TB
    Input[Incoming Document] --> |Extract| Extract[Content Extraction]
    Extract --> |Classify| Class[Classification]
    Class --> |Validate| Val[Validation]
    Val --> |Store| Store[Storage]
    Store --> |Notify| Notify[Notification]
    
    subgraph Document Types
        Labels[Labels]
        SDS[Safety Data Sheets]
        COA[Certificates of Analysis]
        Test[Test Reports]
        Studies[Efficacy Studies]
    end
```

## Integration Points
```mermaid
graph TB
    System[System] --> Gmail[Gmail API]
    System --> Drive[Google Drive]
    System --> Airtable[Airtable]
    
    subgraph Internal Services
        Process[Processing Service]
        Store[Storage Service]
        Notify[Notification Service]
    end
```

## Success Metrics
Tracked through Audit Service:
1. Processing success rates
2. Classification accuracy
3. Response times
4. Error rates
5. Storage utilization

## Future Roadmap
1. Machine learning enhancements
2. Document relationship tracking
3. Automated workflow triggers
4. Advanced search capabilities
5. Real-time processing optimization

[View Implementation Details](../specifications/implementation_details.md)
[View Data Flow Specifications](../specifications/data_flows.md) 