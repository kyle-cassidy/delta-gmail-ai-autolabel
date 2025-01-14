Let's analyze the available tools and create a document outlining our content extraction strategy.
From the Gmail client, we have these key capabilities:

## Message class: 18:59:src/client/message.py
```python
class Message(object):
    """
    The Message class for emails in your Gmail mailbox. This class should not
    be manually constructed. Contains all information about the associated
    message, and can be used to modify the message's labels (e.g., marking as
    read/unread, archiving, moving to trash, starring, etc.).

    Args:
        service: the Gmail service object.
        user_id: the username of the account the message belongs to.
        msg_id: the message id.
        thread_id: the thread id.
        recipient: who the message was addressed to.
        sender: who the message was sent from.
        subject: the subject line of the message.
        date: the date the message was sent.
        snippet: the snippet line for the message.
        plain: the plaintext contents of the message. Default None.
        html: the HTML contents of the message. Default None.
        label_ids: the ids of labels associated with this message. Default [].
        attachments: a list of attachments for the message. Default [].
        headers: a dict of header values. Default {}
        cc: who the message was cc'd on the message.
        bcc: who the message was bcc'd on the message.

    Attributes:
        _service (googleapiclient.discovery.Resource): the Gmail service object.
        user_id (str): the username of the account the message belongs to.
        id (str): the message id.
        recipient (str): who the message was addressed to.
        sender (str): who the message was sent from.
        subject (str): the subject line of the message.
        date (str): the date the message was sent.
        snippet (str): the snippet line for the message.
        plain (str): the plaintext contents of the message.
        html (str): the HTML contents of the message.
        label_ids (List[str]): the ids of labels associated with this message.
        attachments (List[Attachment]): a list of attachments for the message.
        headers (dict): a dict of header values.
        cc (List[str]): who the message was cc'd on the message.
        bcc (List[str]): who the message was bcc'd on the message.

```


The Message class gives us access to:
- Plain text content (message.plain)
- HTML content (message.html)
- Subject and snippet
- Attachments list

## Attachment class: 12:53:src/client/attachment.py
```python
class Attachment(object):
    """
    The Attachment class for attachments to emails in your Gmail mailbox. This 
    class should not be manually instantiated.

    Args:
        service: The Gmail service object.
        user_id: The username of the account the message belongs to.
        msg_id: The id of message the attachment belongs to.
        att_id: The id of the attachment.
        filename: The filename associated with the attachment.
        filetype: The mime type of the file.
        data: The raw data of the file. Default None.

    Attributes:
        _service (googleapiclient.discovery.Resource): The Gmail service object.
        user_id (str): The username of the account the message belongs to.
        msg_id (str): The id of message the attachment belongs to.
        id (str): The id of the attachment.
        filename (str): The filename associated with the attachment.
        filetype (str): The mime type of the file.
        data (bytes): The raw data of the file.

    """
    
    def __init__(
        self,
        service: 'googleapiclient.discovery.Resource',
        user_id: str,
        msg_id: str,
        att_id: str,
        filename: str,
        filetype: str,
        data: Optional[bytes] = None
    ) -> None:
        self._service = service
        self.user_id = user_id
        self.msg_id = msg_id
        self.id = att_id
        self.filename = filename
        self.filetype = filetype
        self.data = data
```
