#!/usr/bin/env python3

import click
import json
import shutil
import pathlib
from typing import Dict, List, Optional
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.progress import track
from pydantic import BaseModel, Field, field_validator, ConfigDict
import questionary
from questionary import Choice

console = Console()

# Directory structure
BASE_DIR = pathlib.Path("tests/fixtures/documents")
TO_LABEL_DIR = BASE_DIR / "_to_label"
LABELED_DIR = BASE_DIR / "labeled_documents/documents"
METADATA_FILE = BASE_DIR / "labeled_documents/metadata.json"

# Valid values
VALID_STATES = ["ME", "CA", "EP", "US", "IL", "AL"]
VALID_BASE_TYPES = ["NEW", "RENEW", "TONNAGE", "CERT", "LABEL"]
VALID_PRODUCT_CATEGORIES = [
    "Commercial Fertilizers",
    "Plant and Soil Amendments",
    "Biostimulants",
    "Liming Materials",
    "Organic Input Materials"
]

class DocumentMetadata(BaseModel):
    """Pydantic model for document metadata."""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    state: str = Field(..., description="Two-letter state code")
    client_code: str = Field(..., description="Three-letter client code")
    base_type: str = Field(..., description="Document base type")
    description: Optional[str] = Field(None, description="Optional description")
    product_categories: List[str] = Field(
        default_factory=lambda: ["Commercial Fertilizers"],
        description="List of product categories"
    )
    expected_filename: str = Field(..., description="Expected standardized filename")
    last_updated: datetime = Field(default_factory=datetime.now)
    
    @field_validator("state")
    def validate_state(cls, v: str) -> str:
        v = v.upper()
        if v not in VALID_STATES:
            raise ValueError(f"Invalid state code. Must be one of: {', '.join(VALID_STATES)}")
        return v
    
    @field_validator("client_code")
    def validate_client_code(cls, v: str) -> str:
        v = v.upper()
        if len(v) != 3:
            raise ValueError("Client code must be exactly 3 letters")
        if not v.isalpha():
            raise ValueError("Client code must contain only letters")
        return v
    
    @field_validator("base_type")
    def validate_base_type(cls, v: str) -> str:
        v = v.upper()
        if v not in VALID_BASE_TYPES:
            raise ValueError(f"Invalid base type. Must be one of: {', '.join(VALID_BASE_TYPES)}")
        return v
    
    @field_validator("product_categories")
    def validate_product_categories(cls, v: List[str]) -> List[str]:
        invalid_categories = [cat for cat in v if cat not in VALID_PRODUCT_CATEGORIES]
        if invalid_categories:
            raise ValueError(
                f"Invalid product categories: {', '.join(invalid_categories)}. "
                f"Must be one of: {', '.join(VALID_PRODUCT_CATEGORIES)}"
            )
        return v

class MetadataStore(BaseModel):
    """Pydantic model for the metadata store."""
    documents: Dict[str, DocumentMetadata] = Field(default_factory=dict)
    last_updated: Optional[datetime] = None

def ensure_directories():
    """Ensure all required directories exist."""
    TO_LABEL_DIR.mkdir(parents=True, exist_ok=True)
    LABELED_DIR.mkdir(parents=True, exist_ok=True)
    METADATA_FILE.parent.mkdir(parents=True, exist_ok=True)

def load_metadata() -> MetadataStore:
    """Load existing metadata or create new if doesn't exist."""
    try:
        with open(METADATA_FILE) as f:
            data = json.load(f)
            return MetadataStore.model_validate(data)
    except FileNotFoundError:
        return MetadataStore()

def save_metadata(metadata: MetadataStore):
    """Save metadata to file."""
    metadata.last_updated = datetime.now()
    with open(METADATA_FILE, "w") as f:
        json.dump(metadata.model_dump(mode='json'), f, indent=2)

def prompt_for_metadata(existing_data: Optional[DocumentMetadata] = None) -> dict:
    """Interactive prompt for document metadata using questionary."""
    
    # State selection with autocomplete
    state = questionary.autocomplete(
        "State code:",
        choices=VALID_STATES,
        default=existing_data.state if existing_data else "",
        validate=lambda x: x.upper() in VALID_STATES
    ).ask()
    
    # Client code with validation
    client_code = questionary.text(
        "Client code (3 letters):",
        default=existing_data.client_code if existing_data else "",
        validate=lambda x: len(x) == 3 and x.isalpha()
    ).ask()
    
    # Base type selection
    base_type = questionary.select(
        "Base type:",
        choices=VALID_BASE_TYPES,
        default=existing_data.base_type if existing_data else "NEW"
    ).ask()
    
    # Optional description
    description = questionary.text(
        "Description (optional, use-hyphens-for-spaces):",
        default=existing_data.description if existing_data else ""
    ).ask()
    
    # Product categories with checkboxes
    product_categories = questionary.checkbox(
        "Select product categories:",
        choices=VALID_PRODUCT_CATEGORIES,
        default=[cat for cat in VALID_PRODUCT_CATEGORIES 
                if existing_data and cat in existing_data.product_categories]
    ).ask()
    
    return {
        "state": state,
        "client_code": client_code,
        "base_type": base_type,
        "description": description,
        "product_categories": product_categories
    }

