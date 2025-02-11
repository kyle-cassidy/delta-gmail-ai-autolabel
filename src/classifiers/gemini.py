"""
Gemini Flash Document Classifier Implementation
"""
import os
from typing import Dict, List, Optional, Union, Tuple
import google.generativeai as genai
from pathlib import Path
import json
import asyncio
import io
import base64
import mimetypes
from .base import BaseDocumentClassifier, ClassificationResult
from .domain_config import DomainConfig

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
        
    async def classify_document(self, 
                              source: Union[str, Path, bytes],
                              source_type: str = "file",
                              metadata: Optional[Dict] = None) -> ClassificationResult:
        """Classify a single document using Gemini Flash."""
        try:
            # Process the document based on source type
            if source_type == "file":
                file_path = Path(source)
                if not file_path.exists():
                    raise FileNotFoundError(f"File not found: {file_path}")
                    
                # Check file size (20MB limit)
                file_size = file_path.stat().st_size
                if file_size > 20 * 1024 * 1024:  # 20MB in bytes
                    raise ValueError("File size exceeds 20MB limit")
                
                mime_type, _ = mimetypes.guess_type(str(file_path))
                with open(file_path, 'rb') as f:
                    file_content = f.read()
                    
            elif source_type == "bytes":
                file_content = source
                mime_type = "application/octet-stream"
                
            elif source_type == "text":
                # For text content, we'll use a different Gemini model
                text_model = genai.GenerativeModel('gemini-pro')
                raw_result = await self._process_text_content(source, text_model)
                if metadata:
                    raw_result = self._enhance_with_metadata(raw_result, metadata)
                return self._convert_to_classification_result(raw_result)
                
            else:
                raise ValueError(f"Unsupported source type: {source_type}")
            
            # For file and bytes, process with Gemini Vision
            raw_result = await self._process_binary_content(file_content, mime_type)
            
            # Enhance with metadata if provided
            if metadata:
                raw_result = self._enhance_with_metadata(raw_result, metadata)
                
            return self._convert_to_classification_result(raw_result)
            
        except Exception as e:
            return self._create_error_result(str(e))
            
    async def classify_batch(self, 
                           sources: List[Union[str, Path, bytes]],
                           source_type: str = "file",
                           metadata: Optional[List[Dict]] = None,
                           max_concurrent: int = 5) -> List[ClassificationResult]:
        """Classify multiple documents concurrently."""
        results = []
        metadata_list = metadata or [None] * len(sources)
        
        for i in range(0, len(sources), max_concurrent):
            batch_sources = sources[i:i + max_concurrent]
            batch_metadata = metadata_list[i:i + max_concurrent]
            tasks = [
                self.classify_document(source, source_type, md) 
                for source, md in zip(batch_sources, batch_metadata)
            ]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle any exceptions in the batch
            for result in batch_results:
                if isinstance(result, Exception):
                    results.append(self._create_error_result(str(result)))
                else:
                    results.append(result)
                    
        return results
        
    async def _process_binary_content(self, content: bytes, mime_type: str) -> Dict:
        """Process binary content with Gemini Vision."""
        file_data = base64.b64encode(content).decode('utf-8')
        
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
            "summary": "A brief summary of the document's purpose and content",
            "text": "The full extracted text content from the document"
        }
        
        Please be precise and only include information that is explicitly present in the document.
        If any field has no relevant information, return an empty array or null.
        """
        
        # Process with Gemini
        response = await self.model.generate_content([{
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
            return json.loads(response.text)
        except json.JSONDecodeError:
            raise ValueError("Failed to parse Gemini response as JSON")
            
    async def _process_text_content(self, content: str, model) -> Dict:
        """Process text content with Gemini Pro."""
        prompt = f"""
        Please analyze this text and extract the following information in JSON format:
        {{
            "document_type": "The type of regulatory document (e.g., registration, renewal, tonnage report)",
            "entities": {{
                "companies": ["List of company names mentioned"],
                "products": ["List of product names/types mentioned"],
                "states": ["List of US states mentioned"]
            }},
            "key_fields": {{
                "dates": ["Any important dates mentioned"],
                "registration_numbers": ["Any registration or license numbers"],
                "amounts": ["Any monetary amounts or quantities"]
            }},
            "summary": "A brief summary of the text's purpose and content",
            "text": {json.dumps(content)}
        }}
        
        Please be precise and only include information that is explicitly present in the text.
        If any field has no relevant information, return an empty array or null.
        """
        
        response = await model.generate_content(prompt)
        
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            raise ValueError("Failed to parse Gemini response as JSON")
            
    def _enhance_with_metadata(self, raw_result: Dict, metadata: Dict) -> Dict:
        """Enhance classification results with provided metadata."""
        # Add metadata to existing result
        if "metadata" not in raw_result:
            raw_result["metadata"] = {}
        raw_result["metadata"]["source_metadata"] = metadata
        
        # If we have email metadata, use it to improve classification
        if "email_subject" in metadata:
            # Try to extract additional entities from subject
            subject_entities = self._extract_entities_from_text(metadata["email_subject"])
            raw_result["entities"]["companies"].extend(subject_entities.get("companies", []))
            raw_result["entities"]["states"].extend(subject_entities.get("states", []))
            
        return raw_result
        
    def _extract_entities_from_text(self, text: str) -> Dict[str, List[str]]:
        """Extract entities from a text string."""
        return {
            "companies": [match[1] for match in self.domain_config.get_company_codes(text)],
            "states": self.domain_config.get_states(text)
        }
        
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
        doc_text = raw_result.get('text', '')
        
        # Use domain config to validate and enhance the classification
        doc_type, base_type = self.domain_config.get_document_type(doc_text)
        if not doc_type:
            doc_type = raw_result.get('document_type')
        
        # Get domain-validated states
        states = self.domain_config.get_states(doc_text)
        
        # Get company codes and names
        company_matches = self.domain_config.get_company_codes(doc_text)
        companies = raw_result.get('entities', {}).get('companies', [])
        company_codes = []
        if company_matches:
            # Add any missing companies from raw results
            companies.extend(match[1] for match in company_matches 
                           if match[1] not in companies)
            # Get the codes
            company_codes = [match[0] for match in company_matches]
        
        # Build entities dict
        entities = raw_result.get('entities', {'companies': [], 'products': [], 'states': []})
        entities['companies'] = companies
        entities['states'] = states
        
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
            'related_document_types': self.domain_config.get_related_documents(doc_type) if doc_type else [],
            'base_type': base_type,  # Add the standardized base type
            'company_codes': company_codes  # Add the standardized company codes
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