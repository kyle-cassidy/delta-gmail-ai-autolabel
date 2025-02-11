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
        self.company_codes = self._load_yaml("clients.yaml")
        self.document_types = self._load_yaml("document_types.yaml")
        
        # Load and process client data
        self.client_data = self._load_client_patterns()
        
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
        for code, company in self.client_data.items():
            # Create pattern from company name, aliases, and patterns
            patterns = []
            
            # Add company name
            if name := company.get("name"):
                patterns.append(re.escape(name))
                # Add partial name matches (for each word in the name)
                words = name.split()
                if len(words) > 1:  # Only add word patterns if name has multiple words
                    for word in words:
                        if len(word) > 3:  # Only match on words longer than 3 chars
                            patterns.append(re.escape(word))
            
            # Add aliases
            patterns.extend(re.escape(alias) for alias in company.get("aliases", []))
            
            # Add provided patterns
            patterns.extend(pattern for pattern in company.get("patterns", []))
            
            # Add code pattern
            patterns.append(rf"{code}\b")
            
            # Join all patterns with OR
            pattern = "|".join(f"({p})" for p in patterns)
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
    
    def _load_client_patterns(self) -> Dict:
        """Load and compile client patterns."""
        client_patterns_file = self.config_dir / "clients.yaml"
        if not client_patterns_file.exists():
            logger.warning("Client patterns file not found")
            return {}
            
        with open(client_patterns_file) as f:
            config = yaml.safe_load(f)
            
        companies = config.get("companies", {})
        
        # Process each client to add patterns
        for code, data in companies.items():
            # Add standard patterns based on company name and code
            patterns = []
            
            # Add company name pattern
            if name := data.get("name"):
                patterns.append(re.escape(name))  # Exact company name
                
            # Add aliases patterns
            for alias in data.get("aliases", []):
                patterns.append(re.escape(alias))
                
            # Add client code pattern
            patterns.append(rf"{code}\b")  # Code with word boundary
            
            # Add email domain patterns
            for domain in data.get("domains", []):
                patterns.append(rf"@{re.escape(domain)}")
                
            # Store patterns with the client data
            data["patterns"] = patterns
            
        return companies

    def get_client_by_company(self, company_name: str) -> Optional[str]:
        """Get client code by exact company name match."""
        for code, data in self.client_data.items():
            if data.get("name") == company_name:
                return code
        return None
        
    def get_client_by_email_domain(self, email: str) -> Optional[str]:
        """Get client code by email domain."""
        domain = email.split("@")[-1].lower()
        for code, data in self.client_data.items():
            if domain in data.get("domains", []):
                return code
        return None
        
    def _identify_client(self, text: str) -> Tuple[Optional[str], float]:
        """Identify client from text with confidence score.
        
        Args:
            text: Text to analyze
            
        Returns:
            Tuple of (client_code, confidence_score)
        """
        logger.debug(f"Identifying client from text: {text}")
        
        # Check exact company name match first (highest confidence)
        for code, data in self.client_data.items():
            if data.get("name"):
                company_name = data["name"]
                if company_name == text.strip():  # Exact match
                    logger.debug(f"Found exact company name match: {code}")
                    return code, 1.0
                elif company_name in text:  # Contains full name
                    logger.debug(f"Found company name in text: {code}")
                    return code, 0.9
                    
        # Check aliases
        for code, data in self.client_data.items():
            for alias in data.get("aliases", []):
                if alias == text.strip():  # Exact alias match
                    logger.debug(f"Found exact alias match: {code}")
                    return code, 0.95
                elif alias in text:  # Contains alias
                    logger.debug(f"Found alias in text: {code}")
                    return code, 0.85
                    
        # Check email domains
        for code, data in self.client_data.items():
            for domain in data.get("domains", []):
                if f"@{domain}" in text.lower():
                    logger.debug(f"Found email domain match: {code}")
                    return code, 0.95
                    
        # Check code patterns (e.g., "EEA", "ARB")
        for code, data in self.client_data.items():
            if re.search(rf"\b{code}\b", text):
                logger.debug(f"Found code pattern match: {code}")
                return code, 0.8
                
        # Check compiled patterns for partial matches
        logger.debug("Checking compiled patterns:")
        for code, pattern in self.patterns["companies"].items():
            logger.debug(f"Pattern for {code}: {pattern.pattern}")
            if pattern.search(text):
                logger.debug(f"Found pattern match: {code}")
                return code, 0.75
                
        logger.debug("No match found")
        return None, 0.0 