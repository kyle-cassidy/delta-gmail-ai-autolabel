#!/usr/bin/env python3

import click
import json
import yaml
import shutil
import pathlib
import re
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

class DocumentMetadata(BaseModel):
    """Pydantic model for document metadata."""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    state: str = Field(..., description="Two-letter state code")
    client_code: str = Field(..., description="Three-letter client code")
    base_type: str = Field(..., description="Document base type")
    description: Optional[str] = Field(None, description="Optional description")
    product_categories: List[str] = Field(
        default_factory=list,
        description="List of product categories"
    )
    expected_filename: str = Field(..., description="Expected standardized filename")
    last_updated: datetime = Field(default_factory=datetime.now)
    
    @field_validator("state")
    def validate_state(cls, v: str) -> str:
        v = v.upper()
        if v not in get_valid_states():
            raise ValueError(f"Invalid state code. Must be one of: {', '.join(get_valid_states())}")
        return v
    
    @field_validator("client_code")
    def validate_client_code(cls, v: str) -> str:
        v = v.upper()
        if len(v) != 3:
            raise ValueError("Client code must be exactly 3 letters")
        if not v.isalpha():
            raise ValueError("Client code must contain only letters")
        if v not in get_valid_client_codes():
            raise ValueError(f"Invalid client code. Must be one of: {', '.join(get_valid_client_codes())}")
        return v
    
    @field_validator("base_type")
    def validate_base_type(cls, v: str) -> str:
        v = v.upper()
        if v not in get_valid_base_types():
            raise ValueError(f"Invalid base type. Must be one of: {', '.join(get_valid_base_types())}")
        return v
    
    @field_validator("product_categories")
    def validate_product_categories(cls, v: List[str]) -> List[str]:
        valid_categories = get_valid_product_categories()
        invalid_categories = [cat for cat in v if cat not in valid_categories]
        if invalid_categories:
            raise ValueError(
                f"Invalid product categories: {', '.join(invalid_categories)}. "
                f"Must be one of: {', '.join(valid_categories)}"
            )
        return v

class MetadataStore(BaseModel):
    """Pydantic model for the metadata store."""
    documents: Dict[str, DocumentMetadata] = Field(default_factory=dict)
    last_updated: Optional[datetime] = None

def load_yaml_config(filename: str) -> dict:
    """Load a YAML configuration file."""
    config_path = pathlib.Path("src/config") / filename
    try:
        with open(config_path) as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        console.print(f"[yellow]Warning: Config file {filename} not found[/yellow]")
        return {}

def get_valid_states() -> List[str]:
    """Get list of valid states from config."""
    # For now, return a fixed list of states until we have proper state config
    return sorted([
        "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
        "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
        "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
        "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
        "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
    ])

def get_valid_client_codes() -> List[str]:
    """Get list of valid client codes from config."""
    config = load_yaml_config("clients.yaml")
    return sorted(list(config.get("companies", {}).keys()))

def get_valid_base_types() -> List[str]:
    """Get list of valid base types from config."""
    # For now, return a fixed list until we have proper base type config
    return [
        "NEW",      # New Registration
        "RENEW",    # Renewal
        "TONNAGE",  # Tonnage Report
        "CERT",     # Certificate
        "LABEL"     # Label Review
    ]

def get_valid_product_categories() -> List[str]:
    """Get list of valid product categories from config."""
    # For now, return a fixed list until we have proper category config
    return sorted([
        "Commercial Fertilizers",
        "Plant and Soil Amendments",
        "Biostimulants",
        "Liming Materials",
        "Organic Input Materials"
    ])

def get_client_info(client_code: str) -> dict:
    """Get detailed information about a client."""
    config = load_yaml_config("clients.yaml")
    return config.get("companies", {}).get(client_code, {})

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

def get_client_choices() -> List[Choice]:
    """Get formatted choices for client selection."""
    clients = load_yaml_config("clients.yaml").get("companies", {})
    choices = []
    for code, info in sorted(clients.items()):
        name = info.get("name", "")
        choices.append(Choice(
            title=f"{code}: {name}",
            value=code
        ))
    return choices

def get_base_type_choices() -> List[Choice]:
    """Get formatted choices for base type selection."""
    descriptions = {
        "NEW": "New Registration",
        "RENEW": "Renewal",
        "TONNAGE": "Tonnage Report",
        "CERT": "Certificate",
        "LABEL": "Label Review"
    }
    return [
        Choice(title=f"{code}: {desc}", value=code)
        for code, desc in descriptions.items()
    ]

def get_product_category_choices() -> List[Choice]:
    """Get formatted choices for product category selection."""
    return [
        Choice(title=category, value=category)
        for category in get_valid_product_categories()
    ]

def prompt_for_metadata(existing_data: Optional[DocumentMetadata] = None) -> dict:
    """Interactive prompt for document metadata using questionary."""
    
    # State selection with autocomplete
    valid_states = get_valid_states()
    state = questionary.autocomplete(
        "State code:",
        choices=valid_states,
        default=existing_data.state if existing_data else "",
        validate=lambda x: x.upper() in valid_states
    ).ask()
    
    # Client selection with search
    client_code = questionary.select(
        "Select client:",
        choices=get_client_choices(),
        default=existing_data.client_code if existing_data else None
    ).ask()
    
    # Show client info
    client_info = get_client_info(client_code)
    if client_info:
        console.print("\n[bold]Client Information:[/bold]")
        console.print(f"Name: {client_info.get('name', '')}")
        console.print(f"Contact: {client_info.get('contact_info', {}).get('primary_contact', '')}")
        console.print(f"Email: {client_info.get('contact_info', {}).get('email', '')}")
        console.print(f"Active States: {', '.join(client_info.get('metadata', {}).get('active_states', []))}\n")
    
    # Base type selection with descriptions
    base_type = questionary.select(
        "Select base type:",
        choices=get_base_type_choices(),
        default=existing_data.base_type if existing_data else "NEW"
    ).ask()
    
    # Optional description
    description = questionary.text(
        "Description (optional, use-hyphens-for-spaces):",
        default=existing_data.description if existing_data else ""
    ).ask()
    
    # Product categories with checkboxes
    category_choices = get_product_category_choices()
    
    # Set default categories
    if existing_data and existing_data.product_categories:
        default_categories = existing_data.product_categories
    else:
        default_categories = [category_choices[0].value] if category_choices else []
        
    product_categories = questionary.checkbox(
        "Select product categories:",
        choices=category_choices,
        default=default_categories
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