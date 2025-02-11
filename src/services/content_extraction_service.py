"""
Content Extraction Service using Google's Gemini Flash
"""
import os
from typing import Dict, List, Optional, Union
import google.generativeai as genai
from pathlib import Path
import json
import base64
import mimetypes

class ContentExtractionService:
    def __init__(self, api_key: str):
        """
        Initialize the content extraction service.
        
        Args:
            api_key: The Gemini API key
        """
        if not api_key:
            raise ValueError("API key is required")
            
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro-vision')
        
    def _read_file_as_base64(self, file_path: Path) -> Dict:
        """
        Read a file and convert it to a base64-encoded blob with MIME type.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dict with mime_type and data fields
        """
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if not mime_type:
            mime_type = 'application/octet-stream'
            
        with open(file_path, 'rb') as f:
            data = base64.b64encode(f.read()).decode('utf-8')
            
        return {
            'mime_type': mime_type,
            'data': data
        }
        
    def _validate_extraction(self, result: Dict) -> Dict:
        """
        Validate and initialize missing fields in extraction result.
        
        Args:
            result: The extraction result to validate
            
        Returns:
            Validated result with all required fields
        """
        if not isinstance(result, dict):
            result = {}
            
        # Initialize required top-level fields
        result.setdefault('document_type', None)
        result.setdefault('entities', {})
        result.setdefault('key_fields', {})
        result.setdefault('tables', [])
        result.setdefault('summary', None)
        
        # Initialize nested fields
        result['entities'].setdefault('companies', [])
        result['entities'].setdefault('products', [])
        result['entities'].setdefault('states', [])
        
        result['key_fields'].setdefault('dates', [])
        result['key_fields'].setdefault('registration_numbers', [])
        result['key_fields'].setdefault('amounts', [])
        
        return result
        
    async def extract_content(self, file_path: Union[str, Path]) -> Dict:
        """
        Extract content from a document using Gemini Flash.
        
        Args:
            file_path: Path to the document file (PDF, image, etc.)
            
        Returns:
            Dict containing extracted information including:
            - document_type: The classified type of document
            - entities: Key entities found (companies, products, etc.)
            - key_fields: Important form fields and values
            - tables: Any tabular data found
            - summary: Brief summary of the document
        """
        try:
            # Load the document
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
                
            # Convert file to base64 blob
            file_blob = self._read_file_as_base64(file_path)
                
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
                    {'inline_data': file_blob}
                ]
            }])
            
            # Parse and validate the response
            try:
                result = json.loads(response.text)
                return self._validate_extraction(result)
            except json.JSONDecodeError:
                raise ValueError("Failed to parse Gemini response as JSON")
                
        except Exception as e:
            raise Exception(f"Content extraction failed: {str(e)}")
            
    async def batch_extract(self, file_paths: List[Union[str, Path]]) -> List[Dict]:
        """
        Extract content from multiple documents in batch.
        
        Args:
            file_paths: List of paths to document files
            
        Returns:
            List of dictionaries containing:
            - success: Whether extraction succeeded
            - data: Extracted content if successful
            - error: Error message if failed
        """
        results = []
        for file_path in file_paths:
            try:
                data = await self.extract_content(file_path)
                results.append({
                    'success': True,
                    'data': data,
                    'error': None
                })
            except Exception as e:
                results.append({
                    'success': False,
                    'data': None,
                    'error': str(e)
                })
        return results
