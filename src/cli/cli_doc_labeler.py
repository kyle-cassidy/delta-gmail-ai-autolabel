#!/usr/bin/env python3
"""Document Labeler CLI (Refactored)"""

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
import builtins  # Import builtins

# --- Constants and Configuration ---
console = Console()

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
        "qmark": f'{MOCHA["mauve"]} bold',
        "question": f'{MOCHA["lavender"]} bold',
        "answer": f'bold {MOCHA["green"]}',
        "pointer": f'bold {MOCHA["peach"]}',
        "highlighted": "",
        "selected": "",
        "separator": MOCHA["overlay0"],
        "instruction": MOCHA["overlay1"],
        "text": MOCHA["text"],
        "input": f'{MOCHA["text"]} bold',
        "choice": MOCHA["text"],
        "choice-selected": f'{MOCHA["text"]}',
        "valid": MOCHA["green"],
        "invalid": MOCHA["red"],
        "completion-menu": f'bg:{MOCHA["surface0"]}',
        "completion-item": MOCHA["text"],
        "completion-item selected": f'bg:{MOCHA["surface1"]} {MOCHA["text"]}',
    }
)


class Config:
    """Configuration settings for the application."""

    BASE_DIR = pathlib.Path("tests/fixtures/documents")
    TO_LABEL_DIR = BASE_DIR / "_to_label"
    LABELED_DIR = BASE_DIR / "labeled_documents/documents"
    METADATA_FILE = BASE_DIR / "labeled_documents/metadata.json"
    VALID_STATES = [
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
    CLIENT_CHOICES = {
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

    BASE_TYPE_DESCRIPTIONS = {
        "NEW": "New Registration",
        "RENEW": "Renewal",
        "TONNAGE": "Tonnage Report",
        "CERT": "Certificate",
        "LABEL": "Label Review",
    }
    VALID_BASE_TYPES = list(BASE_TYPE_DESCRIPTIONS.keys())
    VALID_PRODUCT_CATEGORIES = [
        "Biostimulants",
        "Commercial Fertilizers",
        "Plant and Soil Amendments",
        "Liming Materials",
        "Organic Input Materials",
    ]
    CLIENT_INFO = {  # Example - ideally loaded from a separate file
        "ARB": {
            "name": "Arborjet, Inc.",
            "contact_info": {
                "primary_contact": "Nicholas Millen",
                "email": "nmillen@arborjet.com",
            },
            "metadata": {"active_states": ["MA"]},
        }
    }

    @classmethod
    def get_client_choices_list(cls) -> List[str]:
        """Returns a formatted list of client choices."""
        return [f"{code}: {name}" for code, name in sorted(cls.CLIENT_CHOICES.items())]

    @classmethod
    def get_client_name(cls, client_code: str) -> str:
        """Returns the name of the client given the client code."""
        return cls.CLIENT_CHOICES.get(client_code, "")

    @classmethod
    def get_base_type_choices(cls) -> List[Choice]:
        """Return formatted choices for base type selection."""
        return [
            Choice(title=f"{code}: {desc}", value=code)
            for code, desc in cls.BASE_TYPE_DESCRIPTIONS.items()
        ]

    @classmethod
    def get_product_category_choices(cls) -> List[Choice]:
        """Return formatted choices for product category selection."""
        return [
            Choice(title=category, value=category)
            for category in sorted(cls.VALID_PRODUCT_CATEGORIES)
        ]

    @classmethod
    def ensure_directories(cls) -> None:
        """Ensure required directories exist."""
        cls.TO_LABEL_DIR.mkdir(parents=True, exist_ok=True)
        cls.LABELED_DIR.mkdir(parents=True, exist_ok=True)
        cls.METADATA_FILE.parent.mkdir(parents=True, exist_ok=True)


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
        self._state = ""
        self._client_code = ""
        self._base_type = ""
        self.state = state
        self.client_code = client_code
        self.base_type = base_type
        self.description = description
        self.product_categories = product_categories or []
        self.expected_filename = expected_filename
        self.last_updated = last_updated or datetime.now()
        self._validate_product_categories()

    @property
    def state(self) -> str:
        return self._state

    @state.setter
    def state(self, value: str) -> None:
        value = value.upper().strip()
        if value not in Config.VALID_STATES:
            raise ValueError(
                f"Invalid state code. Must be one of: {', '.join(Config.VALID_STATES)}"
            )
        self._state = value

    @property
    def client_code(self) -> str:
        return self._client_code

    @client_code.setter
    def client_code(self, value: str) -> None:
        value = value.upper().strip()
        if len(value) != 3 or not value.isalpha() or value not in Config.CLIENT_CHOICES:
            raise ValueError("Invalid client code. Must be a 3-letter valid code.")
        self._client_code = value

    @property
    def base_type(self) -> str:
        return self._base_type

    @base_type.setter
    def base_type(self, value: str) -> None:
        value = value.upper().strip()
        if value not in Config.VALID_BASE_TYPES:
            raise ValueError(
                f"Invalid base type. Must be one of: {', '.join(Config.VALID_BASE_TYPES)}"
            )
        self._base_type = value

    def _validate_product_categories(self) -> None:
        """Validate the provided product categories."""
        invalid = [
            cat
            for cat in self.product_categories
            if cat not in Config.VALID_PRODUCT_CATEGORIES
        ]
        if invalid:
            raise ValueError(
                f"Invalid product categories: {', '.join(invalid)}. "
                f"Valid options: {', '.join(Config.VALID_PRODUCT_CATEGORIES)}"
            )


class MetadataStore:
    """Stores and manages document metadata."""

    def __init__(self, metadata_file: pathlib.Path = Config.METADATA_FILE):
        self.metadata_file = metadata_file
        self.documents: Dict[str, DocumentMetadata] = {}
        self.last_updated: Optional[datetime] = None
        self.load()

    def load(self) -> None:
        """Load metadata from the JSON file."""
        try:
            with open(self.metadata_file, "r") as f:
                data = json.load(f)
                self.last_updated = datetime.fromisoformat(
                    data.get("last_updated", str(datetime.min))
                )

                for filename, meta in data.get("documents", {}).items():
                    try:
                        self.documents[filename] = DocumentMetadata(
                            state=meta["state"],
                            client_code=meta["client_code"],
                            base_type=meta["base_type"],
                            description=meta.get("description"),
                            product_categories=meta.get("product_categories", []),
                            expected_filename=meta["expected_filename"],
                            last_updated=datetime.fromisoformat(
                                meta.get("last_updated", str(datetime.min))
                            ),
                        )
                    except (KeyError, ValueError, TypeError) as e:
                        console.print(
                            f"[red]Invalid metadata entry {filename}: {e}[/red]"
                        )

        except (FileNotFoundError, json.JSONDecodeError):
            self.last_updated = datetime.min  # Initialize if file doesn't exist

    def save(self) -> None:
        """Save metadata to the JSON file."""
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
                for filename, doc in self.documents.items()
            },
        }
        with open(self.metadata_file, "w") as f:
            json.dump(serialized, f, indent=2)

    def add_or_update(self, filename: str, metadata: DocumentMetadata) -> None:
        """Add or update a document's metadata."""
        self.documents[filename] = metadata
        self.save()

    def get(self, filename: str) -> Optional[DocumentMetadata]:
        """Retrieve metadata for a given filename."""
        return self.documents.get(filename)


