"""
ContentExtractionService: Manages content parsing and extraction.

Responsibilities:
- Coordinates multiple parser types
- Extracts structured data from emails
- Manages text extraction from attachments
- Handles different document formats
- Entity recognition and extraction
- Content normalization
"""

from typing import Any, Dict, List, Optional
from bs4 import BeautifulSoup
import base64
import re
from datetime import datetime

class ContentExtractionService:
    def __init__(self, storage_service=None, ocr_service=None):
        self.storage = storage_service
        self.ocr = ocr_service

    async def extract_content(self, message: Any) -> Dict[str, Any]:
        """
        Extract content from email message and its attachments.
        
        Args:
            message: Email message object
            
        Returns:
            Dictionary containing extracted content and metadata
        """
        content = {
            "text": "",
            "html": None,
            "format": "unknown",
            "attachments": [],
            "embedded_images": [],
            "urls": [],
            "tables": [],
            "metadata": {
                "timestamp": datetime.utcnow().isoformat(),
                "has_attachments": bool(message.attachments),
                "content_types": []
            }
        }

        # Extract text content
        if message.plain:
            content["text"] = message.plain
            content["format"] = "plain"
            content["metadata"]["content_types"].append("text/plain")

        # Extract HTML content
        if message.html:
            content["html"] = message.html
            if not message.plain:  # Only set format to html if no plain text
                content["format"] = "html"
            content["metadata"]["content_types"].append("text/html")
            
            # Parse HTML content
            await self._parse_html_content(message.html, content)

        # Process attachments
        if message.attachments:
            await self._process_attachments(message.attachments, content)

        # Store extracted content if storage service is available
        if self.storage:
            await self.storage.store_extracted_content(
                message_id=message.id,
                content=content
            )

        return content

    async def _parse_html_content(self, html: str, content: Dict[str, Any]) -> None:
        """Parse HTML content to extract additional information."""
        soup = BeautifulSoup(html, 'lxml')
        
        # Extract text if not already present
        if not content["text"]:
            content["text"] = soup.get_text()
        
        # Extract URLs
        for link in soup.find_all('a'):
            url = link.get('href')
            if url and url.startswith('http'):
                content["urls"].append(url)
        
        # Extract tables
        for table in soup.find_all('table'):
            parsed_table = []
            for row in table.find_all('tr'):
                parsed_row = [cell.get_text(strip=True) for cell in row.find_all(['td', 'th'])]
                if parsed_row:
                    parsed_table.append(parsed_row)
            if parsed_table:
                content["tables"].append(parsed_table)
        
        # Extract embedded images
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if src.startswith('data:image'):
                try:
                    # Extract base64 image data
                    img_data = re.sub('^data:image/.+;base64,', '', src)
                    img_bytes = base64.b64decode(img_data)
                    
                    # Perform OCR if service is available
                    ocr_text = None
                    if self.ocr:
                        ocr_text = await self.ocr.extract_text(img_bytes)
                    
                    content["embedded_images"].append({
                        "type": "embedded",
                        "format": src.split(';')[0].split('/')[1],
                        "ocr_text": ocr_text
                    })
                except Exception:
                    # Skip invalid base64 data
                    continue

    async def _process_attachments(self, attachments: List[Any], content: Dict[str, Any]) -> None:
        """Process email attachments."""
        for attachment in attachments:
            att_content = {
                "filename": attachment.filename,
                "type": self._get_attachment_type(attachment.filename),
                "size": len(attachment.content) if attachment.content else 0,
                "extracted_text": None,
                "ocr_text": None
            }

            if att_content["type"] == "pdf":
                # Extract text from PDF
                if self.storage:
                    att_content["extracted_text"] = await self.storage.extract_pdf_text(
                        attachment.content
                    )

            elif att_content["type"] == "image":
                # Perform OCR on image
                if self.ocr and attachment.content:
                    att_content["ocr_text"] = await self.ocr.extract_text(
                        attachment.content
                    )

            content["attachments"].append(att_content)
            content["metadata"]["content_types"].append(
                f"attachment/{att_content['type']}"
            )

    def _get_attachment_type(self, filename: str) -> str:
        """Determine attachment type from filename."""
        ext = filename.lower().split('.')[-1]
        if ext in ['pdf']:
            return 'pdf'
        elif ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp']:
            return 'image'
        elif ext in ['doc', 'docx']:
            return 'word'
        elif ext in ['xls', 'xlsx']:
            return 'excel'
        elif ext in ['txt', 'csv']:
            return 'text'
        return 'other'
