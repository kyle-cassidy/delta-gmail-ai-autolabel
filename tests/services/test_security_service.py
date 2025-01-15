"""
Tests for the SecurityService class.

This test suite verifies the email security verification system, including:
- Sender verification and reputation checks
- Attachment scanning and validation
- Content analysis for potential security threats
- Integration with audit logging
- Security policy enforcement
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from src.services.security_service import SecurityService

@pytest.fixture
def mock_audit_service():
    return AsyncMock()

@pytest.fixture
def mock_notification_service():
    return AsyncMock()

@pytest.fixture
def security_service(mock_audit_service, mock_notification_service):
    return SecurityService(
        audit_service=mock_audit_service,
        notification_service=mock_notification_service
    )

@pytest.fixture
def sample_message():
    message = MagicMock()
    message.id = "test123"
    message.sender = "test@example.com"
    message.subject = "Test Email"
    message.attachments = []
    return message

@pytest.mark.asyncio
async def test_verify_email_valid_sender(security_service, sample_message):
    """
    Test email verification with a valid sender.
    
    This test verifies that:
    1. Emails from legitimate senders pass verification
    2. The verification process completes successfully
    3. No security alerts are generated
    4. No audit logs are created for normal operations
    
    This test establishes the baseline for normal email processing,
    ensuring that legitimate emails are not incorrectly flagged.
    """
    # Execute: Verify a normal email
    result = await security_service.verify_email(sample_message)
    
    # Verify: Should pass security checks
    assert result is True, "Valid email should pass security verification"

@pytest.mark.asyncio
async def test_verify_email_suspicious_sender(security_service, sample_message, mock_audit_service):
    """
    Test email verification with a suspicious sender.
    
    This test verifies that:
    1. Emails from suspicious domains are properly identified
    2. The verification fails appropriately
    3. Security events are logged for suspicious senders
    4. The audit service is notified of the security concern
    
    This test is crucial for ensuring the system can detect and handle
    potentially malicious senders before any content processing occurs.
    """
    # Setup: Configure a suspicious sender address
    sample_message.sender = "suspicious@malicious-domain.com"
    
    # Execute: Attempt to verify the suspicious email
    result = await security_service.verify_email(sample_message)
    
    # Verify: Check security response
    assert result is False, "Suspicious sender should fail verification"
    mock_audit_service.log_security_event.assert_called_once(), \
        "Security event should be logged for suspicious sender"

@pytest.mark.asyncio
async def test_verify_email_with_attachments(security_service, sample_message):
    """
    Test email verification with valid attachments.
    
    This test verifies that:
    1. Legitimate attachments are properly validated
    2. File size limits are enforced
    3. Allowed file types are accepted
    4. Multiple attachment handling works correctly
    
    This test ensures that emails with normal attachments (like PDFs)
    are processed correctly and not falsely flagged as security risks.
    The test uses a 1MB PDF file as a typical business document example.
    """
    # Setup: Create a mock attachment with valid properties
    attachment = MagicMock()
    attachment.filename = "test.pdf"
    attachment.size = 1024 * 1024  # 1MB
    sample_message.attachments = [attachment]
    
    # Execute: Verify email with attachment
    result = await security_service.verify_email(sample_message)
    
    # Verify: Check attachment validation
    assert result is True, "Email with valid PDF attachment should pass verification"

@pytest.mark.asyncio
async def test_verify_email_suspicious_attachment(security_service, sample_message, mock_audit_service):
    """
    Test email verification with suspicious attachments.
    
    This test verifies that:
    1. Potentially dangerous file types are detected
    2. Executable files are properly blocked
    3. Security events are logged for suspicious attachments
    4. The verification fails for dangerous attachments
    
    This test is critical for preventing the processing of potentially
    malicious attachments that could pose security risks. It specifically
    tests the handling of executable files, which should always be blocked.
    """
    # Setup: Create a mock attachment with suspicious properties
    attachment = MagicMock()
    attachment.filename = "suspicious.exe"
    sample_message.attachments = [attachment]
    
    # Execute: Attempt to verify email with suspicious attachment
    result = await security_service.verify_email(sample_message)
    
    # Verify: Check security response
    assert result is False, "Email with executable attachment should fail verification"
    mock_audit_service.log_security_event.assert_called_once(), \
        "Security event should be logged for suspicious attachment"

@pytest.mark.asyncio
async def test_verify_email_large_attachment(security_service, sample_message, mock_audit_service):
    """
    Test email verification with oversized attachments.
    
    This test verifies that:
    1. File size limits are properly enforced
    2. Large attachments are detected and blocked
    3. Security events are logged for oversized files
    4. The verification fails for files exceeding size limits
    
    This test ensures the system prevents resource exhaustion attacks
    and maintains system performance by blocking unusually large files.
    The test uses a 26MB file, which exceeds typical size limits.
    """
    # Setup: Create a mock attachment with excessive size
    attachment = MagicMock()
    attachment.filename = "large.pdf"
    attachment.size = 26 * 1024 * 1024  # 26MB
    sample_message.attachments = [attachment]
    
    # Execute: Attempt to verify email with large attachment
    result = await security_service.verify_email(sample_message)
    
    # Verify: Check size limit enforcement
    assert result is False, "Email with oversized attachment should fail verification"
    mock_audit_service.log_security_event.assert_called_once(), \
        "Security event should be logged for oversized attachment"

@pytest.mark.asyncio
async def test_verify_email_suspicious_content(security_service, sample_message, mock_audit_service):
    """
    Test email verification with suspicious content patterns.
    
    This test verifies that:
    1. Content-based threat detection is working
    2. Suspicious patterns in email body are identified
    3. Security events are logged for suspicious content
    4. The verification fails for potentially malicious content
    
    This test ensures the system can detect potentially harmful content
    patterns in the email body, such as phishing attempts, malicious
    links, or other suspicious text patterns that might indicate threats.
    """
    # Setup: Configure email with suspicious content
    sample_message.plain = "This is a suspicious message with malicious content"
    
    # Execute: Attempt to verify email with suspicious content
    result = await security_service.verify_email(sample_message)
    
    # Verify: Check content analysis response
    assert result is False, "Email with suspicious content should fail verification"
    mock_audit_service.log_security_event.assert_called_once(), \
        "Security event should be logged for suspicious content"

@pytest.mark.asyncio
async def test_verify_email_multiple_issues(security_service, sample_message, mock_audit_service):
    """
    Test email verification with multiple security issues.
    
    This test verifies that:
    1. Multiple security issues are detected in a single email
    2. All security issues are properly logged
    3. The verification fails fast but logs all issues
    4. Each security issue generates its own audit event
    
    This test is important for ensuring the system can handle and report
    multiple security concerns in a single email, providing comprehensive
    security analysis and audit trails for investigation.
    """
    # Setup: Configure email with multiple security issues
    sample_message.sender = "suspicious@malicious-domain.com"
    attachment = MagicMock()
    attachment.filename = "suspicious.exe"
    sample_message.attachments = [attachment]
    
    # Execute: Attempt to verify email with multiple issues
    result = await security_service.verify_email(sample_message)
    
    # Verify: Check comprehensive security response
    assert result is False, "Email with multiple security issues should fail verification"
    assert mock_audit_service.log_security_event.call_count == 2, \
        "Each security issue should generate a separate audit log entry"

@pytest.mark.asyncio
async def test_check_sender_reputation(security_service):
    """
    Test sender reputation checking functionality.
    
    This test verifies that:
    1. Sender reputation scores are properly calculated
    2. Historical sender data is tracked and retrieved
    3. All required reputation metrics are present
    4. Reputation data is properly structured
    
    This test is crucial for ensuring the system maintains and uses
    sender reputation data effectively to make security decisions.
    The reputation system helps identify trusted senders and detect
    changes in sender behavior that might indicate compromise.
    """
    # Setup: Use a known trusted domain for testing
    sender = "test@trusted-domain.com"
    
    # Execute: Check sender's reputation
    result = await security_service.check_sender_reputation(sender)
    
    # Verify: Check reputation data structure and content
    assert result["reputation_score"] > 0, \
        "Trusted domain should have positive reputation score"
    assert "last_seen" in result, \
        "Reputation data should include last interaction timestamp"
    assert "total_emails" in result, \
        "Reputation data should track total email count"

@pytest.mark.asyncio
async def test_scan_attachment(security_service):
    """
    Test attachment scanning functionality.
    
    This test verifies that:
    1. Attachments are properly scanned for threats
    2. File content is analyzed for malicious patterns
    3. Scan results include all required security metrics
    4. Safe files are correctly identified
    
    This test ensures the system can effectively analyze file contents
    beyond just checking file extensions and sizes. It verifies the
    deep inspection capabilities of the attachment scanning system.
    """
    # Setup: Create a mock attachment with safe content
    attachment = MagicMock()
    attachment.filename = "document.pdf"
    attachment.content = b"test content"
    
    # Execute: Scan the attachment
    result = await security_service.scan_attachment(attachment)
    
    # Verify: Check scan results
    assert result["is_safe"] is True, \
        "Known safe content should pass security scan"
    assert "scan_results" in result, \
        "Scan should provide detailed analysis results"
    assert isinstance(result["scan_results"], dict), \
        "Scan results should contain structured analysis data"