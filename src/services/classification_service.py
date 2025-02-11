"""
ClassificationService: Manages email and document classification.

Responsibilities:
- Provides a unified interface for classifying both email messages and standalone documents.

- Email categorization by type:
    - Client Code: ARB, BIN, etc.
    - State Regulator: CA, NY, etc.
    - Type: 
        - Certificates:
            - Approval
            - Certificate Document (PDF vs go to portal)
        - Notifications:
            - Payment (Confirmation, Received, Failed, Overdue, Paid)
        - Renewal Reminder

- Certificate classification
- Priority determination
- Routing rule implementation
- Machine learning model integration
- Classification accuracy tracking
"""
from typing import Dict, List, Optional, Union
from pathlib import Path
import asyncio
from email.message import Message
from ..classifiers import ClassifierFactory, ClassificationResult
from ..client.attachment import extract_text_from_attachment

class ClassificationService:
    """Service for classifying documents and emails."""
    
    def __init__(self, config_dir: Optional[Path] = None, classifier_name: str = "docling"):
        """
        Initialize the classification service.
        
        Args:
            config_dir: Optional path to configuration directory
            classifier_name: Name of the classifier to use ("docling" or "gemini")
        """
        self.config_dir = config_dir or Path("config")
        self.classifier = ClassifierFactory.create_classifier(
            classifier_name, config_dir=self.config_dir
        )
        
    async def classify_email(self, 
                           email_message: Message,
                           extract_attachments: bool = True) -> List[ClassificationResult]:
        """
        Classify an email message and its attachments.
        
        Args:
            email_message: Email message to classify
            extract_attachments: Whether to extract and classify attachments
            
        Returns:
            List of classification results (one for email body, plus one per attachment)
        """
        results = []
        
        # Extract email metadata
        metadata = {
            "email_subject": email_message["subject"],
            "email_from": email_message["from"],
            "email_date": email_message["date"],
            "message_id": email_message["message-id"]
        }
        
        # Classify email body
        if email_message.is_multipart():
            body = ""
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    body += part.get_payload(decode=True).decode()
        else:
            body = email_message.get_payload(decode=True).decode()
            
        if body.strip():
            body_result = await self.classifier.classify_document(
                body, source_type="text", metadata=metadata
            )
            results.append(body_result)
            
        # Process attachments if requested
        if extract_attachments:
            for part in email_message.walk():
                if part.get_content_maintype() == "application":
                    filename = part.get_filename()
                    if filename:
                        content = part.get_payload(decode=True)
                        attachment_result = await self.classifier.classify_document(
                            content, 
                            source_type="bytes",
                            metadata={**metadata, "filename": filename}
                        )
                        results.append(attachment_result)
                        
        return results
        
    async def classify_document(self,
                              source: Union[str, Path, bytes],
                              source_type: str = "file",
                              metadata: Optional[Dict] = None) -> ClassificationResult:
        """
        Classify a single document.
        
        Args:
            source: Document source (file path, bytes, or text content)
            source_type: Type of the source ("file", "bytes", or "text")
            metadata: Optional metadata about the document
            
        Returns:
            Classification result
        """
        return await self.classifier.classify_document(source, source_type, metadata)
        
    async def classify_batch(self,
                           sources: List[Union[str, Path, bytes]],
                           source_type: str = "file",
                           metadata: Optional[List[Dict]] = None,
                           max_concurrent: int = 5) -> List[ClassificationResult]:
        """
        Classify multiple documents.
        
        Args:
            sources: List of document sources
            source_type: Type of the sources
            metadata: Optional list of metadata dicts
            max_concurrent: Maximum concurrent classifications
            
        Returns:
            List of classification results
        """
        return await self.classifier.classify_batch(
            sources, source_type, metadata, max_concurrent
        )
        
    async def watch_directory(self,
                            directory: Union[str, Path],
                            pattern: str = "*.*",
                            recursive: bool = False) -> None:
        """
        Watch a directory for new documents and classify them.
        
        Args:
            directory: Directory to watch
            pattern: Glob pattern for files to watch
            recursive: Whether to watch subdirectories
        """
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
        
        class DocumentHandler(FileSystemEventHandler):
            def __init__(self, service):
                self.service = service
                
            async def process_file(self, path):
                try:
                    result = await self.service.classify_document(path)
                    # Handle the classification result (e.g., rename file, move to processed folder)
                    print(f"Classified {path}: {result.document_type}")
                except Exception as e:
                    print(f"Error processing {path}: {e}")
                    
            def on_created(self, event):
                if not event.is_directory:
                    asyncio.create_task(self.process_file(event.src_path))
                    
        path = Path(directory)
        event_handler = DocumentHandler(self)
        observer = Observer()
        observer.schedule(event_handler, str(path), recursive=recursive)
        observer.start()
        
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
