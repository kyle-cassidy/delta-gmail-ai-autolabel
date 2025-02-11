# Document Classification Microservice

```python
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass
import asyncio
import json
import re
from datetime import datetime
from enum import Enum

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

@dataclass
class Document:
    content: str
    metadata: Dict[str, Any]

# Abstract Base Classes for Classifiers
class BaseClassifier(ABC):
    @abstractmethod
    async def classify(self, document: Document) -> Classification:
        pass
    
    @abstractmethod
    def get_confidence(self) -> float:
        pass

class PatternClassifier(BaseClassifier):
    def __init__(self, patterns: Dict[str, Any]):
        self.patterns = patterns
        self._compile_patterns()
        
    def _compile_patterns(self):
        """Pre-compile all regex patterns for performance"""
        for category, pattern_list in self.patterns.items():
            if isinstance(pattern_list, list):
                self.patterns[category] = [re.compile(p, re.I) for p in pattern_list]
            elif isinstance(pattern_list, dict):
                for key, patterns in pattern_list.items():
                    if isinstance(patterns, list):
                        self.patterns[category][key] = [re.compile(p, re.I) for p in patterns]

    async def classify(self, document: Document) -> Classification:
        matches = self._find_matches(document.content)
        year, term = self._extract_year_term(document)
        state = self._extract_state(document)
        client = self._extract_client(document)
        base_type = self._determine_base_type(matches)
        
        return Classification(
            year=year,
            term=term,
            state=state,
            client=client,
            base_type=base_type,
            confidence=self.get_confidence()
        )
    
    def _find_matches(self, content: str) -> Dict[str, List[str]]:
        matches = {}
        for category, patterns in self.patterns.items():
            if isinstance(patterns, list):
                matches[category] = []
                for pattern in patterns:
                    if found := pattern.findall(content):
                        matches[category].extend(found)
        return matches

    def get_confidence(self) -> float:
        # Implement confidence calculation based on pattern matches
        return 0.85

class MLClassifier(BaseClassifier):
    def __init__(self, model_path: str):
        self.model = self._load_model(model_path)
        self.last_confidence = 0.0
        
    def _load_model(self, path: str):
        # Placeholder for model loading
        return None
        
    async def classify(self, document: Document) -> Classification:
        # Placeholder for ML classification
        return Classification(
            year=2025,
            term="Q1",
            state="ME",
            client="EEA",
            base_type=BaseType.NEW,
            confidence=self.get_confidence()
        )
        
    def get_confidence(self) -> float:
        return self.last_confidence

# Classification Service
class ClassificationService:
    def __init__(self):
        self.classifiers: List[BaseClassifier] = []
        self.confidence_threshold = 0.9
        
    def add_classifier(self, classifier: BaseClassifier):
        self.classifiers.append(classifier)
        
    def remove_classifier(self, classifier_type: str):
        self.classifiers = [c for c in c.classifiers 
                          if not isinstance(c, classifier_type)]
        
    async def classify_document(self, document: Document) -> Classification:
        results = await asyncio.gather(
            *[classifier.classify(document) for classifier in self.classifiers]
        )
        
        return self._combine_classifications(results)
        
    def _combine_classifications(self, results: List[Classification]) -> Classification:
        # Weight and combine classifications based on confidence
        weights = [r.confidence for r in results]
        total_weight = sum(weights)
        
        if not total_weight:
            return results[0]  # Default to first result if no confidence
            
        # Normalize weights
        weights = [w/total_weight for w in weights]
        
        # Take highest confidence classification as base
        base = max(results, key=lambda x: x.confidence)
        
        # Average confidence
        confidence = sum(r.confidence * w for r, w in zip(results, weights))
        
        base.confidence = confidence
        return base

# Example Usage
async def main():
    # Initialize service
    service = ClassificationService()
    
    # Add classifiers
    pattern_classifier = PatternClassifier(patterns={
        'states': STATE_AGENCY_DOMAINS,
        'document_types': DOCUMENT_TYPE_PATTERNS,
        'status': STATUS_PATTERNS
    })
    
    ml_classifier = MLClassifier(model_path='path/to/model')
    
    service.add_classifier(pattern_classifier)
    service.add_classifier(ml_classifier)
    
    # Example document
    doc = Document(
        content="Maine Department of Agriculture - Registration Renewal Notice",
        metadata={}
    )
    
    # Classify
    result = await service.classify_document(doc)
    
    print(f"Classification: {result}")
    print(f"Confidence: {result.confidence}")

if __name__ == "__main__":
    asyncio.run(main())
```