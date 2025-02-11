"""
Docling Document Classifier Implementation

Uses IBM's open-source Docling library for high-fidelity document parsing and classification.
Runs locally and preserves document structure.
"""
from typing import Dict, List, Optional, Union
from pathlib import Path
import asyncio
import json
from docling import DocProcessor, TableFormer  # Note: Package name may differ
from .base import BaseDocumentClassifier, ClassificationResult
from .domain_config import DomainConfig

class DoclingClassifier(BaseDocumentClassifier):
    """Document classifier using IBM's Docling library."""
    
    def __init__(self, model_path: Optional[str] = None, config_dir: Optional[Path] = None):
        """
        Initialize the Docling classifier.
        
        Args:
            model_path: Optional path to custom model weights
            config_dir: Optional path to configuration directory
        """
        # Initialize Docling components
        self.processor = DocProcessor(model_path=model_path)
        self.table_extractor = TableFormer()
        
        # Load domain configuration
        self.domain_config = DomainConfig(config_dir)
        
    async def classify_document(self, file_path: Union[str, Path]) -> ClassificationResult:
        """Classify a single document using Docling."""
        try:
            # Load and validate the document
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Process the document with Docling
            # Note: We're running CPU-intensive operations in a thread pool
            doc_result = await asyncio.get_event_loop().run_in_executor(
                None, self._process_document, file_path
            )
            
            # Convert Docling output to our standard format
            return self._convert_to_classification_result(doc_result)
            
        except Exception as e:
            raise Exception(f"Docling classification failed: {str(e)}")
    
    async def classify_batch(self, file_paths: List[Union[str, Path]], 
                           max_concurrent: int = 5) -> List[ClassificationResult]:
        """Classify multiple documents concurrently."""
        results = []
        for i in range(0, len(file_paths), max_concurrent):
            batch = file_paths[i:i + max_concurrent]
            tasks = [self.classify_document(path) for path in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle any exceptions in the batch
            for result in batch_results:
                if isinstance(result, Exception):
                    results.append(self._create_error_result(str(result)))
                else:
                    results.append(result)
                    
        return results
    
    def get_classifier_info(self) -> Dict[str, str]:
        """Get information about this classifier implementation."""
        return {
            "name": "Docling Classifier",
            "version": "1.0.0",
            "description": "Uses IBM's Docling library for high-fidelity local document processing",
            "provider": "IBM (Open Source)",
            "features": [
                "Local processing (no data leaves your system)",
                "High-accuracy layout preservation",
                "Superior table extraction via TableFormer",
                "No API costs or rate limits",
                "Domain-aware classification using regulatory configurations"
            ]
        }
    
    def _process_document(self, file_path: Path) -> Dict:
        """
        Process a document using Docling.
        
        Args:
            file_path: Path to the document
            
        Returns:
            Dictionary containing extracted information
        """
        # Process the document
        doc = self.processor.process_document(file_path)
        
        # Get document text for pattern matching
        doc_text = doc.get_text()
        
        # Extract tables if present
        tables = []
        if doc.has_tables:
            tables = self.table_extractor.extract_tables(doc)
        
        # Use domain configuration to extract entities and information
        entities = self._extract_entities(doc, doc_text)
        key_fields = self._extract_key_fields(doc)
        
        # Determine document type using domain patterns
        doc_type = self.domain_config.get_document_type(doc_text)
        
        # Get related document types
        related_types = self.domain_config.get_related_documents(doc_type) if doc_type else []
        
        return {
            "document_type": doc_type,
            "entities": entities,
            "key_fields": key_fields,
            "tables": tables,
            "summary": doc.get_summary(),
            "metadata": {
                "page_count": doc.page_count,
                "has_tables": bool(tables),
                "confidence": doc.extraction_confidence,
                "related_document_types": related_types,
                "product_categories": self.domain_config.get_product_categories(doc_text)
            }
        }
    
    def _extract_entities(self, doc, doc_text: str) -> Dict[str, List[str]]:
        """Extract entities using both Docling and domain configuration."""
        # Get entities from Docling
        companies = doc.extract_entities(entity_type="ORG")
        products = doc.extract_entities(entity_type="PRODUCT")
        
        # Get states from domain configuration
        states = self.domain_config.get_states(doc_text)
        
        return {
            "companies": companies,
            "products": products,
            "states": states
        }
    
    def _extract_key_fields(self, doc) -> Dict[str, List[str]]:
        """Extract and validate key fields."""
        # Extract basic fields
        dates = doc.extract_dates()
        registration_numbers = doc.extract_patterns(r"REG-?\d+|LIC-?\d+")
        amounts = doc.extract_patterns(r"\$?\d+(?:,\d{3})*(?:\.\d{2})?")
        
        # Validate registration numbers against state-specific rules
        doc_text = doc.get_text()
        states = self.domain_config.get_states(doc_text)
        
        valid_numbers = []
        for number in registration_numbers:
            # If we have state context, validate against state rules
            if states:
                if any(self.domain_config.validate_registration_number(number, state) 
                      for state in states):
                    valid_numbers.append(number)
            else:
                # If no state context, include all numbers
                valid_numbers.append(number)
        
        return {
            "dates": dates,
            "registration_numbers": valid_numbers,
            "amounts": amounts
        }
    
    def _convert_to_classification_result(self, doc_result: Dict) -> ClassificationResult:
        """Convert Docling output to standardized ClassificationResult."""
        # Calculate confidence based on Docling's metrics and domain validation
        base_confidence = doc_result.get("metadata", {}).get("confidence", 0.0)
        domain_confidence = self._calculate_domain_confidence(doc_result)
        confidence = (base_confidence + domain_confidence) / 2
        
        # Generate any warning flags
        flags = self._generate_flags(doc_result, confidence)
        
        # Create metadata
        metadata = {
            **doc_result.get("metadata", {}),
            'classifier': self.get_classifier_info()['name'],
            'domain_confidence': domain_confidence
        }
        
        # Construct the result
        return ClassificationResult(
            document_type=doc_result.get("document_type"),
            confidence=confidence,
            entities=doc_result.get("entities", {}),
            key_fields=doc_result.get("key_fields", {}),
            metadata=metadata,
            summary=doc_result.get("summary"),
            flags=flags
        )
    
    def _calculate_domain_confidence(self, result: Dict) -> float:
        """Calculate confidence based on domain validation."""
        score = 0.0
        total_checks = 0
        
        # Check document type against known types
        if result.get("document_type"):
            score += 1
            total_checks += 1
        
        # Check if found states are valid
        if result.get("entities", {}).get("states"):
            score += 1
            total_checks += 1
        
        # Check if found product categories match our domain
        if result.get("metadata", {}).get("product_categories"):
            score += 1
            total_checks += 1
        
        # Check registration number validation
        if result.get("key_fields", {}).get("registration_numbers"):
            score += 1
            total_checks += 1
        
        return round(score / total_checks, 2) if total_checks > 0 else 0.0
    
    def _generate_flags(self, result: Dict, confidence: float) -> List[str]:
        """Generate warning flags based on classification results."""
        flags = []
        
        # Check confidence
        if confidence < 0.5:
            flags.append('LOW_CONFIDENCE')
            
        # Check for missing critical information
        if not result.get("document_type"):
            flags.append('MISSING_DOCUMENT_TYPE')
            
        # Check entities
        if not any(result.get("entities", {}).values()):
            flags.append('NO_ENTITIES_FOUND')
            
        # Check key fields
        key_fields = result.get("key_fields", {})
        if not key_fields.get("dates"):
            flags.append('NO_DATES_FOUND')
        if not key_fields.get("registration_numbers"):
            flags.append('NO_REGISTRATION_NUMBERS')
            
        # Add domain-specific flags
        if not result.get("metadata", {}).get("product_categories"):
            flags.append('NO_PRODUCT_CATEGORY_MATCH')
            
        return flags
    
    def _create_error_result(self, error_message: str) -> ClassificationResult:
        """Create a ClassificationResult for error cases."""
        return ClassificationResult(
            document_type=None,
            confidence=0.0,
            entities={'companies': [], 'products': [], 'states': []},
            key_fields={'dates': [], 'registration_numbers': [], 'amounts': []},
            metadata={
                'error': error_message,
                'classifier': self.get_classifier_info()['name']
            },
            summary=None,
            flags=['CLASSIFICATION_ERROR']
        ) 