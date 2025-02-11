"""
Gemini Flash Document Classifier Implementation
"""
import os
from typing import Dict, List, Optional, Union
import google.generativeai as genai
from pathlib import Path
import json
import asyncio
from .base import BaseDocumentClassifier, ClassificationResult
from .domain_config import DomainConfig
import PyPDF2

class GeminiClassifier(BaseDocumentClassifier):
    """Document classifier using Google's Gemini Flash model."""
    
    def __init__(self, api_key: Optional[str] = None, config_dir: Optional[Path] = None):
        """
        Initialize the Gemini classifier.
        
        Args:
            api_key: Google API key for Gemini
            config_dir: Optional path to configuration directory
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key is required")
        
        # Configure the Gemini API
        genai.configure(api_key=self.api_key)
        # Initialize the model (using Flash for optimal speed/quality balance)
        self.model = genai.GenerativeModel('gemini-pro-vision')
        
        # Load domain configuration
        self.domain_config = DomainConfig(config_dir)
        
    async def classify_document(self, file_path: Union[str, Path]) -> ClassificationResult:
        """Classify a single document using Gemini Flash."""
        try:
            # Load and validate the document
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Check file size (20MB limit)
            file_size = file_path.stat().st_size
            if file_size > 20 * 1024 * 1024:  # 20MB in bytes
                raise ValueError("File size exceeds 20MB limit")
            
            # Check page count for PDFs
            if file_path.suffix.lower() == '.pdf':
                with open(file_path, 'rb') as f:
                    pdf = PyPDF2.PdfReader(f)
                    if len(pdf.pages) > 3600:
                        raise ValueError("Document exceeds 3600 page limit")
            
            # Read file content and convert to base64
            import base64
            import mimetypes
            
            mime_type, _ = mimetypes.guess_type(str(file_path))
            if not mime_type:
                mime_type = 'application/octet-stream'
            
            with open(file_path, 'rb') as f:
                file_content = f.read()
                file_data = base64.b64encode(file_content).decode('utf-8')
            
            # Prepare the prompt for Gemini
            prompt = """
            Please analyze this document and extract the following information in JSON format:
            {
                "document_type": "The type of regulatory document (e.g., registration, renewal, tonnage report)",
                "entities": {
                    "companies": ["List of company names mentioned"],
                    "products": ["List of product names/types mentioned"],
                    "states": ["List of US states mentioned"]
                },
                "key_fields": {
                    "dates": ["Any important dates mentioned"],
                    "registration_numbers": ["Any registration or license numbers"],
                    "amounts": ["Any monetary amounts or quantities"]
                },
                "tables": ["Array of any tables found, each as a list of rows"],
                "summary": "A brief summary of the document's purpose and content"
            }
            
            Please be precise and only include information that is explicitly present in the document.
            If any field has no relevant information, return an empty array or null.
            """
            
            # Process with Gemini
            response = self.model.generate_content([{
                'parts': [
                    {'text': prompt},
                    {'inline_data': {
                        'mime_type': mime_type,
                        'data': file_data
                    }}
                ]
            }])
            
            # Parse and validate the response
            try:
                raw_result = json.loads(response.text)
                return self._convert_to_classification_result(raw_result)
            except json.JSONDecodeError:
                return self._create_error_result("Failed to parse Gemini response as JSON")
            
        except FileNotFoundError as e:
            raise  # Re-raise FileNotFoundError directly
        except ValueError as e:
            raise  # Re-raise ValueError directly
        except Exception as e:
            return self._create_error_result(str(e))
            
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
            "name": "Gemini Flash Classifier",
            "version": "1.0.0",
            "description": "Uses Google's Gemini Flash model for document classification and extraction",
            "model": "gemini-pro-vision",
            "provider": "Google"
        }
        
    def _convert_to_classification_result(self, raw_result: Dict) -> ClassificationResult:
        """Convert raw Gemini output to standardized ClassificationResult."""
        # Get document text for domain validation
        doc_text = raw_result.get('text', '')  # Gemini should include the extracted text
        
        # Use domain config to validate and enhance the classification
        doc_type = self.domain_config.get_document_type(doc_text) or raw_result.get('document_type')
        
        # Get domain-validated states
        states = self.domain_config.get_states(doc_text)
        entities = raw_result.get('entities', {'companies': [], 'products': [], 'states': []})
        entities['states'] = states  # Override with validated states
        
        # Validate registration numbers
        key_fields = raw_result.get('key_fields', {'dates': [], 'registration_numbers': [], 'amounts': []})
        if states:
            valid_numbers = []
            for number in key_fields.get('registration_numbers', []):
                if any(self.domain_config.validate_registration_number(number, state) 
                      for state in states):
                    valid_numbers.append(number)
            key_fields['registration_numbers'] = valid_numbers
        
        # Calculate confidence including domain validation
        base_confidence = self._calculate_confidence(raw_result)
        domain_confidence = self._calculate_domain_confidence(raw_result, doc_text)
        confidence = (base_confidence + domain_confidence) / 2
        
        # Generate flags including domain-specific ones
        flags = self._generate_flags(raw_result, confidence)
        
        # Add domain-specific metadata
        metadata = {
            'has_tables': bool(raw_result.get('tables')),
            'entity_count': sum(len(v) for v in entities.values()),
            'field_count': sum(len(v) for v in key_fields.values()),
            'classifier': self.get_classifier_info()['name'],
            'domain_confidence': domain_confidence,
            'product_categories': self.domain_config.get_product_categories(doc_text),
            'related_document_types': self.domain_config.get_related_documents(doc_type) if doc_type else []
        }
        
        return ClassificationResult(
            document_type=doc_type,
            confidence=confidence,
            entities=entities,
            key_fields=key_fields,
            metadata=metadata,
            summary=raw_result.get('summary'),
            flags=flags
        )
        
    def _calculate_confidence(self, result: Dict) -> float:
        """Calculate a confidence score for the classification."""
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
            if field in result and result[field]:
                if field in ['entities', 'key_fields']:
                    # Check if any subfields have content
                    has_content = any(result[field].values())
                    score += weight if has_content else 0
                else:
                    score += weight
                total_weights += weight
                
        return round(score / total_weights, 2) if total_weights > 0 else 0.0
        
    def _calculate_domain_confidence(self, result: Dict, doc_text: str) -> float:
        """Calculate confidence based on domain validation."""
        score = 0.0
        total_checks = 0
        
        # Check document type against known types
        if result.get("document_type"):
            score += 1
            total_checks += 1
        
        # Check if found states are valid
        if self.domain_config.get_states(doc_text):
            score += 1
            total_checks += 1
        
        # Check if found product categories match our domain
        if self.domain_config.get_product_categories(doc_text):
            score += 1
            total_checks += 1
        
        # Check registration number validation
        key_fields = result.get("key_fields", {})
        if key_fields.get("registration_numbers"):
            score += 1
            total_checks += 1
        
        return round(score / total_checks, 2) if total_checks > 0 else 0.0
        
    def _generate_flags(self, result: Dict, confidence: float) -> List[str]:
        """Generate warning flags based on the classification results."""
        flags = []
        
        # Check confidence
        if confidence < 0.5:
            flags.append('LOW_CONFIDENCE')
            
        # Check for missing critical information
        if not result.get('document_type'):
            flags.append('MISSING_DOCUMENT_TYPE')
            
        # Check entities
        if not any(result.get('entities', {}).values()):
            flags.append('NO_ENTITIES_FOUND')
            
        # Check key fields
        key_fields = result.get('key_fields', {})
        if not key_fields.get('dates'):
            flags.append('NO_DATES_FOUND')
        if not key_fields.get('registration_numbers'):
            flags.append('NO_REGISTRATION_NUMBERS')
            
        # Add domain-specific flags
        doc_text = result.get('text', '')
        if not self.domain_config.get_product_categories(doc_text):
            flags.append('NO_PRODUCT_CATEGORY_MATCH')
            
        return flags
        
    def _create_error_result(self, error_message: str) -> ClassificationResult:
        """Create a ClassificationResult instance for error cases."""
        return ClassificationResult(
            document_type=None,
            confidence=0.0,
            entities={'companies': [], 'products': [], 'states': []},
            key_fields={'dates': [], 'registration_numbers': [], 'amounts': []},
            metadata={'error': error_message, 'classifier': 'Gemini Flash Classifier'},
            summary=None,
            flags=['CLASSIFICATION_ERROR']
        ) 