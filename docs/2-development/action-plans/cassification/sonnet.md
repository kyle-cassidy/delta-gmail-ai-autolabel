I'll help design a complete classification microservice with hot-swappable models. Let's break this down into key components.

## 1. Core Architecture

First, let's look at the existing classification data models from:

```13:30:docs/1-architecture/classification/example/classification-microservice.md
# Core Data Models
class BaseType(str, Enum):
    NEW = "NEW"
    RENEW = "RENEW" 
    TONNAGE = "TONNAGE"
    CERT = "CERT"
    LABEL = "LABEL"

@dataclass
class Classification:
    year: int
    term: str
    state: str  
    client: str
    base_type: BaseType
    description: Optional[str] = None
    confidence: float = 0.0

```


Building on these, here's our enhanced microservice design:

```python
from typing import Protocol, Dict, List, Optional, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass
import asyncio
from enum import Enum

# Model Protocol Definition
class ClassificationModel(Protocol):
    async def predict(self, content: str) -> Dict[str, float]:
        """Returns confidence scores for each classification"""
        ...

    @property
    def model_info(self) -> Dict[str, Any]:
        """Returns model metadata"""
        ...

# Base Classifier Interface
class BaseClassifier(ABC):
    @abstractmethod
    async def classify(self, document: Document) -> Classification:
        """Classify a document"""
        pass
    
    @abstractmethod
    def get_confidence(self) -> float:
        """Get classification confidence score"""
        pass

# Classification Service
class ClassificationService:
    def __init__(self):
        self._classifiers: List[BaseClassifier] = []
        self._active_model: Optional[ClassificationModel] = None
        self._fallback_model: Optional[ClassificationModel] = None
    
    def add_classifier(self, classifier: BaseClassifier) -> None:
        self._classifiers.append(classifier)
    
    def set_active_model(self, model: ClassificationModel) -> None:
        """Hot-swap the active model"""
        self._fallback_model = self._active_model
        self._active_model = model
    
    async def classify_document(self, document: Document) -> Classification:
        results = []
        for classifier in self._classifiers:
            try:
                result = await classifier.classify(document)
                results.append(result)
            except Exception as e:
                continue
        
        return await self._combine_classifications(results)
```

## 2. Model Implementation

```python
@dataclass
class MLClassifier(BaseClassifier):
    model_path: str
    model: Optional[ClassificationModel] = None
    
    async def load_model(self) -> None:
        """Load model from path"""
        # Implementation depends on model type
        pass
    
    async def classify(self, document: Document) -> Classification:
        if not self.model:
            await self.load_model()
            
        predictions = await self.model.predict(document.content)
        return self._convert_predictions(predictions)
    
    def get_confidence(self) -> float:
        # Implementation specific to model type
        pass
```

## 3. Pattern Matching Implementation

```python
@dataclass
class PatternClassifier(BaseClassifier):
    patterns: Dict[str, Dict[str, List[str]]]
    
    async def classify(self, document: Document) -> Classification:
        matches = self._find_matches(document.content)
        return self._create_classification(matches)
    
    def get_confidence(self) -> float:
        # Pattern matching confidence calculation
        pass
```

## 4. Configuration Management

```python
@dataclass
class ClassificationConfig:
    confidence_threshold: float = 0.8
    fallback_threshold: float = 0.6
    max_retries: int = 3
    
    class ModelConfig:
        allow_fallback: bool = True
        cache_predictions: bool = True
        batch_size: int = 32
```

## Usage Example

```python
async def main():
    # Initialize service
    service = ClassificationService()
    
    # Add classifiers
    pattern_classifier = PatternClassifier(patterns={
        'states': STATE_AGENCY_DOMAINS,
        'document_types': DOCUMENT_TYPE_PATTERNS
    })
    
    ml_classifier = MLClassifier(model_path='path/to/model')
    
    service.add_classifier(pattern_classifier)
    service.add_classifier(ml_classifier)
    
    # Process document
    doc = Document(
        content="Maine Department of Agriculture - Registration Renewal Notice",
        metadata={}
    )
    
    result = await service.classify_document(doc)
```

This design provides:

