#!/usr/bin/env python3
"""
Document Labeler CLI

This script allows you to label documents by interactively gathering metadata
about each document. It validates the user input, generates a standardized
filename, moves (or copies) the document to the proper directory, and then
updates a metadata JSON file for future reference.
"""

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
import questionary
from questionary import Choice
from prompt_toolkit.styles import Style
import builtins

console = Console()

# Directory structure
BASE_DIR = pathlib.Path("tests/fixtures/documents")
TO_LABEL_DIR = BASE_DIR / "_to_label"
LABELED_DIR = BASE_DIR / "labeled_documents/documents"
METADATA_FILE = BASE_DIR / "labeled_documents/metadata.json"


# Catppuccin Mocha palette
MOCHA = {
    "rosewater": "#f5e0dc",
    "flamingo": "#f2cdcd",
    "pink": "#f5c2e7",
    "mauve": "#cba6f7",
    "red": "#f38ba8",
    "maroon": "#eba0ac",
    "peach": "#fab387",
    "yellow": "#f9e2af",
    "green": "#a6e3a1",
    "teal": "#94e2d5",
    "sky": "#89dceb",
    "sapphire": "#74c7ec",
    "blue": "#89b4fa",
    "lavender": "#b4befe",
    "text": "#cdd6f4",
    "subtext1": "#bac2de",
    "subtext0": "#a6adc8",
    "overlay2": "#9399b2",
    "overlay1": "#7f849c",
    "overlay0": "#6c7086",
    "surface2": "#585b70",
    "surface1": "#45475a",
    "surface0": "#313244",
    "base": "#1e1e2e",
    "mantle": "#181825",
    "crust": "#11111b",
}

PROMPT_STYLE = Style.from_dict(
    {
        # Base components
        "qmark": f'{MOCHA["mauve"]} bold',  # Question mark
        "question": f'{MOCHA["lavender"]} bold',  # Question text
        "answer": f'bold {MOCHA["green"]}',  # Selected answer appearance
        "pointer": f'bold {MOCHA["peach"]}',  # Make the pointer (arrow) more visible
        "highlighted": "",  # Better contrast for highlighted item
        "selected": "",  # More subtle highlight for selected item
        "separator": MOCHA["overlay0"],  # Separator in lists
        "instruction": MOCHA["overlay1"],  # Instructions/help text
        # Input components
        "text": MOCHA["text"],  # Regular text
        "input": f'{MOCHA["text"]} bold',  # User input text
        # Choice components
        "choice": MOCHA["text"],  # Normal choice appearance
        "choice-selected": f'{MOCHA["text"]}',  # Selected choice appearance
        # Default validators
        "valid": MOCHA["green"],  # Valid input
        "invalid": MOCHA["red"],  # Invalid input
        # Completion components
        "completion-menu": f'bg:{MOCHA["surface0"]}',
        "completion-item": MOCHA["text"],
        "completion-item selected": f'bg:{MOCHA["surface1"]} {MOCHA["text"]}',
    }
)


class DocumentMetadata:
    """Holds metadata for a document and validates its fields."""

    def __init__(
        self,
        state: str,
        client_code: str,
        base_type: str,
        expected_filename: str,
        description: Optional[str] = None,
        product_categories: Optional[List[str]] = None,
        last_updated: Optional[datetime] = None,
    ):
        self.state = validate_state(state)
        self.client_code = validate_client_code(client_code)
        self.base_type = validate_base_type(base_type)
        self.description = description
        self.product_categories = product_categories or []
        self.expected_filename = expected_filename
        self.last_updated = last_updated or datetime.now()

        # Validate product categories after assignment.
        validate_product_categories(self.product_categories)


class MetadataStore:
    """Stores all document metadata."""

    def __init__(self):
        self.documents: Dict[str, DocumentMetadata] = {}
        self.last_updated: Optional[datetime] = None


def load_yaml_config(filename: str) -> dict:
    """Load a YAML configuration file from the src/config directory."""
    config_path = pathlib.Path("src/config") / filename
    try:
        with open(config_path, "r") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        console.print(f"[yellow]Warning: Config file {filename} not found[/yellow]")
        return {}


