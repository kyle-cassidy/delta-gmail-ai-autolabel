"""
Base Classifier Interface

This module defines the base interface that all document classifiers must implement.
Supports hot-swapping of different classification implementations.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Union
from pathlib import Path
from pydantic import BaseModel

class ClassificationResult(BaseModel):
    """Standardized classification result model."""
    document_type: str | None
    confidence: float
    entities: Dict[str, List[str]]
    key_fields: Dict[str, List[str]]
    metadata: Dict[str, Union[bool, int, float, str, List[str]]]
    summary: str | None
    flags: List[str]

class BaseDocumentClassifier(ABC):
    """Abstract base class for document classifiers."""
    
    @abstractmethod
    async def classify_document(self, file_path: Union[str, Path]) -> ClassificationResult:
        """
        Classify a single document.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            ClassificationResult containing the classification details
        """
        pass
    
    @abstractmethod
    async def classify_batch(self, file_paths: List[Union[str, Path]], 
                           max_concurrent: int = 5) -> List[ClassificationResult]:
        """
        Classify multiple documents.
        
        Args:
            file_paths: List of paths to documents
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