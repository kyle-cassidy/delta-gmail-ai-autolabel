#!/usr/bin/env python3
"""
Document Classification & Labeling CLI Tool

This tool watches an incoming_documents folder for new files.
When a new document is detected, it:
  • Extracts text from the file (e.g. via pdfminer for PDFs)
  • Hands the text off to the classification service which generates a set of labels
  • Renames the file to include these classification labels
  • Moves the file to a processed_documents folder

Configuration parameters (such as attachment parsing settings and classification thresholds)
are loaded from YAML files in the config/ directory.
"""

import os
import sys
import time
import shutil
import logging
import yaml
import click
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import asyncio

# Import our client and service modules (assumed to exist)
from src.client.attachment import extract_text
from src.services.classification_service import ClassificationService

# Set up basic logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Directories
CONFIG_DIR = Path("config")
INCOMING_DIR = Path("incoming_documents")
PROCESSED_DIR = Path("processed_documents")

# Supported file types
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}

def ensure_directories() -> None:
    """Ensure that the required directories exist."""
    for directory in (CONFIG_DIR, INCOMING_DIR, PROCESSED_DIR):
        directory.mkdir(parents=True, exist_ok=True)
        logging.debug(f"Ensured directory exists: {directory}")

def load_yaml_config(filename: str) -> dict:
    """
    Load a YAML configuration file from the config/ directory.
    Returns an empty dictionary if the file does not exist.
    """
    config_path = CONFIG_DIR / filename
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f) or {}
            logging.debug(f"Loaded configuration from {config_path}")
            return config
    except FileNotFoundError:
        logging.warning(f"Config file {filename} not found in {CONFIG_DIR}.")
        return {}

def load_all_configs() -> dict:
    """
    Load all relevant YAML configuration files.
    You can adjust the filenames as necessary.
    """
    configs = {
        "email_classification": load_yaml_config("email_classification.yaml"),
        "regulatory_actions": load_yaml_config("regulatory_actions.yaml"),
        "product_categories": load_yaml_config("product_categories.yaml"),
        # Add other configuration files as needed
    }
    return configs

# Load configurations once at startup
CONFIGS = load_all_configs()

def generate_new_filename(original_path: Path, labels: list) -> Path:
    """
    Generate a new filename by appending the classification labels to the original filename.
    Example:
      Original: report.pdf
      Labels: ["client:DUMMY_CLIENT", "type:undetermined"]
      New filename: report__client-DUMMY_CLIENT__type-undetermined.pdf
    """
    safe_labels = [label.replace(":", "-") for label in labels]
    new_stem = f"{original_path.stem}__{'__'.join(safe_labels)}"
    return original_path.with_name(new_stem).with_suffix(original_path.suffix)

def process_document(file_path: Path) -> None:
    """
    Process a single document: extract text, classify it,
    rename the file to include labels, and move it to processed_documents.
    """
    logging.info(f"Processing document: {file_path.name}")
    
    # Verify file extension is supported
    if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        logging.warning(f"Unsupported file type for {file_path.name}. Skipping.")
        return

    try:
        # Extract text from the document (the implementation is in your attachment module)
        document_text = extract_text(file_path)
        if not document_text:
            logging.warning(f"No text extracted from {file_path.name}. Skipping classification.")
            return

        # Create classification service instance and classify document text
        service = ClassificationService()
        labels = asyncio.run(service.classify_document(document_text, source_type="text"))
        if not isinstance(labels, list):
            logging.error(f"Classification service returned an unexpected type: {type(labels)}. Expected a list.")
            return

        # Generate a new filename with appended classification labels
        new_file_path = generate_new_filename(file_path, labels)
        logging.info(f"Renaming and moving file to: {new_file_path}")

        # Move the file to the processed_documents folder with the new name
        final_path = PROCESSED_DIR / new_file_path.name
        shutil.move(str(file_path), str(final_path))
        logging.info(f"File {file_path.name} processed and moved as {final_path.name}")

    except Exception as e:
        logging.error(f"Error processing {file_path.name}: {e}")

# --- Watchdog Event Handler ---

class DocumentEventHandler(FileSystemEventHandler):
    """Watchdog event handler to process new documents."""
    def on_created(self, event):
        # Ignore directories and temporary files
        if event.is_directory:
            return

        new_file = Path(event.src_path)
        if new_file.suffix.lower() in SUPPORTED_EXTENSIONS:
            # Delay briefly to allow file write operations to complete
            time.sleep(1)
            logging.info(f"Detected new file: {new_file.name}")
            process_document(new_file)
        else:
            logging.debug(f"Ignored file (unsupported extension): {new_file.name}")

# --- CLI Commands using Click ---

@click.group()
def cli():
    """
    Document Classification & Labeling CLI Tool

    Use this tool to either process specific document files
    or to continuously watch the incoming_documents folder.
    """
    ensure_directories()

@cli.command()
@click.argument('files', nargs=-1, type=click.Path(exists=True, path_type=Path))
def classify(files):
    """
    Process one or more document files by extracting text, classifying,
    and then renaming/moving the file based on the classification labels.
    
    Example:
        python document_classifier.py classify incoming_documents/report.pdf
    """
    if not files:
        logging.info("No files specified. Exiting.")
        sys.exit(0)

    for file_path in files:
        process_document(file_path)

@cli.command()
def watch():
    """
    Continuously watch the incoming_documents folder for new files
    and process them automatically.
    """
    event_handler = DocumentEventHandler()
    observer = Observer()
    observer.schedule(event_handler, str(INCOMING_DIR), recursive=False)
    observer.start()
    logging.info(f"Watching directory: {INCOMING_DIR.resolve()}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Stopping watcher...")
        observer.stop()
    observer.join()

if __name__ == '__main__':
    cli()