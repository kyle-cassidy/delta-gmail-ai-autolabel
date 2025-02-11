"""
ClassificationService: Manages email and document classification.

Responsibilities:
- Email categorization by type:
    - Client Code: ARB, BIN, etc.
    - State Regulator: CA, NY, etc.
    - Type: 
        - Certificates:
            - Approval
            - Certificate Document (PDF vs go to portal)
        - Notifications:
            - Payment (Confirmation, Received, Failed, Overdue, Paid)
        - Renewal Reminder

- Certificate classification
- Priority determination
- Routing rule implementation
- Machine learning model integration
- Classification accuracy tracking
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from pathlib import Path
import asyncio
import logging
from .content_extraction_service import ContentExtractionService

logger = logging.getLogger(__name__)

class ClassificationService:
    def __init__(self, storage_service=None, model_service=None, content_extractor: Optional[ContentExtractionService] = None):
        self.storage = storage_service
        self.model = model_service
        self.client_codes = {"ARB", "BIN"}  # Example codes
        self.state_codes = {"CA", "NY", "TX"}  # Example states
        self.content_extractor = content_extractor or ContentExtractionService()

    async def classify(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify email content and determine its type, priority, and routing.
        
        Args:
            content: Dictionary containing email content and metadata
            
        Returns:
            Dictionary containing classification results
        """
        classification = {
            "timestamp": datetime.utcnow().isoformat(),
            "client_code": await self._extract_client_code(content),
            "state": await self._extract_state(content),
            "document_type": await self._determine_document_type(content),
            "priority": await self._determine_priority(content),
            "confidence_score": 0.0,
            "routing_rules": []
        }
        
        # Update confidence score based on classification results
        classification["confidence_score"] = await self._calculate_confidence(classification)
        
        # Determine routing rules based on classification
        classification["routing_rules"] = await self._determine_routing(classification)
        
        # Track classification for accuracy monitoring
        await self._track_classification(classification)
        
        return classification

    async def _extract_client_code(self, content: Dict[str, Any]) -> Optional[str]:
        """Extract client code from email content."""
        # Implementation would use regex, ML model, or rule-based system
        return None

    async def _extract_state(self, content: Dict[str, Any]) -> Optional[str]:
        """Extract state code from email content."""
        # Implementation would use regex, ML model, or rule-based system
        return None

    async def _determine_document_type(self, content: Dict[str, Any]) -> str:
        """Determine the type of document (certificate, notification, etc.)."""
        # Implementation would analyze content and attachments
        return "unknown"

    async def _determine_priority(self, content: Dict[str, Any]) -> int:
        """Determine processing priority (1-5, where 1 is highest)."""
        # Implementation would use business rules and content analysis
        return 3

    async def _calculate_confidence(self, classification: Dict[str, Any]) -> float:
        """Calculate confidence score for the classification."""
        # Implementation would evaluate various factors
        return 0.0

    async def _determine_routing(self, classification: Dict[str, Any]) -> List[str]:
        """Determine routing rules based on classification."""
        # Implementation would use business rules
        return []

    async def _track_classification(self, classification: Dict[str, Any]) -> None:
        """Track classification for accuracy monitoring."""
        if self.storage:
            await self.storage.store_classification(classification)

    async def get_classification_accuracy(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, float]:
        """Get classification accuracy metrics."""
        if self.storage:
            return await self.storage.get_classification_metrics(
                start_date=start_date,
                end_date=end_date
            )
        return {}

    async def classify_document(self, file_path: Union[str, Path]) -> Dict:
        """
        Classify a single document and extract its content.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Dict containing classification results and extracted content
        """
        try:
            # Extract content using Gemini
            extraction_result = await self.content_extractor.extract_content(file_path)
            
            # Enhance the classification with confidence scores and metadata
            classification = self._enhance_classification(extraction_result)
            
            return {
                'file_path': str(file_path),
                'success': True,
                'classification': classification
            }
            
        except Exception as e:
            logger.error(f"Classification failed for {file_path}: {str(e)}")
            return {
                'file_path': str(file_path),
                'success': False,
                'error': str(e)
            }
            
    async def classify_batch(self, file_paths: List[Union[str, Path]], 
                           max_concurrent: int = 5) -> List[Dict]:
        """
        Classify multiple documents concurrently.
        
        Args:
            file_paths: List of paths to documents
            max_concurrent: Maximum number of concurrent classifications
            
        Returns:
            List of classification results
        """
        # Process in batches to avoid overwhelming the API
        results = []
        for i in range(0, len(file_paths), max_concurrent):
            batch = file_paths[i:i + max_concurrent]
            tasks = [self.classify_document(path) for path in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            results.extend(batch_results)
        return results
    
    def _enhance_classification(self, extraction_result: Dict) -> Dict:
        """
        Enhance the extraction result with additional classification metadata.
        
        Args:
            extraction_result: Raw extraction result from Gemini
            
        Returns:
            Enhanced classification with confidence scores and metadata
        """
        # Start with the basic extraction
        classification = {
            'document_type': extraction_result.get('document_type'),
            'confidence': self._calculate_confidence(extraction_result),
            'entities': extraction_result.get('entities', {}),
            'key_fields': extraction_result.get('key_fields', {}),
            'metadata': {
                'has_tables': bool(extraction_result.get('tables')),
                'entity_count': sum(len(v) for v in extraction_result.get('entities', {}).values()),
                'field_count': sum(len(v) for v in extraction_result.get('key_fields', {}).values())
            },
            'summary': extraction_result.get('summary')
        }
        
        # Add classification flags
        classification['flags'] = self._generate_flags(classification)
        
        return classification
    
    def _calculate_confidence(self, extraction_result: Dict) -> float:
        """
        Calculate a confidence score for the classification.
        
        Args:
            extraction_result: Extraction result from Gemini
            
        Returns:
            Confidence score between 0 and 1
        """
        # Simple heuristic based on presence of key information
        score = 0.0
        total_weights = 0.0
        
        weights = {
            'document_type': 0.3,
            'entities': 0.2,
            'key_fields': 0.3,
            'tables': 0.1,
            'summary': 0.1
        }
        
        for field, weight in weights.items():
            if field in extraction_result and extraction_result[field]:
                if field in ['entities', 'key_fields']:
                    # Check if any subfields have content
                    has_content = any(extraction_result[field].values())
                    score += weight if has_content else 0
                else:
                    score += weight
                total_weights += weight
                
        return round(score / total_weights, 2) if total_weights > 0 else 0.0
    
    def _generate_flags(self, classification: Dict) -> List[str]:
        """
        Generate warning flags based on the classification results.
        
        Args:
            classification: Enhanced classification result
            
        Returns:
            List of warning flags
        """
        flags = []
        
        # Check confidence
        if classification['confidence'] < 0.5:
            flags.append('LOW_CONFIDENCE')
            
        # Check for missing critical information
        if not classification['document_type']:
            flags.append('MISSING_DOCUMENT_TYPE')
            
        # Check entities
        if not any(classification['entities'].values()):
            flags.append('NO_ENTITIES_FOUND')
            
        # Check key fields
        key_fields = classification['key_fields']
        if not key_fields.get('dates'):
            flags.append('NO_DATES_FOUND')
        if not key_fields.get('registration_numbers'):
            flags.append('NO_REGISTRATION_NUMBERS')
            
        return flags
