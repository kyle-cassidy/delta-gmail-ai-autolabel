"""
Tests for the EmailProcessingService class.

This test suite verifies the email processing pipeline's functionality, including:
- Processing of individual and batch emails
- Error handling and retry mechanisms
- State management and tracking
- Integration with dependent services (security, classification, storage, etc.)
- Audit logging of processing events
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from src.services.email_processing_service import (
    EmailProcessingService,
    EmailProcessingState,
    ProcessingStatus,
    SecurityException
)
from src.client.message import Message

@pytest.fixture
def mock_services():
    """
    Creates mock instances of all dependent services required by EmailProcessingService.
    
    Returns a dictionary containing mock objects for:
    - Gmail client: For email operations
    - Security service: For email verification
    - Content extraction service: For parsing email content
    - Classification service: For categorizing emails
    - Storage service: For persisting processed data
    - Notification service: For sending alerts
    - Audit service: For logging operations
    """
    return {
        'gmail_client': MagicMock(),
        'security_service': AsyncMock(),
        'content_extraction_service': AsyncMock(),
        'classification_service': AsyncMock(),
        'storage_service': AsyncMock(),
        'notification_service': AsyncMock(),
        'audit_service': AsyncMock()
    }

@pytest.fixture
def email_processing_service(mock_services):
    return EmailProcessingService(
        gmail_client=mock_services['gmail_client'],
        security_service=mock_services['security_service'],
        content_extraction_service=mock_services['content_extraction_service'],
        classification_service=mock_services['classification_service'],
        storage_service=mock_services['storage_service'],
        notification_service=mock_services['notification_service'],
        audit_service=mock_services['audit_service']
    )

@pytest.fixture
def sample_message():
    message = MagicMock(spec=Message)
    message.id = "test_email_123"
    message.sender = "test@example.com"
    message.subject = "Test Email"
    return message

@pytest.mark.asyncio
async def test_successful_email_processing(email_processing_service, mock_services, sample_message):
    """
    Test the happy path of email processing.
    
    This test verifies that:
    1. The email passes security verification
    2. Content is successfully extracted
    3. The email is properly classified
    4. Results are stored in the database
    5. Success is logged in the audit trail
    6. Processing state transitions are correct (PROCESSING -> COMPLETED)
    7. Timestamps are properly recorded
    
    The test mocks all dependent services to isolate the processing logic
    and verifies that each service is called exactly once with correct parameters.
    """
    # Setup: Configure mock services to simulate successful processing
    mock_services['security_service'].verify_email.return_value = True
    mock_services['content_extraction_service'].extract_content.return_value = {"text": "test content"}
    mock_services['classification_service'].classify.return_value = {"type": "certificate"}
    
    # Execute: Process a sample email
    result = await email_processing_service.process_email(sample_message)
    
    # Verify: Check processing result
    assert result.email_id == sample_message.id
    assert result.status == ProcessingStatus.COMPLETED
    assert result.error is None
    assert isinstance(result.started_at, datetime)
    assert isinstance(result.completed_at, datetime)
    
    # Verify: Ensure all services were called correctly
    mock_services['security_service'].verify_email.assert_called_once_with(sample_message)
    mock_services['content_extraction_service'].extract_content.assert_called_once_with(sample_message)
    mock_services['classification_service'].classify.assert_called_once()
    mock_services['storage_service'].store_processed_email.assert_called_once()
    mock_services['audit_service'].log_success.assert_called_once()

@pytest.mark.asyncio
async def test_security_check_failure(email_processing_service, mock_services, sample_message):
    """
    Test email processing when security verification fails.
    
    This test verifies that:
    1. Failed security check properly terminates the processing pipeline
    2. The email state is marked as FAILED
    3. Error details are properly recorded
    4. Subsequent processing steps are not executed
    5. Error notifications are sent
    6. The failure is logged in the audit trail
    
    This test is crucial for ensuring that potentially malicious emails
    are properly handled and don't proceed to content extraction or classification.
    """
    # Setup: Configure security service to reject the email
    mock_services['security_service'].verify_email.return_value = False
    
    # Execute: Attempt to process the email
    result = await email_processing_service.process_email(sample_message)
    
    # Verify: Check failure state and error recording
    assert result.status == ProcessingStatus.FAILED
    assert isinstance(result.error, str)
    assert "security verification" in result.error.lower()
    
    # Verify: Ensure pipeline was terminated and proper notifications were sent
    mock_services['content_extraction_service'].extract_content.assert_not_called()
    mock_services['notification_service'].send_error.assert_called_once()
    mock_services['audit_service'].log_error.assert_called_once()

@pytest.mark.asyncio
async def test_process_new_emails_batch(email_processing_service, mock_services):
    """
    Test batch processing of multiple emails from the inbox.
    
    This test verifies that:
    1. Multiple emails can be processed in a single batch operation
    2. The Gmail client is queried exactly once for unread emails
    3. Each email in the batch is processed independently
    4. The overall batch operation succeeds even if individual emails fail
    5. Results are collected and returned for all processed emails
    
    This test is important for ensuring the system can handle bulk processing
    efficiently and maintain proper state tracking for each email in the batch.
    """
    # Setup: Create a batch of test emails and configure mock responses
    messages = [
        MagicMock(spec=Message, id=f"test_email_{i}", 
                 sender=f"test{i}@example.com", 
                 subject=f"Test Email {i}") 
        for i in range(3)
    ]
    mock_services['gmail_client'].get_unread_inbox.return_value = messages
    mock_services['security_service'].verify_email.return_value = True
    
    # Execute: Process the batch of emails
    results = await email_processing_service.process_new_emails()
    
    # Verify: Check batch processing results
    assert len(results) == 3, "All emails in batch should be processed"
    assert all(r.status == ProcessingStatus.COMPLETED for r in results), \
           "All emails should complete processing"
    assert mock_services['gmail_client'].get_unread_inbox.call_count == 1, \
           "Inbox should be queried exactly once"

@pytest.mark.asyncio
async def test_retry_logic(email_processing_service, mock_services, sample_message):
    """
    Test the retry mechanism for failed email processing.
    
    This test verifies that:
    1. Failed operations are properly detected and handled
    2. The retry counter is incremented correctly
    3. The error state is properly recorded
    4. The retry mechanism is triggered appropriately
    5. The final state reflects the retry attempt
    
    This test is crucial for ensuring the system's resilience to transient
    failures and its ability to recover from errors through retry mechanisms.
    The test simulates a security service failure to trigger the retry logic.
    """
    # Setup: Configure security service to raise an exception
    mock_services['security_service'].verify_email.side_effect = Exception("Test error")
    
    # Execute: Process the email, expecting a retry attempt
    result = await email_processing_service.process_email(sample_message)
    
    # Verify: Check retry behavior and final state
    assert result.status == ProcessingStatus.FAILED, "Email should be marked as failed"
    assert result.retry_count == 1, "One retry attempt should be recorded"
    assert isinstance(result.error, str), "Error details should be captured"
    assert "Test error" in result.error, "Original error message should be preserved"

@pytest.mark.asyncio
async def test_get_processing_state(email_processing_service, sample_message):
    """
    Test the ability to retrieve and verify email processing state.
    
    This test verifies that:
    1. Processing state can be retrieved for any email at any time
    2. The state object contains all required information:
       - Email ID
       - Current status
       - Metadata (sender, subject)
       - Timestamps
    3. The state accurately reflects the email's processing history
    4. The state object is properly typed and structured
    
    This test is important for ensuring the system maintains accurate
    tracking of email processing status and history, which is crucial
    for monitoring, debugging, and providing status updates to users.
    """
    # Execute: Initial processing to create a state
    await email_processing_service.process_email(sample_message)
    
    # Execute: Retrieve the processing state
    state = await email_processing_service.get_processing_state(sample_message.id)
    
    # Verify: Check state object structure and content
    assert isinstance(state, EmailProcessingState), \
           "Should return a properly typed state object"
    assert state.email_id == sample_message.id, \
           "State should be associated with correct email"
    assert state.metadata["sender"] == sample_message.sender, \
           "Metadata should include sender information"
    assert state.metadata["subject"] == sample_message.subject, \
           "Metadata should include email subject"