"""
Domain Configuration Loader

Loads and manages domain-specific configuration from YAML files.
"""
from typing import Dict, List, Optional
from pathlib import Path
import yaml
import re

class DomainConfig:
    """Manages domain-specific configuration for document classification."""
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize domain configuration.
        
        Args:
            config_dir: Optional path to configuration directory
        """
        self.config_dir = config_dir or Path("config")
        
        # Load configurations
        self.regulatory_actions = self._load_yaml("regulatory_actions.yaml")
        self.product_categories = self._load_yaml("product_categories.yaml")
        self.state_specific = self._load_yaml("state_specific.yaml")
        self.validation_rules = self._load_yaml("validation_rules.yaml")
        self.relationships = self._load_yaml("relationships.yaml")
        self.state_patterns = self._load_yaml("state_patterns.yaml")
        
        # Compile regex patterns
        self._compile_patterns()
        
    def _load_yaml(self, filename: str) -> Dict:
        """Load YAML configuration file."""
        try:
            with open(self.config_dir / filename) as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            return {}
            
    def _compile_patterns(self) -> None:
        """Compile regex patterns from configurations."""
        self.patterns = {
            "document_types": {},
            "products": {},
            "states": {},
        }
        
        # Compile patterns for document types
        for action in self.regulatory_actions.get("regulatory_actions", {}).values():
            if "patterns" in action:
                for pattern in action["patterns"]:
                    self.patterns["document_types"][action["canonical_name"]] = re.compile(
                        pattern["regex"], re.IGNORECASE
                    )
                    
        # Compile patterns for products
        for category in self.product_categories.get("product_categories", {}).values():
            if "patterns" in category:
                for pattern in category["patterns"]:
                    self.patterns["products"][category["canonical_name"]] = re.compile(
                        pattern["regex"], re.IGNORECASE
                    )
                    
        # Compile state patterns from state_patterns.yaml
        for state_code, state_info in self.state_patterns.get("states", {}).items():
            if "patterns" in state_info:
                for pattern in state_info["patterns"]:
                    self.patterns["states"][state_code] = re.compile(
                        pattern["regex"], re.IGNORECASE
                    )
    
    def get_document_type(self, text: str) -> Optional[str]:
        """
        Determine document type based on configured patterns.
        
        Args:
            text: Document text to analyze
            
        Returns:
            Canonical document type name if found
        """
        for doc_type, pattern in self.patterns["document_types"].items():
            if pattern.search(text):
                return doc_type
        return None
    
    def get_product_categories(self, text: str) -> List[str]:
        """
        Extract product categories based on configured patterns.
        
        Args:
            text: Document text to analyze
            
        Returns:
            List of canonical product category names
        """
        categories = []
        for category, pattern in self.patterns["products"].items():
            if pattern.search(text):
                categories.append(category)
        return categories
    
    def get_states(self, text: str) -> List[str]:
        """
        Extract state references based on configured patterns.
        
        Args:
            text: Document text to analyze
            
        Returns:
            List of state codes
        """
        states = []
        for state_code, pattern in self.patterns["states"].items():
            if pattern.search(text):
                states.append(state_code)
        return states
    
    def validate_registration_number(self, number: str, state: str) -> bool:
        """
        Validate a registration number against state-specific rules.
        
        Args:
            number: Registration number to validate
            state: State code
            
        Returns:
            Whether the number is valid for the state
        """
        rules = self.validation_rules.get("registration_numbers", {}).get(state, {})
        if not rules or "pattern" not in rules:
            return True  # No validation rule defined
            
        pattern = re.compile(rules["pattern"])
        return bool(pattern.match(number))
    
    def get_related_documents(self, doc_type: str) -> List[str]:
        """
        Get related document types based on relationships config.
        
        Args:
            doc_type: Document type to find relationships for
            
        Returns:
            List of related document types
        """
        relationships = self.relationships.get("document_relationships", {})
        return relationships.get(doc_type, []) 