"""
AuditService: Manages system auditing and compliance tracking.

Responsibilities:
- Action logging
- Compliance tracking
- Audit trail maintenance
- Processing history
- Data access logging
- Regulatory compliance
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

class AuditService:
    def __init__(self, storage_service):
        self.storage = storage_service

    async def log_success(self, message_id: str, processing_state: Any) -> None:
        """Log a successful email processing operation."""
        await self.storage.store_audit_log({
            "message_id": message_id,
            "event_type": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "processing_duration_ms": self._calculate_duration(
                processing_state.started_at,
                processing_state.completed_at
            ),
            "metadata": processing_state.metadata
        })

    async def log_error(self, message_id: str, error: Exception) -> None:
        """Log an error that occurred during email processing."""
        await self.storage.store_audit_log({
            "message_id": message_id,
            "event_type": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "error_message": str(error),
            "error_type": error.__class__.__name__
        })

    async def log_security_event(self, message_id: str, event_type: str, details: Dict[str, Any]) -> None:
        """Log a security-related event."""
        await self.storage.store_audit_log({
            "message_id": message_id,
            "event_type": "security",
            "security_event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details
        })

    async def get_audit_logs(
        self,
        start_date: datetime,
        end_date: datetime,
        event_type: str = "all"
    ) -> List[Dict[str, Any]]:
        """Retrieve audit logs for a given time period and event type."""
        return await self.storage.get_audit_logs(
            start_date=start_date,
            end_date=end_date,
            event_type=event_type
        )

    async def get_audit_logs_by_message(self, message_id: str) -> List[Dict[str, Any]]:
        """Retrieve all audit logs for a specific message."""
        return await self.storage.get_audit_logs_by_message(message_id)

    async def get_error_statistics(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get error statistics for a given time period."""
        return await self.storage.get_error_statistics(
            start_date=start_date,
            end_date=end_date
        )

    def _calculate_duration(
        self,
        start_time: datetime,
        end_time: Optional[datetime]
    ) -> int:
        """Calculate duration in milliseconds between two timestamps."""
        if not end_time:
            end_time = datetime.utcnow()
        delta = end_time - start_time
        return int(delta.total_seconds() * 1000)
