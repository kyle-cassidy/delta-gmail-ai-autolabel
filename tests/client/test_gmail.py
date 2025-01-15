import pytest
from unittest.mock import MagicMock, patch
from src.client.gmail import Gmail

@pytest.fixture
def mock_gmail_api():
    """Create a mock Gmail API with proper response chains."""
    api = MagicMock()
    
    # Mock users() chain
    users = MagicMock()
    api.users.return_value = users
    
    # Mock messages() chain
    messages = MagicMock()
    users.messages.return_value = messages
    
    # Mock messages().list()
    messages_list = MagicMock()
    messages.list.return_value = messages_list
    messages_list.execute.return_value = {
        'messages': [
            {'id': '123', 'threadId': 'thread123'},
            {'id': '456', 'threadId': 'thread456'}
        ]
    }
    
    # Mock messages().get()
    message_get = MagicMock()
    messages.get.return_value = message_get
    message_get.execute.return_value = {
        'id': '123',
        'threadId': 'thread123',
        'labelIds': ['INBOX'],
        'snippet': 'Test snippet',
        'payload': {
            'headers': [
                {'name': 'From', 'value': 'sender@example.com'},
                {'name': 'To', 'value': 'recipient@example.com'},
                {'name': 'Subject', 'value': 'Test Subject'},
                {'name': 'Date', 'value': 'Mon, 1 Jan 2024 10:00:00 +0000'}
            ],
            'parts': [
                {
                    'mimeType': 'text/plain',
                    'body': {'data': 'UGxhaW4gdGV4dCBjb250ZW50'}  # "Plain text content"
                }
            ]
        }
    }
    
    # Mock labels() chain
    labels = MagicMock()
    users.labels.return_value = labels
    
    # Mock labels().create()
    create = MagicMock()
    labels.create.return_value = create
    create.execute.return_value = {
        'id': 'Label_123',
        'name': 'TestLabel',
        'messageListVisibility': 'show',
        'labelListVisibility': 'labelShow',
        'type': 'user'
    }
    
    # Mock labels().list()
    labels_list = MagicMock()
    labels.list.return_value = labels_list
    labels_list.execute.return_value = {
        'labels': [
            {'id': 'Label_1', 'name': 'First Label'},
            {'id': 'Label_2', 'name': 'Second Label'}
        ]
    }
    
    return api

@pytest.fixture
def mock_creds():
    """Mock OAuth2Credentials with proper universe domain."""
    creds = MagicMock()
    creds.invalid = False
    creds.access_token_expired = False
    # Required for Google API client validation
    creds.universe_domain = "googleapis.com"
    creds.valid = True
    creds.expired = False
    creds.refresh_token = "mock_refresh_token"
    creds.token_uri = "https://oauth2.googleapis.com/token"
    creds.client_id = "mock_client_id"
    creds.client_secret = "mock_client_secret"
    return creds

@pytest.fixture
def gmail_client(mock_gmail_api, mock_creds):
    with patch('src.client.gmail.build', return_value=mock_gmail_api), \
         patch('oauth2client.file.Storage') as mock_storage:
        # Setup mock storage to return our mock credentials
        mock_storage.return_value.get.return_value = mock_creds
        return Gmail(_creds=mock_creds)

def test_get_unread_inbox(gmail_client, mock_gmail_api):
    """Test retrieving unread messages from inbox."""
    # Execute
    messages = gmail_client.get_unread_inbox()
    
    # Verify
    assert len(messages) == 2
    mock_gmail_api.users().messages().list.assert_called_with(
        userId='me',
        q='label:INBOX label:UNREAD',
        includeSpamTrash=False
    )

def test_get_message_by_id(gmail_client, mock_gmail_api):
    """Test retrieving a specific message by ID."""
    # Execute
    messages = gmail_client.get_messages(user_id='me', msg_ids=['123'])
    
    # Verify
    assert len(messages) == 1
    assert messages[0].id == '123'
    assert messages[0].thread_id == 'thread123'
    assert messages[0].sender == 'sender@example.com'
    mock_gmail_api.users().messages().get.assert_called_with(
        userId='me',
        id='123',
        format='full'
    )

def test_modify_labels(gmail_client, mock_gmail_api):
    """Test modifying message labels."""
    # Setup
    message_id = '123'
    add_labels = ['Label_1', 'Label_2']
    remove_labels = ['Label_3']
    
    # Setup mock response
    modify_response = MagicMock()
    modify_response.execute.return_value = {
        'id': message_id,
        'labelIds': add_labels
    }
    mock_gmail_api.users().messages().modify.return_value = modify_response
    
    # Execute
    gmail_client.modify_labels(message_id, add_labels, remove_labels)
    
    # Verify
    mock_gmail_api.users().messages().modify.assert_called_with(
        userId='me',
        id=message_id,
        body={
            'addLabelIds': add_labels,
            'removeLabelIds': remove_labels
        }
    )

def test_create_label(gmail_client, mock_gmail_api):
    """Test creating a new label."""
    # Setup
    label_name = 'TestLabel'
    
    # Execute
    label = gmail_client.create_label(label_name)
    
    # Verify
    assert label.id == 'Label_123'
    assert label.name == 'TestLabel'
    mock_gmail_api.users().labels().create.assert_called_with(
        userId='me',
        body={
            'name': label_name,
            'labelListVisibility': 'labelShow',
            'messageListVisibility': 'show'
        }
    )

def test_list_labels(gmail_client, mock_gmail_api):
    """Test retrieving list of labels."""
    # Execute
    labels = gmail_client.list_labels()
    
    # Verify
    assert len(labels) == 2
    assert labels[0].id == 'Label_1'
    assert labels[0].name == 'First Label'
    assert labels[1].id == 'Label_2'
    assert labels[1].name == 'Second Label'
    mock_gmail_api.users().labels().list.assert_called_with(userId='me')