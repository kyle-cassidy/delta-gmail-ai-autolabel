import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from src.services.audit_service import AuditService

@pytest.fixture
def mock_storage():
    return AsyncMock()

@pytest.fixture
def audit_service(mock_storage):
    return AuditService(storage_service=mock_storage)

@pytest.mark.asyncio
async def test_log_success(audit_service, mock_storage):
    # Setup
    message_id = "test123"
    processing_state = MagicMock(
        email_id=message_id,
        started_at=datetime.utcnow(),
        completed_at=datetime.utcnow(),
        metadata={"sender": "test@example.com"}
    )
    
    # Execute
    await audit_service.log_success(message_id, processing_state)
    
    # Verify
    mock_storage.store_audit_log.assert_called_once()
    call_args = mock_storage.store_audit_log.call_args[0][0]
    assert call_args["message_id"] == message_id
    assert call_args["event_type"] == "success"
    assert "processing_duration_ms" in call_args
    assert call_args["metadata"] == processing_state.metadata

@pytest.mark.asyncio
async def test_log_error(audit_service, mock_storage):
    # Setup
    message_id = "test123"
    error = Exception("Test error")
    
    # Execute
    await audit_service.log_error(message_id, error)
    
    # Verify
    mock_storage.store_audit_log.assert_called_once()
    call_args = mock_storage.store_audit_log.call_args[0][0]
    assert call_args["message_id"] == message_id
    assert call_args["event_type"] == "error"
    assert call_args["error_message"] == str(error)
    assert "timestamp" in call_args

@pytest.mark.asyncio
async def test_log_security_event(audit_service, mock_storage):
    # Setup
    message_id = "test123"
    event_type = "suspicious_sender"
    details = {"sender": "suspicious@example.com"}
    
    # Execute
    await audit_service.log_security_event(message_id, event_type, details)
    
    # Verify
    mock_storage.store_audit_log.assert_called_once()
    call_args = mock_storage.store_audit_log.call_args[0][0]
    assert call_args["message_id"] == message_id
    assert call_args["event_type"] == "security"
    assert call_args["security_event_type"] == event_type
    assert call_args["details"] == details

@pytest.mark.asyncio
async def test_get_audit_logs(audit_service, mock_storage):
    # Setup
    mock_logs = [
        {"message_id": "1", "event_type": "success"},
        {"message_id": "2", "event_type": "error"}
    ]
    mock_storage.get_audit_logs.return_value = mock_logs
    
    # Execute
    logs = await audit_service.get_audit_logs(
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow(),
        event_type="all"
    )
    
    # Verify
    assert logs == mock_logs
    mock_storage.get_audit_logs.assert_called_once()

@pytest.mark.asyncio
async def test_get_audit_logs_by_message(audit_service, mock_storage):
    # Setup
    message_id = "test123"
    mock_logs = [
        {"message_id": message_id, "event_type": "success"},
        {"message_id": message_id, "event_type": "error"}
    ]
    mock_storage.get_audit_logs_by_message.return_value = mock_logs
    
    # Execute
    logs = await audit_service.get_audit_logs_by_message(message_id)
    
    # Verify
    assert logs == mock_logs
    mock_storage.get_audit_logs_by_message.assert_called_once_with(message_id)

@pytest.mark.asyncio
async def test_get_error_statistics(audit_service, mock_storage):
    # Setup
    mock_stats = {
        "total_errors": 10,
        "error_types": {
            "security": 3,
            "processing": 7
        }
    }
    mock_storage.get_error_statistics.return_value = mock_stats
    
    # Execute
    stats = await audit_service.get_error_statistics(
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow()
    )
    
    # Verify
    assert stats == mock_stats
    mock_storage.get_error_statistics.assert_called_once()