def get_valid_states() -> List[str]:
    """Return a sorted list of valid state codes."""
    return sorted(
        [
            "AL",
            "AK",
            "AZ",
            "AR",
            "CA",
            "CO",
            "CT",
            "DE",
            "FL",
            "GA",
            "HI",
            "ID",
            "IL",
            "IN",
            "IA",
            "KS",
            "KY",
            "LA",
            "ME",
            "MD",
            "MA",
            "MI",
            "MN",
            "MS",
            "MO",
            "MT",
            "NE",
            "NV",
            "NH",
            "NJ",
            "NM",
            "NY",
            "NC",
            "ND",
            "OH",
            "OK",
            "OR",
            "PA",
            "RI",
            "SC",
            "SD",
            "TN",
            "TX",
            "UT",
            "VT",
            "VA",
            "WA",
            "WV",
            "WI",
            "WY",
        ]
    )


def get_client_choices_dict() -> Dict[str, str]:
    """Return a dictionary of client codes and names."""
    return {
        "AAS": "Able Ag Solutions, LLC",
        "AGR": "Agrauxine Corp.",
        "AND": "Andermatt US",
        "AQB": "AquaBella Organic Solutions LLC",
        "AQT": "Aquatrols Corp of American",
        "ARB": "Arborjet, Inc.",
        "BIN": "Bio Insumos Nativa SpA",
        "BIO": "BIOVERT SL",
        "BOR": "U.S. Borax Inc.",
        "BPT": "BioPro Technologies, LLC",
        "CLI": "Cytozyme Laboratories, Inc",
        "COM": "Comerco",
        "COR": "Corteva Agriscience LLC",
        "DED": "dedetec",
        "DEL": "Delta Analytical Corporation",
        "ECO": "Ecologel Solutions, LLC",
        "EEA": "Elemental Enzymes Ag and Turf, LLC",
        "GRN": "Greenwise Turf and Ag Solutions",
        "GWB": "Groundwork BioAg Ltd",
        "HIC": "Hi Cell Crop Science PVt. Ltd",
        "IBA": "Indogulf BioAg",
        "KIT": "KitoZyme",
        "KOC": "Kocide / Speiss-Urania",
        "LAM": "Lamberti, Inc",
        "LOC": "Locus Agriculture Solutions",
        "MAN": "Manvert USA LLC",
        "NLS": "NewLeaf Symbiotics",
        "OMC": "Omya Canada",
        "OMY": "Omya Inc.",
        "P66": "Phillips 66",
        "PET": "Petglow",
        "PLL": "Precision Laboratories Ltd",
        "PRO": "Probelte S.A.U.",
        "PVT": "Pivot Bio, Inc.",
        "ROY": "Royal Brinkman Canada",
        "SAG": "Solstice Agriculture, LLC",
        "SEI": "SEIPASA, S.A.",
        "SYM": "Symborg Inc",
        "TBP": "ThinkBio PTY",
        "VLS": "Verdesian Life Sciences US LLC",
        "ZZZ": "Company Automation Tester",
    }


def get_base_type_choices() -> List[Choice]:
    """Return formatted choices for base type selection."""
    descriptions = {
        "NEW": "New Registration",
        "RENEW": "Renewal",
        "TONNAGE": "Tonnage Report",
        "CERT": "Certificate",
        "LABEL": "Label Review",
    }
    return [
        Choice(title=f"{code}: {desc}", value=code)
        for code, desc in descriptions.items()
    ]


def get_client_info(client_code: str) -> dict:
    """Return detailed client information based on client code."""
    # Hardcoded client information
    clients_info = {
        "ARB": {
            "name": "Arborjet, Inc.",
            "contact_info": {
                "primary_contact": "Nicholas Millen",
                "email": "nmillen@arborjet.com",
            },
            "metadata": {"active_states": ["MA"]},
        }
        # Add other clients as needed
    }
    return clients_info.get(client_code, {})


def get_valid_client_codes() -> List[str]:
    """Return a sorted list of valid client codes."""
    return sorted(
        [
            "AAS",
            "AGR",
            "AND",
            "AQB",
            "AQT",
            "ARB",
            "BIN",
            "BIO",
            "BOR",
            "BPT",
            "CLI",
            "COM",
            "COR",
            "DED",
            "DEL",
            "ECO",
            "EEA",
            "GRN",
            "GWB",
            "HIC",
            "IBA",
            "KIT",
            "KOC",
            "LAM",
            "LOC",
            "MAN",
            "NLS",
            "OMC",
            "OMY",
            "P66",
            "PET",
            "PLL",
            "PRO",
            "PVT",
            "ROY",
            "SAG",
            "SEI",
            "SYM",
            "TBP",
            "VLS",
            "ZZZ",
        ]
    )


def get_valid_base_types() -> List[str]:
    """Return a list of valid base types."""
    return ["NEW", "RENEW", "TONNAGE", "CERT", "LABEL"]