1. Hot-swappable models through the `ClassificationModel` protocol
2. Multiple classification strategies (ML and pattern-based)
3. Fallback mechanisms for reliability
4. Async processing for better performance
5. Clear separation of concerns

The service follows the routing rules defined in:

````95:125:docs/1-architecture/classification/schema/1st-pass-document-title.md
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
````


I'll help outline an integration plan and directory refactor based on the provided codebase and requirements from:


```4:7:docs/0-overview/accessible-overview-v3.md
Delta Analytical Corporation specializes in EPA and state-level pesticide registration services, handling complex regulatory documentation and multi-jurisdictional compliance. Our system processes critical communications including regulatory updates, client correspondence, product registrations, and financial documents.

## Problem Statement
We receive a high volume of incoming emails, many of which contain vital regulatory documents, client instructions, and financial information that require timely classification, storage, and follow-up. Manually processing these emails is laborious, prone to delays, and disruptive to our workflows. This increases both our time spent and risk of human error. Our goal is to build a robust, automated classification system to streamline routing, extraction, and storage, enabling our teams to focus on higher-value tasks.
```


## Directory Structure Refactor

```
src/
├── api/
│   ├── __init__.py
│   ├── routes/
│   │   ├── classification.py
│   │   ├── documents.py
│   │   └── health.py
│   └── schemas/
│       ├── classification.py
│       └── document.py
├── core/
│   ├── __init__.py
│   ├── classifiers/
│   │   ├── base.py
│   │   ├── combined.py
│   │   ├── factory.py
│   │   ├── ml/
│   │   │   ├── model.py
│   │   │   └── trainer.py
│   │   └── pattern/
│   │       ├── engine.py
│   │       └── rules.py
│   └── processors/
│       ├── content.py
│       └── validation.py
├── infrastructure/
│   ├── __init__.py
│   ├── clients/
│   │   ├── gmail.py
│   │   └── airtable.py
│   ├── queue/
│   │   ├── consumer.py
│   │   └── producer.py
│   └── storage/
│       ├── document_store.py
│       └── model_store.py
├── config/
│   ├── settings.py
│   └── patterns/
├── services/
└── utils/
```

## Integration Plan

### Phase 1: Core Classification System (Weeks 1-2)

1. **Setup Core Infrastructure**
```python:src/core/classifiers/factory.py
class ClassifierFactory:
    def create_classifier(self, classifier_type: str) -> BaseClassifier:
        if classifier_type == "pattern":
            return PatternClassifier()
        elif classifier_type == "ml":
            return MLClassifier()
        elif classifier_type == "combined":
            return CombinedClassifier()
```

2. **Pattern Matching Engine**
- Implement rule engine based on:

```13:32:docs/1-architecture/classification/classification_system.md
    subgraph Rule Engine
        Context --> RuleManager[Rule Manager]
        
        subgraph Rule Types
            Simple[Simple Rules]
            Pattern[Pattern Rules]
            Composite[Composite Rules]
            ML[ML-Powered Rules]
        end

        RuleManager --> Simple
        RuleManager --> Pattern
        RuleManager --> Composite
        RuleManager --> ML

        Simple --> RuleEval[Rule Evaluator]
        Pattern --> RuleEval
        Composite --> RuleEval
        ML --> RuleEval
    end
```


3. **ML Model Integration**
- Setup model registry and versioning
- Implement model hot-swapping
- Add feedback loop for training

### Phase 2: Service Integration (Weeks 3-4)

1. **Email Processing Pipeline**
- Gmail API integration
- Content extraction
- Document parsing
- Classification routing

2. **Storage & Persistence**
- Document storage
- Classification results
- Model artifacts
- Training data

3. **API Development**
- Classification endpoints
- Model management
- Health checks
- Metrics collection

### Phase 3: Monitoring & Feedback (Weeks 5-6)

1. **Observability**
- Classification metrics
- Model performance
- System health
- Error tracking

2. **Feedback Loop**
- User corrections
- Model retraining
- Pattern updates
- Performance analytics

## Success Metrics
Based on:

```80:86:docs/0-overview/overview-diagrams.md
| Metric | Target | Tracking |
|--------|--------|----------|
| Processing Success | >99% | 📊 |
| Classification Accuracy | >95% | 🎯 |
| Response Time | <2s | ⚡ |
| Error Rate | <0.1% | 📉 |
| Storage Optimization | >90% | 💾 |
```


