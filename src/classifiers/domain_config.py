"""
Domain Configuration Loader

Loads and manages domain-specific configuration from YAML files.
"""
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import yaml
import re
from src.utils.version_checker import VersionChecker
import logging

logger = logging.getLogger(__name__)

class DomainConfig:
    """Manages domain-specific configuration for document classification."""
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize domain configuration.
        
        Args:
            config_dir: Optional path to configuration directory
        """
        self.config_dir = config_dir or Path("config")
        
        # Initialize version checker
        self.version_checker = VersionChecker(self.config_dir)
        
        # Check config compatibility
        warnings = self.version_checker.check_compatibility()
        for warning in warnings:
            logger.warning(warning)
            
        # Load configurations
        self.regulatory_actions = self._load_yaml("regulatory_actions.yaml")
        self.product_categories = self._load_yaml("product_categories.yaml")
        self.state_specific = self._load_yaml("state_specific.yaml")
        self.validation_rules = self._load_yaml("validation_rules.yaml")
        self.relationships = self._load_yaml("relationships.yaml")
        self.state_patterns = self._load_yaml("state_patterns.yaml")
        self.company_codes = self._load_yaml("company_codes.yaml")
        self.document_types = self._load_yaml("document_types.yaml")
        
        # Check for required migrations
        self._check_migrations()
        
        # Compile regex patterns
        self._compile_patterns()
        
    def _load_yaml(self, filename: str) -> Dict:
        """Load YAML configuration file."""
        try:
            with open(self.config_dir / filename) as f:
                config = yaml.safe_load(f) or {}
                
            # Check if migration is needed
            config_name = filename.replace(".yaml", "")
            if self.version_checker.needs_migration(config_name):
                migrations = self.version_checker.get_required_migrations(config_name)
                logger.warning(
                    f"Config {filename} needs migration. Required steps: {migrations}"
                )
                
            return config
        except FileNotFoundError:
            return {}
            
    def _check_migrations(self) -> None:
        """Check if any config files need migration."""
        for config_name in [
            "regulatory_actions",
            "product_categories",
            "document_types",
            "company_codes",
            "state_patterns"
        ]:
            if self.version_checker.needs_migration(config_name):
                migrations = self.version_checker.get_required_migrations(config_name)
                logger.warning(
                    f"Config {config_name} needs migration. Steps: {migrations}"
                )
            
    def _compile_patterns(self) -> None:
        """Compile regex patterns from configurations."""
        self.patterns = {
            "document_types": {},
            "products": {},
            "states": {},
            "companies": {}
        }
        
        # Compile patterns for document types from document_types.yaml
        for doc_type_id, doc_type in self.document_types.get("document_types", {}).items():
            if "patterns" in doc_type:
                for pattern in doc_type["patterns"]:
                    self.patterns["document_types"][doc_type_id] = re.compile(
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
        
        # Compile company name patterns
        for code, company in self.company_codes.get("companies", {}).items():
            # Create pattern from company name and aliases
            name_patterns = [re.escape(company["name"])] + [
                re.escape(alias) for alias in company.get("aliases", [])
            ]
            pattern = "|".join(name_patterns)
            self.patterns["companies"][code] = re.compile(
                f"(?i)\\b({pattern})\\b"
            )
    
    def get_document_type(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Determine document type based on configured patterns.
        
        Args:
            text: Document text to analyze
            
        Returns:
            Tuple of (canonical_name, base_type) if found, else (None, None)
        """
        for doc_type_id, pattern in self.patterns["document_types"].items():
            if pattern.search(text):
                doc_type = self.document_types["document_types"][doc_type_id]
                return doc_type["canonical_name"], doc_type["base_type"]
        return None, None
    
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
    
    def get_company_codes(self, text: str) -> List[Tuple[str, str]]:
        """
        Extract company codes based on configured patterns.
        
        Args:
            text: Document text to analyze
            
        Returns:
            List of tuples (company_code, matched_name)
        """
        matches = []
        for code, pattern in self.patterns["companies"].items():
            match = pattern.search(text)
            if match:
                matches.append((code, match.group(0)))
        return matches
    
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