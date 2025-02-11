"""
Document Classification CLI

Command-line interface for classifying documents using our classification service.
"""
import asyncio
import click
from pathlib import Path
from typing import Optional
from ..services.classification_service import ClassificationService

@click.group()
def cli():
    """Document classification command line interface."""
    pass

@cli.command()
@click.argument('source', type=click.Path(exists=True))
@click.option('--classifier', '-c', default='docling',
              type=click.Choice(['docling', 'gemini']),
              help='Classifier to use')
@click.option('--config-dir', type=click.Path(exists=True),
              help='Path to configuration directory')
@click.option('--metadata', '-m', multiple=True,
              help='Additional metadata in key=value format')
async def classify(source: str,
                  classifier: str,
                  config_dir: Optional[str],
                  metadata: tuple) -> None:
    """Classify a single document or directory of documents."""
    service = ClassificationService(
        config_dir=Path(config_dir) if config_dir else None,
        classifier_name=classifier
    )
    
    # Parse metadata
    metadata_dict = {}
    for item in metadata:
        key, value = item.split('=', 1)
        metadata_dict[key.strip()] = value.strip()
    
    source_path = Path(source)
    if source_path.is_file():
        # Classify single file
        result = await service.classify_document(
            source_path,
            source_type="file",
            metadata=metadata_dict
        )
        _display_result(result)
    elif source_path.is_dir():
        # Classify all files in directory
        files = list(source_path.glob("*.*"))
        results = await service.classify_batch(
            files,
            source_type="file",
            metadata=[metadata_dict] * len(files)
        )
        for file_path, result in zip(files, results):
            click.echo(f"\nFile: {file_path}")
            _display_result(result)
            
@cli.command()
@click.argument('directory', type=click.Path(exists=True))
@click.option('--classifier', '-c', default='docling',
              type=click.Choice(['docling', 'gemini']),
              help='Classifier to use')
@click.option('--config-dir', type=click.Path(exists=True),
              help='Path to configuration directory')
@click.option('--pattern', default="*.*",
              help='Glob pattern for files to watch')
@click.option('--recursive/--no-recursive', default=False,
              help='Watch subdirectories recursively')
async def watch(directory: str,
               classifier: str,
               config_dir: Optional[str],
               pattern: str,
               recursive: bool) -> None:
    """Watch a directory for new documents and classify them."""
    service = ClassificationService(
        config_dir=Path(config_dir) if config_dir else None,
        classifier_name=classifier
    )
    
    click.echo(f"Watching directory: {directory}")
    click.echo(f"Pattern: {pattern}")
    click.echo(f"Recursive: {recursive}")
    click.echo(f"Classifier: {classifier}")
    click.echo("\nPress Ctrl+C to stop watching\n")
    
    await service.watch_directory(
        directory=directory,
        pattern=pattern,
        recursive=recursive
    )

def _display_result(result):
    """Display classification result in a formatted way."""
    click.echo("\nClassification Result:")
    click.echo(f"Document Type: {result.document_type}")
    click.echo(f"Confidence: {result.confidence:.2%}")
    
    if result.entities:
        click.echo("\nEntities:")
        for entity_type, entities in result.entities.items():
            if entities:
                click.echo(f"  {entity_type}:")
                for entity in entities:
                    click.echo(f"    - {entity}")
                    
    if result.key_fields:
        click.echo("\nKey Fields:")
        for field_type, fields in result.key_fields.items():
            if fields:
                click.echo(f"  {field_type}:")
                for field in fields:
                    click.echo(f"    - {field}")
                    
    if result.flags:
        click.echo("\nFlags:")
        for flag in result.flags:
            click.echo(f"  - {flag}")
            
    if result.summary:
        click.echo(f"\nSummary: {result.summary}")

def main():
    """Entry point for the CLI."""
    asyncio.run(cli()) 