class FileHandler:
    """Handles file operations."""

    @staticmethod
    def move_or_copy(
        src_path: pathlib.Path,
        target_dir: pathlib.Path,
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
        except (
            shutil.Error,
            OSError,
            PermissionError,
        ) as e:  # Catch specific file errors
            console.print(f"[red]Error moving/copying file:[/red] {e}")
            raise

    @staticmethod
    def generate_filename(meta_data: DocumentMetadata) -> str:
        """Generate a standardized filename."""
        filename = f"{meta_data.state}-{meta_data.client_code}-{meta_data.base_type}"
        if meta_data.description:
            filename += f"-{meta_data.description}"
        return filename + ".pdf"


class PromptHandler:
    """Handles user interaction for gathering metadata."""

    @staticmethod
    def prompt_for_metadata(
        existing_data: Optional[DocumentMetadata] = None,
    ) -> DocumentMetadata:
        """Prompt the user for document metadata, using existing data as defaults."""

        console.print(
            f"\n[bold {MOCHA['lavender']}]📄 Document Metadata Entry[/bold {MOCHA['lavender']}]"
        )

        # State
        console.print(
            f"┌─ [bold {MOCHA['overlay1']}]Step 1 of 4:[/bold {MOCHA['overlay1']}] Basic Information\n"
        )
        # Use questionary.prompt with a list of questions
        questions = [
            {
                "type": "autocomplete",
                "name": "state",  # Use a name for each question
                "message": "State code:",
                "choices": Config.VALID_STATES,
                "default": existing_data.state if existing_data else "",
                "validate": lambda x: x.upper() in Config.VALID_STATES,
                "style": PROMPT_STYLE,
            }
        ]
        answers = questionary.prompt(questions, style=PROMPT_STYLE)
        state = answers["state"]

        # Client Code
        console.print()
        questions = [
            {
                "type": "autocomplete",
                "name": "client_code",
                "message": "Client code:",
                "choices": Config.get_client_choices_list(),
                "default": (f"{existing_data.client_code}" if existing_data else ""),
                "validate": lambda x: x.split(":")[0].strip().upper()
                in Config.CLIENT_CHOICES,
                "style": PROMPT_STYLE,
            }
        ]
        answers = questionary.prompt(questions, style=PROMPT_STYLE)

        client_code = answers["client_code"].split(":")[0].strip()

        # Display client info
        PromptHandler.display_client_info(client_code)

        # Base Type (Refactored for rawselect and correct highlighting)
        console.print(
            f"\n┌─ [bold {MOCHA['overlay1']}]Step 2 of 4:[/bold {MOCHA['overlay1']}] Document Type\n"
        )
        base_type_choices = Config.get_base_type_choices()
        default_base_type = (
            existing_data.base_type
            if existing_data and existing_data.base_type in Config.VALID_BASE_TYPES
            else "NEW"
        )

        # Find the index of the default base type.
        try:
            default_index = [c.value for c in base_type_choices].index(
                default_base_type
            )
        except ValueError:
            default_index = 0  # Fallback to the first item if not found.

        # Reorder the choices list to put the default item first.
        reordered_choices = (
            base_type_choices[default_index:] + base_type_choices[:default_index]
        )

        questions = [
            {
                "type": "rawselect",
                "name": "base_type",
                "message": "Select base type:",
                "choices": reordered_choices,  # Use the reordered list.
                "style": PROMPT_STYLE,
                "use_indicator": True,
            }
        ]
        answers = questionary.prompt(questions, style=PROMPT_STYLE)
        base_type = answers["base_type"]

        # Description
        console.print(
            f"\n┌─ [bold {MOCHA['overlay1']}]Step 3 of 4:[/bold {MOCHA['overlay1']}] Description\n"
        )
        questions = [
            {
                "type": "text",
                "name": "description",
                "message": "Description (optional, use-hyphens-for-spaces):",
                "default": existing_data.description if existing_data else "",
                "style": PROMPT_STYLE,
            }
        ]
        answers = questionary.prompt(questions, style=PROMPT_STYLE)
        description = answers["description"]

        if description:
            description = re.sub(r"\s+", "-", description.lower())
            description = re.sub(r"[^\w-]", "", description)

        # Product Categories (Refactored for custom handling)
        console.print(
            f"\n┌─ [bold {MOCHA['overlay1']}]Step 4 of 4:[/bold {MOCHA['overlay1']}] Categories\n"
        )
        category_choices = Config.get_product_category_choices()
        selected_categories = []
        if existing_data and existing_data.product_categories:
            selected_categories = [
                cat
                for cat in existing_data.product_categories
                if cat in Config.VALID_PRODUCT_CATEGORIES
            ]

        choices_with_selection = [
            Choice(
                title=(
                    f"[X] {category}"
                    if category in selected_categories
                    else f"[ ] {category}"
                ),
                value=category,
            )
            for category in Config.VALID_PRODUCT_CATEGORIES
        ] + [Choice(title="[Done]", value="__DONE__")]
        questions = [
            {
                "type": "rawselect",
                "name": "product_categories",
                "message": "Select product categories (Enter to toggle, [Done] to finish):",
                "choices": choices_with_selection,
                "style": PROMPT_STYLE,
                "use_indicator": True,
            }
        ]
        selected_category = questionary.prompt(questions, style=PROMPT_STYLE)[
            "product_categories"
        ]

        if (
            selected_category != "__DONE__"
        ):  # Only enter loop if user didn't immediately select done
            while True:  # Custom loop for category selection
                if selected_category == "__DONE__":
                    break
                elif selected_category in selected_categories:
                    selected_categories.remove(selected_category)  # Toggle off
                else:
                    selected_categories.append(selected_category)  # Toggle on

                choices_with_selection = [
                    Choice(
                        title=(
                            f"[X] {category}"
                            if category in selected_categories
                            else f"[ ] {category}"
                        ),
                        value=category,
                    )
                    for category in Config.VALID_PRODUCT_CATEGORIES
                ] + [Choice(title="[Done]", value="__DONE__")]

                questions = [
                    {
                        "type": "rawselect",
                        "name": "product_categories",
                        "message": "Select product categories (Enter to toggle, [Done] to finish):",
                        "choices": choices_with_selection,
                        "style": PROMPT_STYLE,
                        "use_indicator": True,
                    }
                ]

                selected_category = questionary.prompt(questions, style=PROMPT_STYLE)[
                    "product_categories"
                ]

        console.print(
            f"\n[bold {MOCHA['green']}]✓ Metadata collection complete![/bold {MOCHA['green']}]\n"
        )
        product_categories = selected_categories
        # Create and return a new DocumentMetadata object
        return DocumentMetadata(
            state=state,
            client_code=client_code,
            base_type=base_type,
            description=description,
            product_categories=product_categories,
            expected_filename="",  # Placeholder, will be filled later.
        )

    @staticmethod
    def display_client_info(client_code: str) -> None:
        """Displays client information if available."""
        client_info = Config.CLIENT_INFO.get(client_code)
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


class DocumentLabeler:
    """Main class to handle the document labeling process."""

    def __init__(self):
        self.config = Config()
        self.metadata_store = MetadataStore()
        self.file_handler = FileHandler()
        Config.ensure_directories()

    def label_documents(
        self, document_paths: List[pathlib.Path], batch_mode: bool = False
    ) -> None:
        """Label one or more documents."""
        if not document_paths:
            document_paths = list(self.config.TO_LABEL_DIR.glob("*.pdf"))
            if not document_paths:
                console.print(
                    "[yellow]No documents found in _to_label directory.[/yellow]"
                )
                return
            batch_mode = True  # If processing the _to_label dir, it's batch mode

        for doc_path in track(
            document_paths,
            description="Processing documents...",
            disable=not batch_mode,
        ):
            self.process_single_document(doc_path, batch_mode)

    def process_single_document(self, doc_path: str, batch_mode: bool) -> None:
        """Process a single document."""
        # Convert the string path back to a Path object.
        doc_path_obj = pathlib.Path(doc_path)
        console.print(
            f"\n[bold blue]Labeling document:[/bold blue] {doc_path_obj.name}"
        )
        is_external = self.config.TO_LABEL_DIR not in doc_path_obj.parents
        existing_data = self.metadata_store.get(doc_path_obj.name)

        try:
            metadata = PromptHandler.prompt_for_metadata(existing_data)
            metadata.expected_filename = self.file_handler.generate_filename(metadata)
            self.file_handler.move_or_copy(
                doc_path_obj,
                self.config.LABELED_DIR,
                metadata.expected_filename,
                is_external,
            )
            self.metadata_store.add_or_update(metadata.expected_filename, metadata)
            console.print(
                f"[green]Successfully labeled as:[/green] {metadata.expected_filename}"
            )
        except ValueError as e:
            self.handle_labeling_error(
                e, doc_path_obj, batch_mode
            )  # Pass Path object here too

    def handle_labeling_error(
        self, error: Exception, doc_path: pathlib.Path, batch_mode: bool
    ) -> None:
        """Handle errors during labeling."""
        console.print(f"[red]Validation error:[/red] {error}")
        if (
            not batch_mode
            and questionary.confirm("Would you like to try again?", default=True).ask()
        ):
            self.process_single_document(doc_path, batch_mode)

    def list_documents(self) -> None:
        """List all labeled documents and their metadata."""
        if not self.metadata_store.documents:
            console.print("[yellow]No labeled documents found.[/yellow]")
            return

        table = Table(title="Labeled Documents")
        table.add_column("Filename", style="cyan")
        table.add_column("State", style="magenta")
        table.add_column("Type", style="green")
        table.add_column("Client", style="yellow")
        table.add_column("Categories", style="blue")

        for doc_name, doc_data in self.metadata_store.documents.items():
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

    def show_status(self) -> None:
        """Show the status of documents."""
        to_label = list(self.config.TO_LABEL_DIR.glob("*.pdf"))
        labeled = list(self.config.LABELED_DIR.glob("*.pdf"))

        console.print(f"\n[bold]Documents Status:[/bold]")
        console.print(f"Waiting to be labeled: [yellow]{len(to_label)}[/yellow]")
        console.print(f"Successfully labeled: [green]{len(labeled)}[/green]")

        if to_label:
            console.print("\n[bold]Documents waiting for labels:[/bold]")
            for doc in to_label:
                console.print(f"- {doc.name}")


# --- Click CLI ---
@click.group()
def cli():
    """Document labeling system."""
    pass


@cli.command()
@click.argument(
    "document_paths", nargs=-1, type=click.Path(exists=True, path_type=pathlib.Path)
)
def label(document_paths: List[pathlib.Path]):
    """Label one or more documents."""
    labeler = DocumentLabeler()
    # Convert Path objects to strings before passing to label_documents
    labeler.label_documents([str(path) for path in document_paths])


@cli.command()
def list():
    """List all labeled documents."""
    labeler = DocumentLabeler()
    labeler.list_documents()


@cli.command()
def status():
    """Show the status of documents."""
    labeler = DocumentLabeler()
    labeler.show_status()


if __name__ == "__main__":
    cli()
