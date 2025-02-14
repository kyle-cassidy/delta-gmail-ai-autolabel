"""
Classifier Factory

Manages the creation and configuration of document classifiers.
"""

from typing import Dict, Type, Any
from .base import BaseDocumentClassifier
from .gemini import GeminiClassifier
from .docling import DoclingClassifier


class ClassifierFactory:
    """Factory for creating document classifier instances."""

    # Registry of available classifier implementations
    _registry: Dict[str, Type[BaseDocumentClassifier]] = {
        "gemini": GeminiClassifier,
        "docling": DoclingClassifier,
        # Add more implementations as they become available:
        # "openai": OpenAIClassifier,
        # "document_ai": GoogleDocumentAIClassifier,
    }

    @classmethod
    def register_classifier(
        cls, name: str, classifier_class: Type[BaseDocumentClassifier]
    ) -> None:
        """
        Register a new classifier implementation.

        Args:
            name: Identifier for the classifier
            classifier_class: The classifier class to register
        """
        if not issubclass(classifier_class, BaseDocumentClassifier):
            raise ValueError(f"Classifier must implement BaseDocumentClassifier")
        cls._registry[name] = classifier_class

    @classmethod
    def create_classifier(
        cls, name: str, **kwargs: dict[str, Any]
    ) -> BaseDocumentClassifier:
        """
        Create an instance of the specified classifier.

        Args:
            name: Name of the classifier to create
            **kwargs: Configuration parameters for the classifier

        Returns:
            Configured classifier instance

        Raises:
            ValueError: If classifier name is not registered
        """
        if name not in cls._registry:
            raise ValueError(
                f"Unknown classifier: {name}. "
                f"Available classifiers: {list(cls._registry.keys())}"
            )

        classifier_class = cls._registry[name]
        return classifier_class(**kwargs)

    @classmethod
    def list_available_classifiers(cls) -> Dict[str, str]:
        """
        Get information about available classifier implementations.

        Returns:
            Dictionary mapping classifier names to their descriptions
        """
        info = {}
        for name, classifier_class in cls._registry.items():
            # Create a temporary instance to get info
            try:
                instance = classifier_class()
                info[name] = instance.get_classifier_info()["description"]
            except Exception as e:
                info[name] = f"(Configuration required) {str(e)}"
        return info