## Implementation Notes

1. **Hot-Swappable Models**
- Use factory pattern for classifier creation
- Implement model versioning
- Support A/B testing
- Enable gradual rollout

2. **Configuration Management**
- Move patterns to YAML files
- Implement hot reload
- Add validation
- Version control

3. **Error Handling**
- Implement retry mechanisms
- Add circuit breakers
- Setup dead letter queues
- Monitor classification confidence

---

Here's a detailed implementation task list based on our integration plan:

## Phase 1: Core Classification System (Weeks 1-2)

### Infrastructure Setup
- [ ] Create new directory structure
- [ ] Setup dependency management
- [ ] Configure logging
- [ ] Initialize test framework
- [ ] Setup CI/CD pipeline

### Core Classification Engine
- [ ] Implement BaseClassifier interface
- [ ] Create ClassifierFactory
- [ ] Add classifier registration mechanism
- [ ] Setup model versioning system
- [ ] Implement hot-swap mechanism

### Pattern Matching Engine
- [ ] Build rule engine framework
- [ ] Implement pattern matching rules
- [ ] Add regex support
- [ ] Create confidence scoring system
- [ ] Setup pattern validation

### ML Integration
- [ ] Setup model registry
- [ ] Implement model loading/unloading
- [ ] Create prediction pipeline
- [ ] Add batch processing support
- [ ] Setup model metrics collection

## Phase 2: Service Integration (Weeks 3-4)

### Email Processing
- [ ] Setup Gmail API client
- [ ] Implement email fetching
- [ ] Add content extraction
- [ ] Create attachment handling
- [ ] Setup email queuing

### Document Processing
- [ ] Implement PDF parsing
- [ ] Add text extraction
- [ ] Create metadata extraction
- [ ] Setup document validation
- [ ] Implement storage interface

### API Development
- [ ] Create FastAPI application
- [ ] Add classification endpoints
- [ ] Implement health checks
- [ ] Setup authentication
- [ ] Add rate limiting

### Storage Layer
- [ ] Setup document store
- [ ] Implement model storage
- [ ] Create classification history
- [ ] Add audit logging
- [ ] Setup backup system

## Phase 3: Monitoring & Feedback (Weeks 5-6)

### Monitoring Setup
- [ ] Implement metrics collection
- [ ] Setup performance monitoring
- [ ] Add error tracking
- [ ] Create health checks
- [ ] Setup alerting

### Feedback System
- [ ] Create feedback collection
- [ ] Implement correction handling
- [ ] Setup retraining pipeline
- [ ] Add performance analytics
- [ ] Create reporting system

### Testing & Validation
- [ ] Write unit tests
- [ ] Add integration tests
- [ ] Create performance tests
- [ ] Setup continuous testing
- [ ] Implement smoke tests

### Documentation
- [ ] Write API documentation
- [ ] Create setup guides
- [ ] Add configuration docs
- [ ] Document deployment process
- [ ] Create troubleshooting guide

## Final Steps

### Deployment
- [ ] Setup staging environment
- [ ] Configure production environment
- [ ] Create deployment scripts
- [ ] Setup monitoring
- [ ] Create rollback procedures

### Training & Handoff
- [ ] Create user documentation
- [ ] Setup training environment
- [ ] Write training materials
- [ ] Conduct training sessions
- [ ] Create support procedures

### Performance Optimization
- [ ] Optimize classification speed
- [ ] Improve accuracy metrics
- [ ] Reduce resource usage
- [ ] Enhance scalability
- [ ] Fine-tune configurations

This task list aligns with the core requirements from:

````8:15:docs/0-overview/about_delta-ai_context.md
### 1. Document Processing & Validation
* Registration applications across federal and state jurisdictions
* Label compliance verification for multiple regulatory standards
* Technical data review and validation
* Chain of custody maintenance for sensitive documents

### 2. Regulatory Knowledge Management
* Cross-reference of requirements across jurisdictions
* Tracking of regulatory updates and requirement changes
* Management of compliance timelines and deadlines
* Maintenance of requirement databases and updates
````
$$