def get_valid_product_categories() -> List[str]:
    """Return a sorted list of valid product categories."""
    return sorted(
        [
            "Biostimulants",
            "Commercial Fertilizers",
            "Plant and Soil Amendments",
            "Liming Materials",
            "Organic Input Materials",
        ]
    )


def get_product_category_choices() -> List[Choice]:
    """Return formatted choices for product category selection."""
    return [
        Choice(title=category, value=category)
        for category in get_valid_product_categories()
    ]


def ensure_directories() -> None:
    """Ensure required directories exist."""
    TO_LABEL_DIR.mkdir(parents=True, exist_ok=True)
    LABELED_DIR.mkdir(parents=True, exist_ok=True)
    METADATA_FILE.parent.mkdir(parents=True, exist_ok=True)


def validate_state(state: str) -> str:
    """Validate and format a state code."""
    state = state.upper().strip()
    if state not in get_valid_states():
        raise ValueError(
            f"Invalid state code. Must be one of: {', '.join(get_valid_states())}"
        )
    return state


def validate_client_code(code: str) -> str:
    """Validate and format a client code."""
    code = code.upper().strip()
    if len(code) != 3 or not code.isalpha():
        raise ValueError("Client code must be exactly 3 alphabetic letters")
    if code not in get_valid_client_codes():
        raise ValueError(
            f"Invalid client code. Must be one of: {', '.join(get_valid_client_codes())}"
        )
    return code


def validate_base_type(base_type: str) -> str:
    """Validate and format a base type."""
    base_type = base_type.upper().strip()
    if base_type not in get_valid_base_types():
        raise ValueError(
            f"Invalid base type. Must be one of: {', '.join(get_valid_base_types())}"
        )
    return base_type


def validate_product_categories(categories: List[str]) -> None:
    """Validate the provided product categories."""
    valid_categories = get_valid_product_categories()
    invalid = [cat for cat in categories if cat not in valid_categories]
    if invalid:
        raise ValueError(
            f"Invalid product categories: {', '.join(invalid)}. "
            f"Valid options: {', '.join(valid_categories)}"
        )


def load_metadata() -> MetadataStore:
    """Load existing metadata from file."""
    store = MetadataStore()
    try:
        with open(METADATA_FILE, "r") as f:
            data = json.load(f)
        last_updated_str = data.get("last_updated")
        if not last_updated_str:
            store.last_updated = datetime.min
        else:
            try:
                store.last_updated = datetime.fromisoformat(last_updated_str)
            except (ValueError, TypeError):
                store.last_updated = datetime.min

        for filename, meta in data.get("documents", {}).items():
            try:
                doc_last_updated = datetime.min
                if meta.get("last_updated"):
                    try:
                        doc_last_updated = datetime.fromisoformat(meta["last_updated"])
                    except (ValueError, TypeError):
                        pass

                store.documents[filename] = DocumentMetadata(
                    state=meta["state"],
                    client_code=meta["client_code"],
                    base_type=meta["base_type"],
                    description=meta.get("description"),
                    product_categories=meta.get("product_categories", []),
                    expected_filename=meta["expected_filename"],
                    last_updated=doc_last_updated,
                )
            except (KeyError, ValueError) as e:
                console.print(f"[red]Invalid metadata entry {filename}: {e}[/red]")
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return store


def save_metadata(metadata: MetadataStore) -> None:
    """Save the metadata store to a file."""
    serialized = {
        "last_updated": datetime.now().isoformat(),
        "documents": {
            filename: {
                "state": doc.state,
                "client_code": doc.client_code,
                "base_type": doc.base_type,
                "description": doc.description,
                "product_categories": doc.product_categories,
                "expected_filename": doc.expected_filename,
                "last_updated": doc.last_updated.isoformat(),
            }
            for filename, doc in metadata.documents.items()
        },
    }
    with open(METADATA_FILE, "w") as f:
        json.dump(serialized, f, indent=2)


