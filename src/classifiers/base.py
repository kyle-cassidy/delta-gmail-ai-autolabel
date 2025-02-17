"""
Base Classifier Interface

This module defines the base interface that all document classifiers must implement.
Supports hot-swapping of different classification implementations.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Union, Optional
from pathlib import Path
from pydantic import BaseModel

class ClassificationResult(BaseModel):
    """Standardized classification result model."""
    document_type: str | None
    client_code: str | None
    confidence: float
    entities: Dict[str, List[str]]
    key_fields: Dict[str, List[str]]
    metadata: Dict[str, Union[bool, int, float, str, List[str]]]
    summary: str | None
    flags: List[str]

class BaseDocumentClassifier(ABC):
    """Abstract base class for document classifiers."""
    
    @abstractmethod
    async def classify_document(self, 
                              source: Union[str, Path, bytes], 
                              source_type: str = "file",
                              metadata: Optional[Dict] = None) -> ClassificationResult:
        """
        Classify a single document from various sources.
        
        Args:
            source: The document source, which can be:
                   - A file path (str or Path) when source_type is "file"
                   - Raw document bytes when source_type is "bytes"
                   - Document text content when source_type is "text"
            source_type: Type of the source ("file", "bytes", or "text")
            metadata: Optional metadata about the source (e.g., email subject, sender)
            
        Returns:
            ClassificationResult containing the classification details
        """
        pass
    
    @abstractmethod
    async def classify_batch(self, 
                           sources: List[Union[str, Path, bytes]],
                           source_type: str = "file",
                           metadata: Optional[List[Dict]] = None,
                           max_concurrent: int = 5) -> List[ClassificationResult]:
        """
        Classify multiple documents from various sources.
        
        Args:
            sources: List of document sources (paths, bytes, or text)
            source_type: Type of the sources ("file", "bytes", or "text")
            metadata: Optional list of metadata dicts for each source
            max_concurrent: Maximum number of concurrent classifications
            
        Returns:
            List of ClassificationResults
        """
        pass
    
    @abstractmethod
    def get_classifier_info(self) -> Dict[str, str]:
        """
        Get information about the classifier implementation.
        
        Returns:
            Dictionary containing classifier metadata like:
            - name: Name of the classifier
            - version: Version of the classifier
            - description: Brief description of how it works
        """
        pass 