"""Mock Docling package for testing."""
from typing import List, Dict, Any

class DocProcessor:
    """Mock DocProcessor class."""
    
    def __init__(self, model_path=None):
        self.model_path = model_path
    
    def process_document(self, file_path):
        """Mock document processing."""
        return MockDocument()

class TableFormer:
    """Mock TableFormer class."""
    
    def extract_tables(self, doc):
        """Mock table extraction."""
        return []

class MockDocument:
    """Mock Document class."""
    
    def get_text(self) -> str:
        return "Test document for registration in California"
    
    def extract_entities(self, entity_type: str) -> List[str]:
        entities = {
            "ORG": ["Test Corp"],
            "PRODUCT": ["Test Product"]
        }
        return entities.get(entity_type, [])
    
    def extract_dates(self) -> List[str]:
        return ["2024-02-11"]
    
    def extract_patterns(self, pattern: str) -> List[str]:
        patterns = {
            r"REG-?\d+|LIC-?\d+": ["REG-12345"],
            r"\$?\d+(?:,\d{3})*(?:\.\d{2})?": ["$1000.00"]
        }
        return patterns.get(pattern, [])
    
    @property
    def page_count(self) -> int:
        return 1
    
    @property
    def has_tables(self) -> bool:
        return False
    
    @property
    def extraction_confidence(self) -> float:
        return 0.95
    
    def get_summary(self) -> str:
        return "Test document summary" 