def prompt_for_metadata(existing_data: Optional[DocumentMetadata] = None) -> dict:
    """Interactively prompt the user for document metadata."""
    console.print(
        f"\n[bold {MOCHA['lavender']}]📄 Document Metadata Entry[/bold {MOCHA['lavender']}]"
    )
    console.print(
        f"┌─ [bold {MOCHA['overlay1']}]Step 1 of 4:[/bold {MOCHA['overlay1']}] Basic Information\n"
    )

    # Get state code
    valid_states = get_valid_states()
    state = questionary.autocomplete(
        "State code:",
        choices=valid_states,
        default=existing_data.state if existing_data is not None else "",
        validate=lambda x: x.upper() in valid_states,
        style=PROMPT_STYLE,
    ).ask()

    console.print()  # Add vertical spacing

    # Get client code with company name
    valid_clients = [
        f"{code}: {name}" for code, name in sorted(get_client_choices_dict().items())
    ]
    client_response = questionary.autocomplete(
        "Client code:",
        choices=valid_clients,
        default=(f"{existing_data.client_code}" if existing_data is not None else ""),
        validate=lambda x: x.split(":")[0].strip().upper() in get_valid_client_codes(),
        style=PROMPT_STYLE,
    ).ask()
    client_code = client_response.split(":")[0].strip()

    # Display client information if available
    client_info = get_client_info(client_code)
    if client_info:
        console.print(
            f"\n[bold {MOCHA['overlay1']}]Client Information:[/bold {MOCHA['overlay1']}]"
        )
        console.print(
            f"[{MOCHA['text']}]Name:[/{MOCHA['text']}] [{MOCHA['green']}]{client_info.get('name', '')}[/{MOCHA['green']}]"
        )
        console.print(
            f"[{MOCHA['text']}]Contact:[/{MOCHA['text']}] [{MOCHA['green']}]{client_info.get('contact_info', {}).get('primary_contact', '')}[/{MOCHA['green']}]"
        )
        console.print(
            f"[{MOCHA['text']}]Email:[/{MOCHA['text']}] [{MOCHA['green']}]{client_info.get('contact_info', {}).get('email', '')}[/{MOCHA['green']}]"
        )
        console.print(
            f"[{MOCHA['text']}]Active States:[/{MOCHA['text']}] [{MOCHA['green']}]{', '.join(client_info.get('metadata', {}).get('active_states', []))}[/{MOCHA['green']}]\n"
        )

    # Base type selection using checkbox
    console.print(
        f"\n┌─ [bold {MOCHA['overlay1']}]Step 2 of 4:[/bold {MOCHA['overlay1']}] Document Type\n"
    )

    valid_base_types = get_valid_base_types()
    base_type_choices = get_base_type_choices()
    default_base_type = []
    if existing_data is not None and existing_data.base_type:
        if existing_data.base_type in valid_base_types:
            default_base_type = [existing_data.base_type]

    ### Base type using checkbox - restricting to single selection in post-processing
    selected_base_types = questionary.checkbox(
        "Select base type:",
        choices=base_type_choices,
        default=default_base_type if default_base_type else None,
        style=PROMPT_STYLE,
    ).ask()

    # Process selection to ensure only one type is selected
    base_type = None
    if selected_base_types and isinstance(selected_base_types, list):
        selected_base_types = [
            type_
            for type_ in selected_base_types
            if isinstance(type_, str) and type_ in valid_base_types
        ]
        if selected_base_types:
            base_type = selected_base_types[0]  # Take the first selected type

    # If no valid selection was made, default to NEW
    if not base_type:
        base_type = "NEW"
    # Get description
    console.print(
        f"\n┌─ [bold {MOCHA['overlay1']}]Step 3 of 4:[/bold {MOCHA['overlay1']}] Description\n"
    )

    ## Description
    description = questionary.text(
        "Description (optional, use-hyphens-for-spaces):",
        default=existing_data.description if existing_data is not None else "",
        style=PROMPT_STYLE,
    ).ask()

    if description:
        description = description.lower()
        description = re.sub(r"\s+", "-", description)
        description = re.sub(r"[^\w-]", "", description)

    # Get product categories
    console.print(
        f"\n┌─ [bold {MOCHA['overlay1']}]Step 4 of 4:[/bold {MOCHA['overlay1']}] Categories\n"
    )

    valid_categories = get_valid_product_categories()
    category_choices = get_product_category_choices()
    default_categories = []
    if existing_data is not None and existing_data.product_categories:
        default_categories = [
            cat for cat in existing_data.product_categories if cat in valid_categories
        ]

    # Get product categories using checkbox
    product_categories = questionary.checkbox(
        "Select product categories (optional):",
        choices=category_choices + [Choice(title="[Done]", value="__DONE__")],
        default=default_categories if default_categories else None,
        style=PROMPT_STYLE,
    ).ask()

    # Sanitize product categories
    if not product_categories or not isinstance(product_categories, list):
        product_categories = []
    else:
        product_categories = [
            cat
            for cat in product_categories
            if isinstance(cat, str) and cat in valid_categories and cat != "__DONE__"
        ]

    console.print(
        f"\n[bold {MOCHA['green']}]✓ Metadata collection complete![/bold {MOCHA['green']}]\n"
    )

    return {
        "state": state.upper(),
        "client_code": client_code.upper(),
        "base_type": base_type.upper(),
        "description": description or None,
        "product_categories": product_categories,
    }


