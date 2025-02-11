from typing import Any, Dict, Optional
from pydantic import BaseSettings, Field
from pathlib import Path

class ClassifierConfig(BaseSettings):
    """Configuration for document classifiers."""
    
    # General settings
    classifier_type: str = Field(
        default="gemini",
        description="Type of classifier to use (gemini, docling, openai)"
    )
    
    # API keys (optional)
    google_api_key: Optional[str] = Field(
        default=None,
        description="Google API key for Gemini classifier"
    )
    openai_api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key for OpenAI classifier"
    )
    
    # Performance settings
    max_concurrent_requests: int = Field(
        default=5,
        description="Maximum number of concurrent classification requests"
    )
    request_timeout_seconds: int = Field(
        default=30,
        description="Timeout for classification requests in seconds"
    )
    
    # Feature flags
    enable_caching: bool = Field(
        default=True,
        description="Enable caching of classification results"
    )
    debug_mode: bool = Field(
        default=False,
        description="Enable debug logging"
    )
    
    # Docling-specific settings
    docling_model_path: Optional[Path] = Field(
        default=None,
        description="Path to custom Docling model weights"
    )
    docling_use_gpu: bool = Field(
        default=False,
        description="Use GPU acceleration for Docling"
    )
    docling_config_dir: Optional[Path] = Field(
        default=Path("config/domain"),
        description="Path to domain configuration directory"
    )
    docling_batch_size: int = Field(
        default=10,
        description="Batch size for Docling document processing"
    )
    
    class Config:
        env_prefix = "CLASSIFIER_"
        case_sensitive = False
    
    def get_classifier_kwargs(self) -> Dict[str, Any]:
        """Get initialization arguments for the selected classifier."""
        kwargs = {}
        
        if self.classifier_type == "gemini":
            if not self.google_api_key:
                raise ValueError("Google API key required for Gemini classifier")
            kwargs["api_key"] = self.google_api_key
            
        elif self.classifier_type == "openai":
            if not self.openai_api_key:
                raise ValueError("OpenAI API key required for OpenAI classifier")
            kwargs["api_key"] = self.openai_api_key
            
        elif self.classifier_type == "docling":
            if self.docling_model_path:
                kwargs["model_path"] = str(self.docling_model_path)
            kwargs["config_dir"] = self.docling_config_dir
            kwargs["use_gpu"] = self.docling_use_gpu
            kwargs["batch_size"] = self.docling_batch_size
            
        return kwargs 