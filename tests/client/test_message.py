import pytest
from unittest.mock import MagicMock
from src.client.message import Message
from base64 import b64encode
import email

@pytest.fixture
def sample_gmail_message():
    return {
        'id': 'msg123',
        'threadId': 'thread123',
        'labelIds': ['INBOX', 'UNREAD'],
        'snippet': 'Email snippet...',
        'payload': {
            'headers': [
                {'name': 'From', 'value': 'sender@example.com'},
                {'name': 'To', 'value': 'recipient@example.com'},
                {'name': 'Subject', 'value': 'Test Subject'},
                {'name': 'Date', 'value': 'Mon, 1 Jan 2024 10:00:00 +0000'}
            ],
            'mimeType': 'multipart/alternative',
            'parts': [
                {
                    'mimeType': 'text/plain',
                    'body': {'data': b64encode(b'Plain text content').decode()}
                },
                {
                    'mimeType': 'text/html',
                    'body': {'data': b64encode(b'<div>HTML content</div>').decode()}
                }
            ]
        }
    }

@pytest.fixture
def message(sample_gmail_message):
    return Message(sample_gmail_message)

def test_basic_properties(message):
    assert message.id == 'msg123'
    assert message.thread_id == 'thread123'
    assert message.sender == 'sender@example.com'
    assert message.recipient == 'recipient@example.com'
    assert message.subject == 'Test Subject'
    assert isinstance(message.date, email.utils.datetime.datetime)
    assert 'Plain text content' in message.plain
    assert '<div>HTML content</div>' in message.html

def test_labels(message):
    assert message.labels == ['INBOX', 'UNREAD']
    assert message.is_unread is True
    assert message.in_inbox is True

def test_message_with_attachment():
    # Setup message with attachment
    msg_with_attachment = {
        'id': 'msg123',
        'payload': {
            'headers': [
                {'name': 'From', 'value': 'sender@example.com'},
                {'name': 'Subject', 'value': 'Test Subject'}
            ],
            'parts': [
                {
                    'mimeType': 'text/plain',
                    'body': {'data': b64encode(b'Content').decode()}
                },
                {
                    'filename': 'test.pdf',
                    'mimeType': 'application/pdf',
                    'body': {'attachmentId': 'att123'}
                }
            ]
        }
    }
    
    message = Message(msg_with_attachment)
    assert len(message.attachment_parts) == 1
    attachment = message.attachment_parts[0]
    assert attachment['filename'] == 'test.pdf'
    assert attachment['mimeType'] == 'application/pdf'
    assert attachment['attachmentId'] == 'att123'

def test_nested_multipart_message():
    # Setup nested multipart message
    nested_msg = {
        'id': 'msg123',
        'payload': {
            'headers': [
                {'name': 'From', 'value': 'sender@example.com'},
                {'name': 'Subject', 'value': 'Test Subject'}
            ],
            'mimeType': 'multipart/mixed',
            'parts': [
                {
                    'mimeType': 'multipart/alternative',
                    'parts': [
                        {
                            'mimeType': 'text/plain',
                            'body': {'data': b64encode(b'Plain content').decode()}
                        },
                        {
                            'mimeType': 'text/html',
                            'body': {'data': b64encode(b'<div>HTML</div>').decode()}
                        }
                    ]
                },
                {
                    'filename': 'test.pdf',
                    'mimeType': 'application/pdf',
                    'body': {'attachmentId': 'att123'}
                }
            ]
        }
    }
    
    message = Message(nested_msg)
    assert 'Plain content' in message.plain
    assert '<div>HTML</div>' in message.html
    assert len(message.attachment_parts) == 1

def test_message_without_parts():
    # Setup message without parts
    simple_msg = {
        'id': 'msg123',
        'payload': {
            'headers': [
                {'name': 'From', 'value': 'sender@example.com'},
                {'name': 'Subject', 'value': 'Test Subject'}
            ],
            'mimeType': 'text/plain',
            'body': {'data': b64encode(b'Simple plain text').decode()}
        }
    }
    
    message = Message(simple_msg)
    assert message.plain == 'Simple plain text'
    assert message.html is None
    assert len(message.attachment_parts) == 0

def test_message_with_inline_images():
    # Setup message with inline images
    msg_with_inline = {
        'id': 'msg123',
        'payload': {
            'headers': [
                {'name': 'From', 'value': 'sender@example.com'},
                {'name': 'Subject', 'value': 'Test Subject'}
            ],
            'parts': [
                {
                    'mimeType': 'text/html',
                    'body': {'data': b64encode(b'<img src="cid:image1">').decode()}
                },
                {
                    'filename': 'image.jpg',
                    'mimeType': 'image/jpeg',
                    'headers': [{'name': 'Content-ID', 'value': '<image1>'}],
                    'body': {'attachmentId': 'att123'}
                }
            ]
        }
    }
    
    message = Message(msg_with_inline)
    assert len(message.inline_parts) == 1
    assert message.inline_parts[0]['filename'] == 'image.jpg'
    assert message.inline_parts[0]['content_id'] == 'image1'

def test_message_with_invalid_encoding():
    # Setup message with invalid encoding
    invalid_msg = {
        'id': 'msg123',
        'payload': {
            'headers': [
                {'name': 'From', 'value': 'sender@example.com'},
                {'name': 'Subject', 'value': 'Test Subject'}
            ],
            'parts': [
                {
                    'mimeType': 'text/plain',
                    'body': {'data': 'invalid base64'}
                }
            ]
        }
    }
    
    message = Message(invalid_msg)
    assert message.plain == ''  # Should handle invalid encoding gracefully

def test_header_parsing():
    # Setup message with various header formats
    msg_with_headers = {
        'id': 'msg123',
        'payload': {
            'headers': [
                {'name': 'From', 'value': '"John Doe" <john@example.com>'},
                {'name': 'To', 'value': 'jane@example.com, bob@example.com'},
                {'name': 'Cc', 'value': 'cc@example.com'},
                {'name': 'Reply-To', 'value': 'reply@example.com'},
                {'name': 'Subject', 'value': 'Test Subject'}
            ],
            'body': {'data': b64encode(b'content').decode()}
        }
    }
    
    message = Message(msg_with_headers)
    assert message.sender == 'john@example.com'
    assert message.sender_name == 'John Doe'
    assert isinstance(message.recipients, list)
    assert len(message.recipients) == 2
    assert message.cc == 'cc@example.com'
    assert message.reply_to == 'reply@example.com'