def generate_filename(meta_data: dict) -> str:
    """
    Generate a standardized filename from the metadata dictionary.

    The filename is constructed in the following format:
      STATE-CLIENT-BASETYPE[-description].pdf
    """
    filename = (
        f"{meta_data['state']}-{meta_data['client_code']}-{meta_data['base_type']}"
    )
    if meta_data.get("description"):
        filename += f"-{meta_data['description']}"
    return filename + ".pdf"


@click.group()
def cli():
    """Document labeling system for classification testing."""
    ensure_directories()


@cli.command()
@click.argument(
    "document_path", nargs=-1, type=click.Path(exists=True, path_type=pathlib.Path)
)
def label(document_path):
    """
    Label one or more documents. If no paths are provided, process all documents in the _to_label directory.
    """
    metadata = load_metadata()
    if document_path:
        for path in document_path:
            process_single_document(path, metadata)
    else:
        docs_to_label = list(TO_LABEL_DIR.glob("*.pdf"))
        if not docs_to_label:
            console.print("[yellow]No documents found in _to_label directory.[/yellow]")
            return
        for doc_path in track(docs_to_label, description="Processing documents..."):
            process_single_document(doc_path, metadata, batch_mode=True)


def process_single_document(
    doc_path: pathlib.Path, metadata: MetadataStore, batch_mode: bool = False
) -> None:
    """Process a single document: prompt for metadata, generate a new filename, and update metadata."""
    console.print(f"\n[bold blue]Labeling document:[/bold blue] {doc_path.name}")
    is_external = TO_LABEL_DIR not in doc_path.parents
    doc_key = doc_path.name
    existing_data = metadata.documents.get(doc_key)

    try:
        meta_data = prompt_for_metadata(existing_data)
        new_filename = generate_filename(meta_data)
        doc_entry = DocumentMetadata(**meta_data, expected_filename=new_filename)
        handle_file_move(doc_path, new_filename, is_external)
        update_metadata(metadata, new_filename, doc_entry)
        console.print(f"[green]Successfully labeled as:[/green] {new_filename}")
    except ValueError as e:
        handle_labeling_error(e, doc_path, metadata, batch_mode)


def handle_file_move(
    src_path: pathlib.Path, new_filename: str, is_external: bool
) -> None:
    """Move or copy the file to the labeled directory."""
    target_path = LABELED_DIR / new_filename
    try:
        if is_external:
            shutil.copy2(str(src_path), str(target_path))
        else:
            shutil.move(str(src_path), str(target_path))
        console.print(
            f"[green]{'Copied' if is_external else 'Moved'} document to:[/green] {target_path}"
        )
    except Exception as e:
        console.print(f"[red]Error moving file:[/red] {e}")
        raise


def update_metadata(
    metadata: MetadataStore, filename: str, entry: DocumentMetadata
) -> None:
    """Update the metadata store and save changes."""
    metadata.documents[filename] = entry
    save_metadata(metadata)


def handle_labeling_error(
    error: Exception, doc_path: pathlib.Path, metadata: MetadataStore, batch_mode: bool
) -> None:
    """Display the error and, if appropriate, allow the user to retry labeling."""
    console.print(f"[red]Validation error:[/red] {error}")
    if (
        not batch_mode
        and questionary.confirm("Would you like to try again?", default=True).ask()
    ):
        process_single_document(doc_path, metadata)


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
            (
                ", ".join(doc_data.product_categories)
                if doc_data.product_categories
                else "None"
            ),
        )
    console.print(table)


@cli.command()
def status():
    """Show the status of documents waiting to be labeled."""
    to_label = list(TO_LABEL_DIR.glob("*.pdf"))
    labeled = list(LABELED_DIR.glob("*.pdf"))

    console.print(f"\n[bold]Documents Status:[/bold]")
    console.print(f"Waiting to be labeled: [yellow]{len(to_label)}[/yellow]")
    console.print(f"Successfully labeled: [green]{len(labeled)}[/green]")

    if to_label:
        console.print("\n[bold]Documents waiting for labels:[/bold]")
        for doc in to_label:
            console.print(f"- {doc.name}")


if __name__ == "__main__":
    cli()
