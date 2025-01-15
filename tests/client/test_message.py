import pytest
from unittest.mock import MagicMock
from src.client.message import Message
from src.client.attachment import Attachment
import email

@pytest.fixture
def mock_service():
    return MagicMock()

@pytest.fixture
def mock_creds():
    creds = MagicMock()
    creds.access_token_expired = False
    return creds

@pytest.fixture
def sample_gmail_message(mock_service, mock_creds):
    # Create a Message instance with required parameters
    return Message(
        service=mock_service,
        creds=mock_creds,
        user_id='me',
        msg_id='msg123',
        thread_id='thread123',
        recipient='recipient@example.com',
        sender='sender@example.com',
        subject='Test Subject',
        date='Mon, 1 Jan 2024 10:00:00 +0000',
        snippet='Email snippet...',
        plain='Plain text content',
        html='<div>HTML content</div>',
        label_ids=['INBOX', 'UNREAD']
    )

@pytest.fixture
def message(sample_gmail_message):
    return sample_gmail_message

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

def test_message_with_attachment(mock_service, mock_creds):
    # Create a message with attachment
    attachment = Attachment(
        service=mock_service,
        user_id='me',
        msg_id='msg123',
        att_id='att123',
        filename='test.pdf',
        filetype='application/pdf',
        data=b'PDF content'
    )
    
    message = Message(
        service=mock_service,
        creds=mock_creds,
        user_id='me',
        msg_id='msg123',
        thread_id='thread123',
        recipient='recipient@example.com',
        sender='sender@example.com',
        subject='Test Subject',
        date='Mon, 1 Jan 2024 10:00:00 +0000',
        snippet='Email with attachment',
        plain='Content',
        attachments=[attachment]
    )
    
    assert len(message.attachments) == 1
    assert message.attachments[0].filename == 'test.pdf'
    assert message.attachments[0].filetype == 'application/pdf'
    assert message.attachments[0].id == 'att123'

def test_nested_multipart_message(mock_service, mock_creds):
    # Create a message with both plain and HTML content plus attachment
    attachment = Attachment(
        service=mock_service,
        user_id='me',
        msg_id='msg123',
        att_id='att123',
        filename='test.pdf',
        filetype='application/pdf',
        data=b'PDF content'
    )
    
    message = Message(
        service=mock_service,
        creds=mock_creds,
        user_id='me',
        msg_id='msg123',
        thread_id='thread123',
        recipient='recipient@example.com',
        sender='sender@example.com',
        subject='Test Subject',
        date='Mon, 1 Jan 2024 10:00:00 +0000',
        snippet='Multipart message',
        plain='Plain content',
        html='<div>HTML</div>',
        attachments=[attachment]
    )
    
    assert message.plain == 'Plain content'
    assert message.html == '<div>HTML</div>'
    assert len(message.attachments) == 1
    assert message.attachments[0].filename == 'test.pdf'

def test_message_without_parts(mock_service, mock_creds):
    # Create a simple plain text message
    message = Message(
        service=mock_service,
        creds=mock_creds,
        user_id='me',
        msg_id='msg123',
        thread_id='thread123',
        recipient='recipient@example.com',
        sender='sender@example.com',
        subject='Test Subject',
        date='Mon, 1 Jan 2024 10:00:00 +0000',
        snippet='Simple message',
        plain='Simple plain text'
    )
    
    assert message.plain == 'Simple plain text'
    assert message.html is None
    assert len(message.attachments) == 0

def test_message_with_inline_images(mock_service, mock_creds):
    # Create a message with inline image
    attachment = Attachment(
        service=mock_service,
        user_id='me',
        msg_id='msg123',
        att_id='att123',
        filename='image.jpg',
        filetype='image/jpeg',
        data=b'image data'
    )
    
    message = Message(
        service=mock_service,
        creds=mock_creds,
        user_id='me',
        msg_id='msg123',
        thread_id='thread123',
        recipient='recipient@example.com',
        sender='sender@example.com',
        subject='Test Subject',
        date='Mon, 1 Jan 2024 10:00:00 +0000',
        snippet='Message with inline image',
        html='<img src="cid:image1">',
        attachments=[attachment]
    )
    
    assert len(message.attachments) == 1
    assert message.attachments[0].filename == 'image.jpg'
    assert message.attachments[0].filetype == 'image/jpeg'
    assert message.attachments[0].id == 'att123'

def test_message_with_invalid_encoding(mock_service, mock_creds):
    # Create a message with invalid encoding
    message = Message(
        service=mock_service,
        creds=mock_creds,
        user_id='me',
        msg_id='msg123',
        thread_id='thread123',
        recipient='recipient@example.com',
        sender='sender@example.com',
        subject='Test Subject',
        date='Mon, 1 Jan 2024 10:00:00 +0000',
        snippet='Message with invalid encoding',
        plain=''  # Empty string for invalid content
    )
    
    assert message.plain == ''  # Should handle invalid content gracefully

def test_header_parsing(mock_service, mock_creds):
    # Create a message with various headers
    message = Message(
        service=mock_service,
        creds=mock_creds,
        user_id='me',
        msg_id='msg123',
        thread_id='thread123',
        recipient='jane@example.com, bob@example.com',
        sender='"John Doe" <john@example.com>',
        subject='Test Subject',
        date='Mon, 1 Jan 2024 10:00:00 +0000',
        snippet='Message with headers',
        plain='content',
        cc=['cc@example.com'],
        bcc=['bcc@example.com'],
        headers={
            'Reply-To': 'reply@example.com'
        }
    )
    
    assert message.sender == '"John Doe" <john@example.com>'
    assert len(message.cc) == 1
    assert message.cc[0] == 'cc@example.com'
    assert len(message.bcc) == 1
    assert message.bcc[0] == 'bcc@example.com'
    assert message.headers.get('Reply-To') == 'reply@example.com'