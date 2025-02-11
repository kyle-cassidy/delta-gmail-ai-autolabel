"""
Classification API Routes

Provides endpoints for document classification using configurable classifiers.
"""
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from typing import Dict, List
import tempfile
import os
from pathlib import Path

from ...classifiers.base import BaseDocumentClassifier, ClassificationResult
from ...classifiers.factory import ClassifierFactory
from ...config.classifier_config import ClassifierConfig

router = APIRouter(prefix="/classify", tags=["classification"])

async def get_config() -> ClassifierConfig:
    """Get the current classifier configuration."""
    return ClassifierConfig()

async def get_classifier(config: ClassifierConfig = Depends(get_config)) -> BaseDocumentClassifier:
    """
    Dependency to get the configured classifier instance.
    
    Args:
        config: Classifier configuration settings
        
    Returns:
        Configured classifier instance
    """
    try:
        return ClassifierFactory.create_classifier(
            config.classifier_type,
            **config.get_classifier_kwargs()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initialize classifier: {str(e)}"
        )

@router.post("/", response_model=ClassificationResult)
async def classify_document(
    file: UploadFile = File(...),
    classifier: BaseDocumentClassifier = Depends(get_classifier),
    config: ClassifierConfig = Depends(get_config)
):
    """
    Classify a single document.
    
    Args:
        file: The document file to classify
        classifier: Document classifier implementation
        config: Classifier configuration
        
    Returns:
        ClassificationResult containing the document analysis
    """
    try:
        # Create a temporary file to store the upload
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name
        
        try:
            # Classify the document
            result = await classifier.classify_document(temp_path)
            return result
        finally:
            # Clean up temp file
            os.unlink(temp_path)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch/", response_model=List[ClassificationResult])
async def classify_documents(
    files: List[UploadFile] = File(...),
    classifier: BaseDocumentClassifier = Depends(get_classifier),
    config: ClassifierConfig = Depends(get_config)
):
    """
    Classify multiple documents in batch.
    
    Args:
        files: List of document files to classify
        classifier: Document classifier implementation
        config: Classifier configuration
        
    Returns:
        List of ClassificationResults
    """
    temp_files = []
    try:
        # Create temporary files for all uploads
        for file in files:
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_files.append(temp_file.name)
        
        # Classify all documents
        results = await classifier.classify_batch(
            temp_files,
            max_concurrent=config.max_concurrent_requests
        )
        return results
    
    finally:
        # Clean up all temp files
        for temp_path in temp_files:
            try:
                os.unlink(temp_path)
            except:
                pass

@router.get("/info/current")
async def get_current_classifier_info(
    classifier: BaseDocumentClassifier = Depends(get_classifier)
) -> Dict:
    """
    Get information about the current classifier implementation.
    
    Returns:
        Dictionary with current classifier metadata
    """
    return classifier.get_classifier_info()

@router.get("/info/available")
async def list_available_classifiers() -> Dict[str, str]:
    """
    List all available classifier implementations.
    
    Returns:
        Dictionary mapping classifier names to their descriptions
    """
    return ClassifierFactory.list_available_classifiers()

@router.get("/config")
async def get_current_config(
    config: ClassifierConfig = Depends(get_config)
) -> Dict:
    """
    Get current classifier configuration.
    
    Returns:
        Dictionary of current configuration settings
    """
    return config.dict(exclude_none=True) 