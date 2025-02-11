# Dynamic Classification Schema Design

## Overview
This document outlines the design for a flexible, learning-enabled classification system that supports faceted navigation and interactive refinement.

## Core Components

### 1. Classification Hierarchy
```python
@dataclass
class ClassificationNode:
    """Represents a node in the classification hierarchy"""
    id: str
    name: str
    parent_id: Optional[str]
    attributes: Dict[str, Any]
    rules: List[ClassificationRule]
    examples: List[DocumentExample]
    created_at: datetime
    modified_at: datetime
    version: int

@dataclass
class ClassificationRule:
    """Rule for classifying documents"""
    pattern: str
    context: Dict[str, Any]
    confidence_threshold: float
    priority: int
    created_by: str
    performance_metrics: Dict[str, float]
```

### 2. Learning Components

```python
class ExampleBasedLearner:
    """Learns classification rules from examples"""
    
    async def learn_from_example(
        self, 
        document: Document,
        classifications: List[str],
        context: Dict[str, Any]
    ) -> List[ClassificationRule]:
        """Generate rules from a correctly classified example"""
        pass

    async def validate_rule(
        self,
        rule: ClassificationRule,
        test_set: List[Document]
    ) -> RulePerformance:
        """Validate a rule against test documents"""
        pass

    async def suggest_refinements(
        self,
        rule: ClassificationRule,
        performance_data: RulePerformance
    ) -> List[RuleRefinement]:
        """Suggest ways to improve rule performance"""
        pass
```

### 3. Interactive Classification Interface

```typescript
interface ClassificationWorkbench {
  // Document viewing and annotation
  currentDocument: Document;
  suggestedTags: Tag[];
  appliedTags: Tag[];
  confidence: Record<string, number>;

  // Learning interface
  onAcceptSuggestion: (tag: Tag) => void;
  onRejectSuggestion: (tag: Tag) => void;
  onAddExample: (document: Document, tags: Tag[]) => void;
  onRuleRefinement: (rule: Rule, modification: Modification) => void;
}
```

## Classification Schemas

### 1. Regulatory Document Schema
```json
{
  "regulatory": {
    "document_type": {
      "values": [
        "application",
        "renewal",
        "amendment",
        "correspondence"
      ],
      "rules": [
        {
          "pattern": "renewal fee|renewal period|renew registration",
          "type": "renewal",
          "confidence": 0.85
        }
      ]
    },
    "state": {
      "values": ["CA", "NY", "KS"],
      "rules": [
        {
          "pattern": "California Department of|CA Reg",
          "type": "CA",
          "confidence": 0.9
        }
      ]
    },
    "status": {
      "values": [
        "pending",
        "approved",
        "rejected",
        "needs_info"
      ],
      "rules": [
        {
          "pattern": "approved|registration granted",
          "type": "approved",
          "confidence": 0.95
        }
      ]
    }
  }
}
```

### 2. Client Information Schema
```json
{
  "client": {
    "company_type": {
      "values": [
        "manufacturer",
        "distributor",
        "agent"
      ],
      "attributes": {
        "regulatory_requirements": ["string"],
        "submission_types": ["string"]
      }
    },
    "product_lines": {
      "values": [
        "soil_amendment",
        "fertilizer",
        "pesticide"
      ],
      "attributes": {
        "regulatory_bodies": ["string"],
        "testing_requirements": ["string"]
      }
    }
  }
}
```

## Learning Mechanisms

### 1. Pattern Recognition
```python
class PatternLearner:
    """Learns document patterns from examples"""
    
    async def extract_patterns(
        self,
        documents: List[Document],
        classification: str
    ) -> List[Pattern]:
        """Extract common patterns from similarly classified docs"""
        pass

    async def validate_patterns(
        self,
        patterns: List[Pattern],
        test_docs: List[Document]
    ) -> List[PatternPerformance]:
        """Validate extracted patterns"""
        pass

    async def refine_patterns(
        self,
        patterns: List[Pattern],
        feedback: List[PatternFeedback]
    ) -> List[Pattern]:
        """Refine patterns based on feedback"""
        pass
```

### 2. Context Learning
```python
class ContextLearner:
    """Learns from document context"""
    
    async def learn_context_rules(
        self,
        documents: List[Document],
        context: Dict[str, Any]
    ) -> List[ContextRule]:
        """Learn rules that depend on context"""
        pass

    async def apply_context(
        self,
        base_classification: Classification,
        context: Dict[str, Any]
    ) -> Classification:
        """Apply contextual rules to refine classification"""
        pass
```

## Example-Based Classification

### 1. Example Management
```python
@dataclass
class DocumentExample:
    """Represents a known-good classification example"""
    document_id: str
    classifications: List[str]
    context: Dict[str, Any]
    annotated_by: str
    annotation_date: datetime
    confidence: float
    performance_impact: Dict[str, float]

class ExampleManager:
    """Manages classification examples"""
    
    async def add_example(
        self,
        document: Document,
        classifications: List[str],
        annotator: str
    ) -> DocumentExample:
        """Add a new classification example"""
        pass

    async def find_similar_examples(
        self,
        document: Document
    ) -> List[DocumentExample]:
        """Find similar examples for a document"""
        pass

    async def validate_example(
        self,
        example: DocumentExample
    ) -> ExampleValidation:
        """Validate an example's usefulness"""
        pass
```

### 2. Interactive Learning
```python
class InteractiveLearner:
    """Learns from user interactions"""
    
    async def suggest_classifications(
        self,
        document: Document,
        context: Dict[str, Any]
    ) -> List[ClassificationSuggestion]:
        """Suggest classifications for a document"""
        pass

    async def learn_from_feedback(
        self,
        document: Document,
        accepted: List[str],
        rejected: List[str]
    ) -> None:
        """Learn from user feedback"""
        pass

    async def explain_suggestion(
        self,
        suggestion: ClassificationSuggestion
    ) -> List[ExplanationFactor]:
        """Explain why a classification was suggested"""
        pass
```

## Implementation Considerations

1. **Performance**
   - Cache frequently used patterns
   - Optimize pattern matching
   - Batch learning updates

2. **Accuracy**
   - Confidence thresholds
   - Validation sets
   - Cross-validation

3. **User Experience**
   - Quick feedback loops
   - Clear explanations
   - Easy corrections

4. **Maintenance**
   - Version control for rules
   - Performance monitoring
   - Rule cleanup

## Next Steps

1. **Phase 1: Basic Classification**
   - Implement core schemas
   - Basic pattern matching
   - Simple user interface

2. **Phase 2: Learning System**
   - Example-based learning
   - Pattern refinement
   - Context awareness

3. **Phase 3: Advanced Features**
   - Interactive learning
   - Performance optimization
   - Advanced UI