"""
Unit tests for the document classification CLI.
"""
import pytest
from click.testing import CliRunner
from pathlib import Path
from src.cli.document_classifier import cli, classify, watch

@pytest.fixture
def cli_runner():
    """Create a Click CLI test runner."""
    return CliRunner()

def test_classify_single_file(cli_runner, test_documents_dir):
    """Test classification of a single file."""
    test_file = test_documents_dir / "test_license.txt"
    
    result = cli_runner.invoke(classify, [str(test_file)])
    
    assert result.exit_code == 0
    assert "Classification Result:" in result.output
    assert "Document Type: license" in result.output
    assert "ARB" in result.output
    assert "AL" in result.output

def test_classify_directory(cli_runner, test_documents_dir):
    """Test classification of all files in a directory."""
    result = cli_runner.invoke(classify, [str(test_documents_dir)])
    
    assert result.exit_code == 0
    # Should show results for both test files
    assert "test_license.txt" in result.output
    assert "test_registration.txt" in result.output
    assert "Document Type: license" in result.output
    assert "Document Type: registration" in result.output

def test_classifier_selection(cli_runner, test_documents_dir):
    """Test using different classifiers."""
    test_file = test_documents_dir / "test_license.txt"
    
    # Test with Docling classifier
    result_docling = cli_runner.invoke(classify, [
        str(test_file),
        "--classifier", "docling"
    ])
    
    assert result_docling.exit_code == 0
    assert "Document Type: license" in result_docling.output
    
    # Test with Gemini classifier
    result_gemini = cli_runner.invoke(classify, [
        str(test_file),
        "--classifier", "gemini"
    ])
    
    assert result_gemini.exit_code == 0
    assert "Document Type: license" in result_gemini.output

def test_metadata_option(cli_runner, test_documents_dir):
    """Test classification with metadata options."""
    test_file = test_documents_dir / "test_license.txt"
    
    result = cli_runner.invoke(classify, [
        str(test_file),
        "-m", "source=email",
        "-m", "priority=high"
    ])
    
    assert result.exit_code == 0
    assert "Classification Result:" in result.output

def test_error_handling(cli_runner):
    """Test CLI error handling."""
    # Test with non-existent file
    result = cli_runner.invoke(classify, ["/nonexistent/file.pdf"])
    assert result.exit_code != 0
    assert "Error" in result.output or "not found" in result.output
    
    # Test with invalid classifier
    result = cli_runner.invoke(classify, [
        "test.txt",
        "--classifier", "invalid"
    ])
    assert result.exit_code != 0
    assert "Error" in result.output or "Invalid" in result.output

def test_watch_command_help(cli_runner):
    """Test the watch command help text."""
    result = cli_runner.invoke(watch, ["--help"])
    
    assert result.exit_code == 0
    assert "Watch a directory" in result.output
    assert "--pattern" in result.output
    assert "--recursive" in result.output 