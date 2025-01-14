import pytest
from unittest.mock import AsyncMock, MagicMock
from src.services.content_extraction_service import ContentExtractionService

@pytest.fixture
def mock_storage():
    return AsyncMock()

@pytest.fixture
def content_extraction_service(mock_storage):
    return ContentExtractionService(storage_service=mock_storage)

@pytest.fixture
def sample_message():
    message = MagicMock()
    message.id = "test123"
    message.plain = "This is a plain text email"
    message.html = "<div>This is an HTML email</div>"
    message.attachments = []
    return message

@pytest.mark.asyncio
async def test_extract_plain_text(content_extraction_service, sample_message):
    # Execute
    content = await content_extraction_service.extract_content(sample_message)
    
    # Verify
    assert content["text"] == sample_message.plain
    assert content["format"] == "plain"
    assert "metadata" in content

@pytest.mark.asyncio
async def test_extract_html_content(content_extraction_service, sample_message):
    # Setup
    sample_message.plain = None
    
    # Execute
    content = await content_extraction_service.extract_content(sample_message)
    
    # Verify
    assert "This is an HTML email" in content["text"]
    assert content["format"] == "html"
    assert "metadata" in content

@pytest.mark.asyncio
async def test_extract_pdf_content(content_extraction_service, sample_message):
    # Setup
    attachment = MagicMock()
    attachment.filename = "document.pdf"
    attachment.content = b"%PDF-1.4 test content"
    sample_message.attachments = [attachment]
    
    # Execute
    content = await content_extraction_service.extract_content(sample_message)
    
    # Verify
    assert "attachments" in content
    assert len(content["attachments"]) == 1
    assert content["attachments"][0]["type"] == "pdf"
    assert "extracted_text" in content["attachments"][0]

@pytest.mark.asyncio
async def test_extract_image_content(content_extraction_service, sample_message):
    # Setup
    attachment = MagicMock()
    attachment.filename = "image.jpg"
    attachment.content = b"image data"
    sample_message.attachments = [attachment]
    
    # Execute
    content = await content_extraction_service.extract_content(sample_message)
    
    # Verify
    assert "attachments" in content
    assert len(content["attachments"]) == 1
    assert content["attachments"][0]["type"] == "image"
    assert "ocr_text" in content["attachments"][0]

@pytest.mark.asyncio
async def test_extract_multiple_attachments(content_extraction_service, sample_message):
    # Setup
    attachments = [
        MagicMock(filename="doc1.pdf", content=b"%PDF-1.4 content1"),
        MagicMock(filename="doc2.pdf", content=b"%PDF-1.4 content2"),
        MagicMock(filename="image.jpg", content=b"image data")
    ]
    sample_message.attachments = attachments
    
    # Execute
    content = await content_extraction_service.extract_content(sample_message)
    
    # Verify
    assert len(content["attachments"]) == 3
    assert sum(1 for a in content["attachments"] if a["type"] == "pdf") == 2
    assert sum(1 for a in content["attachments"] if a["type"] == "image") == 1

@pytest.mark.asyncio
async def test_extract_with_embedded_images(content_extraction_service, sample_message):
    # Setup
    sample_message.html = """
        <div>Email content with embedded image:
            <img src="data:image/jpeg;base64,/9j/4AAQSkZJRg==" />
        </div>
    """
    
    # Execute
    content = await content_extraction_service.extract_content(sample_message)
    
    # Verify
    assert "embedded_images" in content
    assert len(content["embedded_images"]) == 1
    assert "ocr_text" in content["embedded_images"][0]

@pytest.mark.asyncio
async def test_extract_with_urls(content_extraction_service, sample_message):
    # Setup
    sample_message.html = """
        <div>Email with links:
            <a href="https://example.com/doc1.pdf">Document 1</a>
            <a href="https://example.com/doc2.pdf">Document 2</a>
        </div>
    """
    
    # Execute
    content = await content_extraction_service.extract_content(sample_message)
    
    # Verify
    assert "urls" in content
    assert len(content["urls"]) == 2
    assert all(url.startswith("https://") for url in content["urls"])

@pytest.mark.asyncio
async def test_extract_with_tables(content_extraction_service, sample_message):
    # Setup
    sample_message.html = """
        <table>
            <tr><td>Name</td><td>Value</td></tr>
            <tr><td>Item 1</td><td>100</td></tr>
        </table>
    """
    
    # Execute
    content = await content_extraction_service.extract_content(sample_message)
    
    # Verify
    assert "tables" in content
    assert len(content["tables"]) == 1
    assert isinstance(content["tables"][0], list)  # Should be a 2D array

@pytest.mark.asyncio
async def test_content_storage(content_extraction_service, sample_message, mock_storage):
    # Execute
    content = await content_extraction_service.extract_content(sample_message)
    
    # Verify
    mock_storage.store_extracted_content.assert_called_once_with(
        message_id=sample_message.id,
        content=content
    )