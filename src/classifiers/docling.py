"""
Docling Document Classifier Implementation

Uses IBM's open-source Docling library for high-fidelity document parsing and classification.
Runs locally and preserves document structure.
"""

from typing import Dict, List, Optional, Union, Tuple, Any, Callable, cast
from pathlib import Path
import asyncio
import json
import io
from .docling_impl import (
    DocProcessor,
    TableFormer,
    Document,
)  # Import Document class too
from .base import BaseDocumentClassifier, ClassificationResult
from .domain_config import DomainConfig


class DoclingClassifier(BaseDocumentClassifier):
    """Document classifier using IBM's Docling library."""

    def __init__(
        self, model_path: Optional[str] = None, config_dir: Optional[Path] = None
    ):
        """
        Initialize the Docling classifier.

        Args:
            model_path: Optional path to custom model weights
            config_dir: Optional path to configuration directory
        """
        # Initialize Docling components
        self.processor = DocProcessor(model_path=model_path)
        self.table_extractor = TableFormer()

        # Load domain configuration
        self.domain_config = DomainConfig(config_dir or Path("src/config"))

    async def classify_document(
        self,
        source: Union[str, Path, bytes],
        source_type: str = "file",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ClassificationResult:
        """Classify a single document using Docling."""
        try:
            # Process the document based on source type
            if source_type == "file":
                file_path = Path(str(source))  # Convert to string first
                if not file_path.exists():
                    raise FileNotFoundError(f"File not found: {file_path}")
                doc_result = await asyncio.get_event_loop().run_in_executor(
                    None, lambda x: self._process_document(x), file_path
                )
            elif source_type == "bytes":
                # Process bytes directly
                doc_result = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda x: self._process_bytes(cast(bytes, x)),  # Cast to bytes
                    source,
                )
            elif source_type == "text":
                # Process text content directly
                doc_result = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda x: self._process_text(cast(str, x)),  # Cast to str
                    source,
                )
            else:
                raise ValueError(f"Unsupported source type: {source_type}")

            # Enhance classification with metadata if provided
            if metadata:
                doc_result = self._enhance_with_metadata(doc_result, metadata)

            # Convert Docling output to our standard format
            return self._convert_to_classification_result(doc_result)

        except Exception as e:
            return self._create_error_result(str(e))

    async def classify_batch(
        self,
        sources: List[Union[str, Path, bytes]],
        source_type: str = "file",
        metadata: Optional[List[Dict[str, Any]]] = None,
        max_concurrent: int = 5,
    ) -> List[ClassificationResult]:
        """Classify multiple documents concurrently."""
        results: List[ClassificationResult] = []
        metadata_list = metadata if metadata is not None else [{} for _ in sources]

        for i in range(0, len(sources), max_concurrent):
            batch_sources = sources[i : i + max_concurrent]
            batch_metadata = metadata_list[i : i + max_concurrent]
            tasks = [
                self.classify_document(source, source_type, md)
                for source, md in zip(batch_sources, batch_metadata)
            ]
            batch_results = await asyncio.gather(*tasks)
            results.extend(batch_results)

        return results

    def _process_bytes(self, content: bytes) -> Dict[str, Any]:
        """Process document from bytes."""
        # Create a file-like object from bytes
        file_obj = io.BytesIO(content)
        doc = self.processor.process_file_object(file_obj)
        return self._extract_document_info(doc)

    def _process_text(self, content: str) -> Dict[str, Any]:
        """Process document from text content."""
        doc = self.processor.process_text(content)
        return self._extract_document_info(doc)

    def _process_document(self, file_path: Path) -> Dict[str, Any]:
        """Process document from file path."""
        doc = self.processor.process_document(file_path)
        return self._extract_document_info(doc)

    def _extract_document_info(self, doc: Document) -> Dict[str, Any]:
        """Extract common document information."""
        # Get document text for pattern matching
        doc_text = doc.get_text()

        # Extract tables if present
        tables = []
        if doc.has_tables:
            tables = self.table_extractor.extract_tables(doc)

        # Use domain configuration to extract entities and information
        entities = self._extract_entities(doc, doc_text)
        key_fields = self._extract_key_fields(doc)

        # Determine document type using domain patterns
        doc_type, base_type = self.domain_config.get_document_type(doc_text)

        # Get related document types
        related_types = (
            self.domain_config.get_related_documents(doc_type) if doc_type else []
        )

        return {
            "document_type": doc_type,
            "base_type": base_type,
            "entities": entities,
            "key_fields": key_fields,
            "tables": tables,
            "summary": doc.get_summary(),
            "metadata": {
                "page_count": doc.page_count,
                "has_tables": bool(tables),
                "confidence": doc.extraction_confidence,
                "related_document_types": related_types,
                "product_categories": self.domain_config.get_product_categories(
                    doc_text
                ),
            },
        }

    def _enhance_with_metadata(
        self, doc_result: Dict[str, Any], metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enhance classification results with provided metadata."""
        # Add metadata to existing result
        doc_result["metadata"].update({"source_metadata": metadata})

        # If we have email metadata, use it to improve classification
        if "email_subject" in metadata:
            # Try to extract additional entities from subject
            subject_entities = self._extract_entities_from_text(
                metadata["email_subject"]
            )
            # Ensure unique companies and states
            doc_result["entities"]["companies"] = list(
                set(
                    doc_result["entities"]["companies"]
                    + subject_entities.get("companies", [])
                )
            )
            doc_result["entities"]["states"] = list(
                set(
                    doc_result["entities"]["states"]
                    + subject_entities.get("states", [])
                )
            )

        return doc_result

    def _extract_entities_from_text(self, text: str) -> Dict[str, List[str]]:
        """Extract entities from a text string."""
        return {
            "companies": [
                match[1] for match in self.domain_config.get_company_codes(text)
            ],
            "states": self.domain_config.get_states(text),
        }

    def get_classifier_info(self) -> Dict[str, Any]:
        """Get information about this classifier implementation."""
        return {
            "name": "Docling Classifier",
            "version": "1.0.0",
            "description": "Uses IBM's Docling library for high-fidelity local document processing",
            "provider": "IBM (Open Source)",
            "features": ", ".join(
                [
                    "Local processing (no data leaves your system)",
                    "High-accuracy layout preservation",
                    "Superior table extraction via TableFormer",
                    "No API costs or rate limits",
                    "Domain-aware classification using regulatory configurations",
                ]
            ),
        }

    def _extract_entities(self, doc: Document, doc_text: str) -> Dict[str, List[str]]:
        """Extract entities using both Docling and domain configuration."""
        # Get entities from Docling
        companies = doc.extract_entities(entity_type="ORG")
        products = doc.extract_entities(entity_type="PRODUCT")

        # Get states from domain configuration
        states = self.domain_config.get_states(doc_text)

        return {"companies": companies, "products": products, "states": states}

    def _extract_key_fields(self, doc: Document) -> Dict[str, List[str]]:
        """Extract and validate key fields."""
        # Extract basic fields
        dates = doc.extract_dates()
        registration_numbers = doc.extract_patterns(r"REG-?\d+|LIC-?\d+")
        amounts = doc.extract_patterns(r"\$?\d+(?:,\d{3})*(?:\.\d{2})?")

        # Validate registration numbers against state-specific rules
        doc_text = doc.get_text()
        states = self.domain_config.get_states(doc_text)

        valid_numbers = []
        for number in registration_numbers:
            # If we have state context, validate against state rules
            if states:
                if any(
                    self.domain_config.validate_registration_number(number, state)
                    for state in states
                ):
                    valid_numbers.append(number)
            else:
                # If no state context, include all numbers
                valid_numbers.append(number)

        return {
            "dates": dates,
            "registration_numbers": valid_numbers,
            "amounts": amounts,
        }

    def _identify_client(
        self, doc_text: str, companies: List[str]
    ) -> Tuple[Optional[str], float]:
        """
        Identify client code from document text and extracted companies.

        Returns:
            Tuple of (client_code, confidence)
        """
        # Check against known client patterns
        client_matches = []

        # Use _load_client_patterns instead of get_client_patterns
        for code, patterns in self.domain_config._load_client_patterns().items():
            for pattern in patterns:
                if pattern.search(doc_text):
                    client_matches.append((code, 0.9))

        # Check extracted company names against client database
        for company in companies:
            if client_code := self.domain_config.get_client_by_company(company):
                client_matches.append((client_code, 0.8))

        if not client_matches:
            return None, 0.0

        # Return highest confidence match
        return max(client_matches, key=lambda x: x[1])

    def _convert_to_classification_result(
        self, raw_result: Dict[str, Any]
    ) -> ClassificationResult:
        """Convert Docling output to standardized ClassificationResult."""
        # Calculate confidence based on Docling's metrics and domain validation
        base_confidence = raw_result.get("metadata", {}).get("confidence", 0.0)
        domain_confidence = self._calculate_domain_confidence(raw_result)
        confidence = (base_confidence + domain_confidence) / 2

        # Generate any warning flags
        flags = self._generate_flags(raw_result, confidence)

        # Create metadata
        metadata = {
            **raw_result.get("metadata", {}),
            "classifier": self.get_classifier_info()["name"],
            "domain_confidence": domain_confidence,
        }

        # Identify client
        client_code, client_confidence = self._identify_client(
            raw_result.get("summary", ""),
            raw_result.get("entities", {}).get("companies", []),
        )

        # Construct the result
        return ClassificationResult(
            document_type=raw_result.get("document_type"),
            client_code=client_code,
            confidence=min(confidence, client_confidence),
            entities=raw_result.get("entities", {}),
            key_fields=raw_result.get("key_fields", {}),
            metadata=metadata,
            summary=raw_result.get("summary"),
            flags=flags,
        )

    def _calculate_domain_confidence(self, result: Dict[str, Any]) -> float:
        """Calculate confidence based on domain validation."""
        score = 0.0
        total_checks = 0

        # Check document type against known types
        if result.get("document_type"):
            score += 1
            total_checks += 1

        # Check if found states are valid
        if result.get("entities", {}).get("states"):
            score += 1
            total_checks += 1

        # Check if found product categories match our domain
        if result.get("metadata", {}).get("product_categories"):
            score += 1
            total_checks += 1

        # Check registration number validation
        if result.get("key_fields", {}).get("registration_numbers"):
            score += 1
            total_checks += 1

        return round(score / total_checks, 2) if total_checks > 0 else 0.0

    def _generate_flags(self, result: Dict[str, Any], confidence: float) -> List[str]:
        """Generate warning flags based on classification results."""
        flags = []

        # Check confidence
        if confidence < 0.5:
            flags.append("LOW_CONFIDENCE")

        # Check for missing critical information
        if not result.get("document_type"):
            flags.append("MISSING_DOCUMENT_TYPE")

        # Check entities
        if not any(result.get("entities", {}).values()):
            flags.append("NO_ENTITIES_FOUND")

        # Check key fields
        key_fields = result.get("key_fields", {})
        if not key_fields.get("dates"):
            flags.append("NO_DATES_FOUND")
        if not key_fields.get("registration_numbers"):
            flags.append("NO_REGISTRATION_NUMBERS")

        # Add domain-specific flags
        if not result.get("metadata", {}).get("product_categories"):
            flags.append("NO_PRODUCT_CATEGORY_MATCH")

        return flags

    def _create_error_result(self, error_message: str) -> ClassificationResult:
        """Create a ClassificationResult for error cases."""
        return ClassificationResult(
            document_type=None,
            client_code=None,  # Add missing required parameter
            confidence=0.0,
            entities={"companies": [], "products": [], "states": []},
            key_fields={"dates": [], "registration_numbers": [], "amounts": []},
            metadata={
                "error": error_message,
                "classifier": self.get_classifier_info()["name"],
            },
            summary=None,
            flags=["CLASSIFICATION_ERROR"],
        )
