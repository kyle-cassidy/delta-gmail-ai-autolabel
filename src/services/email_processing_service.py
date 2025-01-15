from typing import List, Optional, Dict
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from src.client.gmail import Gmail
from src.client.message import Message

class ProcessingStatus(Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    RETRYING = "RETRYING"

@dataclass
class EmailProcessingState:
    email_id: str
    status: ProcessingStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    retry_count: int = 0
    metadata: Dict = None

class EmailProcessingService:
    """
    EmailProcessingService: Orchestrates the complete email processing pipeline.

    Responsibilities:
    - Coordinates email fetching via Gmail client
    - Manages processing workflow and state
    - Handles retries and failure recovery
    - Routes emails to appropriate services
    - Maintains processing queue
    - Tracks processing status
    """


    def __init__(
        self,
        gmail_client: Gmail,
        security_service,
        content_extraction_service,
        classification_service,
        storage_service,
        notification_service,
        audit_service
    ):
        self.gmail = gmail_client
        self.security = security_service
        self.extractor = content_extraction_service
        self.classifier = classification_service
        self.storage = storage_service
        self.notifier = notification_service
        self.audit = audit_service
        self.processing_queue: Dict[str, EmailProcessingState] = {}

    async def process_new_emails(self) -> List[EmailProcessingState]:
        """Main entry point for processing new emails"""
        try:
            # Get unread messages from inbox
            messages = self.gmail.get_unread_inbox()
            results = []
            
            for message in messages:
                state = await self.process_email(message)
                results.append(state)
            
            return results
            
        except Exception as e:
            await self.notifier.send_error("Batch processing failed", str(e))
            await self.audit.log_error("batch_processing", str(e))
            raise

    async def process_email(self, message: Message) -> EmailProcessingState:
        
        """Process a single email through the pipeline"""
        
        state = EmailProcessingState(
            email_id=message.id,
            status=ProcessingStatus.PROCESSING,
            started_at=datetime.utcnow(),
            metadata={"sender": message.sender, "subject": message.subject}
        )
        self.processing_queue[message.id] = state

        try:
            # Security check
            security_result = await self.security.verify_email(message)
            if not security_result.is_safe:
                state.status = ProcessingStatus.FAILED
                state.error = f"Email failed security verification: {', '.join(security_result.checks_failed)}"
                state.completed_at = datetime.utcnow()
                await self.notifier.send_error(
                    f"Email {message.id} failed security verification",
                    f"Failed checks: {', '.join(security_result.checks_failed)}"
                )
                await self.audit.log_error(
                    message.id,
                    SecurityException(f"Security checks failed: {', '.join(security_result.checks_failed)}")
                )
                return state

            # Extract content
            content = await self.extractor.extract_content(message)
            
            # Classify content
            classification = await self.classifier.classify(content)
            
            # Store results
            await self.storage.store_processed_email(message, content, classification)
            
            # Update state
            state.status = ProcessingStatus.COMPLETED
            state.completed_at = datetime.utcnow()
            
            # Audit success
            await self.audit.log_success(message.id, state)
            
            return state

        except Exception as e:
            state.error = str(e)
            state.completed_at = datetime.utcnow()
            
            await self.notifier.send_error(f"Failed to process email {message.id}", str(e))
            await self.audit.log_error(message.id, e)
            
            # Increment retry count before checking
            state.retry_count += 1
            
            if state.retry_count > 0:  # Already tried once
                state.status = ProcessingStatus.FAILED
                await self.notifier.send_error(
                    f"Email {message.id} failed after {state.retry_count} attempts",
                    f"Final error: {str(e)}"
                )
            else:
                await self._schedule_retry(message)
            
            return state

    async def _schedule_retry(self, message: Message):
        """Schedule a retry for failed message processing"""
        state = self.processing_queue[message.id]
        state.retry_count += 1
        state.status = ProcessingStatus.RETRYING
        state.error = f"Retry attempt {state.retry_count}/3"

    async def get_processing_state(self, email_id: str) -> Optional[EmailProcessingState]:
        """Get current processing state for an email"""
        return self.processing_queue.get(email_id)

# TODO: Sec
class SecurityException(Exception):
    """Raised when an email fails security checks"""
    pass
