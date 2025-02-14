from pathlib import Path
from typing import Optional
import shutil
import PyPDF2
import logging
from rich.console import Console

logger = logging.getLogger(__name__)
console = Console()


class FileHandler:
    """Handles file operations for document processing."""

    @staticmethod
    def extract_text_from_pdf(pdf_path: Path) -> str:
        """Extract text content from a PDF file."""
        try:
            with open(pdf_path, "rb") as file:
                # Create PDF reader object
                reader = PyPDF2.PdfReader(file)

                # Extract text from all pages
                text = []
                for page in reader.pages:
                    text.append(page.extract_text())

                extracted_text = "\n".join(text)

                # Debug output
                logger.debug(f"Extracted {len(extracted_text)} characters from PDF")
                logger.debug(f"First 100 chars: {extracted_text[:100]}")

                return extracted_text
        except Exception as e:
            console.print(f"[red]Error extracting text from PDF:[/red] {e}")
            logger.error(f"Error extracting text from PDF: {e}")
            return ""

    @staticmethod
    def move_or_copy(
        src_path: Path,
        target_dir: Path,
        new_filename: str,
        is_external: bool,
    ) -> None:
        """Move or copy a file to the target directory."""
        target_path = target_dir / new_filename
        try:
            if is_external:
                shutil.copy2(str(src_path), str(target_path))
                console.print(f"[green]Copied document to:[/green] {target_path}")
            else:
                shutil.move(str(src_path), str(target_path))
                console.print(f"[green]Moved document to:[/green] {target_path}")
        except (shutil.Error, OSError, PermissionError) as e:
            console.print(f"[red]Error moving/copying file:[/red] {e}")
            raise

    @staticmethod
    def generate_filename(meta_data: "DocumentMetadata") -> str:
        """Generate a standardized filename."""
        filename = f"{meta_data.state}-{meta_data.client_code}-{meta_data.base_type}"
        if meta_data.description:
            filename += f"-{meta_data.description}"
        return filename + ".pdf"
