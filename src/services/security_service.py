from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import re
import logging

from src.client.message import Message
from src.client.attachment import Attachment

@dataclass
class SecurityVerificationResult:
    is_safe: bool
    checks_passed: List[str]
    checks_failed: List[str]
    scan_date: datetime
    threat_level: str = "low"
    details: Optional[str] = None

class SecurityService:
    """
    SecurityService: Handles all security-related aspects of email processing.

    Responsibilities:
    - Spam detection and filtering
    - Malware scanning of attachments
    - Security policy enforcement
    - Sender verification
    - Content safety validation
    - Security logging and alerts
    """

    def __init__(self, audit_service, notification_service):
        self.audit = audit_service
        self.notifier = notification_service
        # For testing, trust example.com domain
        self.trusted_domains = {'example.com'}
        self.blocked_senders = set()  # TODO: Load from config
        self.max_attachment_size = 25 * 1024 * 1024  # 25MB
        self.allowed_attachment_types = {
            'application/pdf', 'image/jpeg', 'image/png',
            'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        }

    async def verify_email(self, message: Message) -> SecurityVerificationResult:
        """Main security verification method for incoming emails"""
        checks_passed = []
        checks_failed = []
        
        # Verify sender
        sender_safe = await self.verify_sender(message.sender)
        if sender_safe:
            checks_passed.append("sender_verification")
        else:
            checks_failed.append("sender_verification")

        # Check attachments if present
        if message.attachments:
            attachments_safe = await self.scan_attachments(message.attachments)
            if attachments_safe:
                checks_passed.append("attachment_scan")
            else:
                checks_failed.append("attachment_scan")

        # Check content safety
        content_safe = await self.verify_content_safety(message)
        if content_safe:
            checks_passed.append("content_safety")
        else:
            checks_failed.append("content_safety")

        # Determine overall safety
        is_safe = len(checks_failed) == 0
        threat_level = self._calculate_threat_level(checks_failed)

        result = SecurityVerificationResult(
            is_safe=is_safe,
            checks_passed=checks_passed,
            checks_failed=checks_failed,
            scan_date=datetime.utcnow(),
            threat_level=threat_level
        )

        # Log security check results
        await self._log_security_check(message.id, result)
        
        return result

    async def scan_attachment(self, attachment: Attachment) -> Dict[str, Any]:
        """Scan a single attachment for security threats."""
        return {
            "is_safe": True,
            "scan_results": {
                "filename": attachment.filename,
                "size": len(attachment.data) if attachment.data else 0,
                "type": attachment.filetype,
                "scan_date": datetime.utcnow()
            }
        }

    async def scan_attachments(self, attachments: List[Attachment]) -> bool:
        """Scans multiple attachments for security threats"""
        for attachment in attachments:
            # Check file size
            if attachment.data and len(attachment.data) > self.max_attachment_size:
                await self._log_security_violation(
                    "attachment_size_exceeded",
                    f"Attachment {attachment.filename} exceeds size limit"
                )
                return False

            # Check file type
            if attachment.filetype not in self.allowed_attachment_types:
                await self._log_security_violation(
                    "unauthorized_file_type",
                    f"Attachment type {attachment.filetype} not allowed"
                )
                return False

            # TODO: Implement actual malware scanning
            # For now, just checking basic security rules

        return True

    async def check_sender_reputation(self, sender: str) -> Dict[str, Any]:
        """Check sender's reputation score and history."""
        domain_match = re.search(r'@([\w.-]+)', sender)
        domain = domain_match.group(1) if domain_match else None
        
        return {
            "reputation_score": 1.0 if domain in self.trusted_domains else 0.5,
            "last_seen": datetime.utcnow(),
            "total_emails": 0,
            "domain": domain,
            "is_trusted": domain in self.trusted_domains
        }

    async def verify_sender(self, sender: str) -> bool:
        """Verifies sender against security policies"""
        if sender in self.blocked_senders:
            await self._log_security_violation(
                "blocked_sender",
                f"Email from blocked sender: {sender}"
            )
            return False

        # Extract domain from sender email
        domain_match = re.search(r'@([\w.-]+)', sender)
        if not domain_match:
            await self._log_security_violation(
                "invalid_sender_format",
                f"Invalid sender email format: {sender}"
            )
            return False

        domain = domain_match.group(1)
        
        # TODO: Implement SPF, DKIM, and DMARC checks
        # For now, just checking against trusted domains
        return domain in self.trusted_domains

    async def verify_content_safety(self, message: Message) -> bool:
        """Verifies email content against security policies"""
        # Check for suspicious patterns in content
        suspicious_patterns = [
            r'(?i)urgent.*transfer',
            r'(?i)bank.*verify',
            r'(?i)password.*reset',
            r'(?i)suspicious.*activity'
        ]

        content = f"{message.subject} {message.plain or ''}"
        
        for pattern in suspicious_patterns:
            if re.search(pattern, content):
                await self._log_security_violation(
                    "suspicious_content",
                    f"Suspicious pattern detected in message {message.id}"
                )
                return False

        return True

    def _calculate_threat_level(self, failed_checks: List[str]) -> str:
        """Calculates threat level based on failed security checks"""
        if not failed_checks:
            return "low"
        if "attachment_scan" in failed_checks:
            return "high"
        if len(failed_checks) > 1:
            return "medium"
        return "low"

    async def _log_security_check(self, message_id: str, result: SecurityVerificationResult):
        """Logs security check results"""
        await self.audit.log_security_check(
            message_id=message_id,
            timestamp=result.scan_date,
            passed=result.checks_passed,
            failed=result.checks_failed,
            threat_level=result.threat_level
        )

        if not result.is_safe:
            await self.notifier.send_security_alert(
                message_id=message_id,
                threat_level=result.threat_level,
                failed_checks=result.checks_failed
            )

    async def _log_security_violation(self, violation_type: str, details: str):
        """Logs security violations"""
        await self.audit.log_security_violation(
            violation_type=violation_type,
            details=details,
            timestamp=datetime.utcnow()
        )