@click.group()
def cli():
    """Document labeling system for classification testing."""
    ensure_directories()

@cli.command()
@click.argument('document_path', type=click.Path(exists=True, path_type=pathlib.Path), required=False)
def label(document_path=None):
    """
    Label a document for testing. If no path provided, process all documents in _to_label directory.
    """
    metadata = load_metadata()
    
    if document_path:
        # Single document mode
        process_single_document(document_path, metadata)
    else:
        # Batch mode - process all documents in to_label directory
        docs_to_label = list(TO_LABEL_DIR.glob("*.pdf"))
        if not docs_to_label:
            console.print("[yellow]No documents found in _to_label directory.[/yellow]")
            return
            
        for doc_path in track(docs_to_label, description="Processing documents..."):
            process_single_document(doc_path, metadata, batch_mode=True)

def process_single_document(doc_path: pathlib.Path, metadata: MetadataStore, batch_mode=False):
    """Process a single document for labeling."""
    console.print(f"\n[bold blue]Labeling document:[/bold blue] {doc_path.name}")
    
    # Determine if this is an external document that needs to be copied
    is_external = TO_LABEL_DIR not in doc_path.parents
    
    doc_key = doc_path.name
    existing_data = metadata.documents.get(doc_key)
    
    try:
        # Get metadata through interactive prompts
        meta_data = prompt_for_metadata(existing_data)
        
        # Generate standardized filename
        new_filename = f"{meta_data['state']}-{meta_data['client_code']}-{meta_data['base_type']}"
        if meta_data['description']:
            new_filename += f"-{meta_data['description']}"
        new_filename += ".pdf"
        
        # Create document metadata
        doc_entry = DocumentMetadata(
            **meta_data,
            expected_filename=new_filename
        )
        
        # Copy/move document to labeled directory
        target_path = LABELED_DIR / new_filename
        try:
            if is_external:
                shutil.copy2(str(doc_path), str(target_path))
                console.print(f"[green]Copied document to:[/green] {target_path}")
            else:
                shutil.move(str(doc_path), str(target_path))
                console.print(f"[green]Moved document to:[/green] {target_path}")
        except Exception as e:
            console.print(f"[red]Error moving/copying file:[/red] {e}")
            return
        
        # Save updated metadata
        metadata.documents[new_filename] = doc_entry
        save_metadata(metadata)
        
        console.print(f"[green]Successfully labeled as:[/green] {new_filename}")
        
    except ValueError as e:
        console.print(f"[red]Validation error:[/red] {str(e)}")
        if not batch_mode:
            if questionary.confirm("Would you like to try again?", default=True).ask():
                process_single_document(doc_path, metadata, batch_mode)

@cli.command()
def list():
    """List all labeled documents and their metadata."""
    metadata = load_metadata()
    
    if not metadata.documents:
        console.print("[yellow]No labeled documents found.[/yellow]")
        return
    
    table = Table(title="Labeled Documents")
    table.add_column("Filename", style="cyan")
    table.add_column("State", style="magenta")
    table.add_column("Type", style="green")
    table.add_column("Client", style="yellow")
    table.add_column("Categories", style="blue")
    
    for doc_name, doc_data in metadata.documents.items():
        table.add_row(
            doc_name,
            doc_data.state,
            doc_data.base_type,
            doc_data.client_code,
            ", ".join(doc_data.product_categories)
        )
    
    console.print(table)

@cli.command()
def status():
    """Show status of documents waiting to be labeled."""
    to_label = list(TO_LABEL_DIR.glob("*.pdf"))
    labeled = list(LABELED_DIR.glob("*.pdf"))
    
    console.print(f"\n[bold]Documents Status:[/bold]")
    console.print(f"Waiting to be labeled: [yellow]{len(to_label)}[/yellow]")
    console.print(f"Successfully labeled: [green]{len(labeled)}[/green]")
    
    if to_label:
        console.print("\n[bold]Documents waiting for labels:[/bold]")
        for doc in to_label:
            console.print(f"- {doc.name}")

if __name__ == '__main__':
    cli() 