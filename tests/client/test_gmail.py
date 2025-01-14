import pytest
from unittest.mock import MagicMock, patch
from src.client.gmail import Gmail

@pytest.fixture
def mock_gmail_api():
    return MagicMock()

@pytest.fixture
def gmail_client(mock_gmail_api):
    with patch('src.client.gmail.build', return_value=mock_gmail_api):
        return Gmail()

def test_get_unread_inbox(gmail_client, mock_gmail_api):
    # Setup mock response
    mock_response = {
        'messages': [
            {'id': '123', 'threadId': 'thread123'},
            {'id': '456', 'threadId': 'thread456'}
        ]
    }
    mock_gmail_api.users().messages().list().execute.return_value = mock_response
    
    # Execute
    messages = gmail_client.get_unread_inbox()
    
    # Verify
    assert len(messages) == 2
    mock_gmail_api.users().messages().list.assert_called_with(
        userId='me',
        q='is:unread in:inbox'
    )

def test_get_message_by_id(gmail_client, mock_gmail_api):
    # Setup mock response
    message_id = '123'
    mock_response = {
        'id': message_id,
        'payload': {
            'headers': [
                {'name': 'From', 'value': 'sender@example.com'},
                {'name': 'Subject', 'value': 'Test Subject'}
            ],
            'parts': []
        }
    }
    mock_gmail_api.users().messages().get().execute.return_value = mock_response
    
    # Execute
    message = gmail_client.get_message(message_id)
    
    # Verify
    assert message.id == message_id
    mock_gmail_api.users().messages().get.assert_called_with(
        userId='me',
        id=message_id,
        format='full'
    )

def test_modify_labels(gmail_client, mock_gmail_api):
    # Setup
    message_id = '123'
    add_labels = ['Label_1', 'Label_2']
    remove_labels = ['Label_3']
    
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
    # Setup
    label_name = 'TestLabel'
    
    # Execute
    gmail_client.create_label(label_name)
    
    # Verify
    mock_gmail_api.users().labels().create.assert_called_with(
        userId='me',
        body={
            'name': label_name,
            'labelListVisibility': 'labelShow',
            'messageListVisibility': 'show'
        }
    )

def test_list_labels(gmail_client, mock_gmail_api):
    # Setup mock response
    mock_response = {
        'labels': [
            {'id': 'Label_1', 'name': 'First Label'},
            {'id': 'Label_2', 'name': 'Second Label'}
        ]
    }
    mock_gmail_api.users().labels().list().execute.return_value = mock_response
    
    # Execute
    labels = gmail_client.list_labels()
    
    # Verify
    assert len(labels) == 2
    mock_gmail_api.users().labels().list.assert_called_with(userId='me')