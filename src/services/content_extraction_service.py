"""
Content Extraction Service using Google's Gemini Flash
"""
import os
from typing import Dict, List, Optional, Union
import google.generativeai as genai
from pathlib import Path
import json

class ContentExtractionService:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Gemini content extraction service."""
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key is required")
        
        # Configure the Gemini API
        genai.configure(api_key=self.api_key)
        # Initialize the model (using Flash for optimal speed/quality balance)
        self.model = genai.GenerativeModel('gemini-pro-vision')
        
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
            with open(file_path, 'rb') as f:
                response = self.model.generate_content([prompt, f])
                
            # Parse and validate the response
            try:
                result = json.loads(response.text)
                return self._validate_extraction(result)
            except json.JSONDecodeError:
                raise ValueError("Failed to parse Gemini response as JSON")
                
        except Exception as e:
            raise Exception(f"Content extraction failed: {str(e)}")
            
    def _validate_extraction(self, result: Dict) -> Dict:
        """Validate and clean up the extraction results."""
        required_keys = ['document_type', 'entities', 'key_fields', 'tables', 'summary']
        
        # Ensure all required keys exist
        for key in required_keys:
            if key not in result:
                result[key] = None
                
        # Ensure nested dictionaries exist
        if result['entities'] is None:
            result['entities'] = {'companies': [], 'products': [], 'states': []}
        if result['key_fields'] is None:
            result['key_fields'] = {'dates': [], 'registration_numbers': [], 'amounts': []}
            
        return result

    async def batch_extract(self, file_paths: List[Union[str, Path]]) -> List[Dict]:
        """
        Process multiple documents in batch.
        
        Args:
            file_paths: List of paths to documents
            
        Returns:
            List of extraction results, one per document
        """
        results = []
        for file_path in file_paths:
            try:
                result = await self.extract_content(file_path)
                results.append({
                    'file_path': str(file_path),
                    'success': True,
                    'data': result
                })
            except Exception as e:
                results.append({
                    'file_path': str(file_path),
                    'success': False,
                    'error': str(e)
                })
        return results
