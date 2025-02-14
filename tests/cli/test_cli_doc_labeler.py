# test_labeler.py
import pytest
import pathlib
import json
from datetime import datetime
from your_script_name import (  # Replace your_script_name.py
    Config,
    DocumentMetadata,
    MetadataStore,
    FileHandler,
    PromptHandler,
    DocumentLabeler,
)


# Mock questionary.autocomplete and questionary.text
@pytest.fixture
def mock_questionary(monkeypatch):
    def mock_autocomplete(*args, **kwargs):
        class MockAutocompleteResult:
            def ask(self):
                # Simulate user input based on the 'question'
                question_text = args[0]
                if question_text == "State code:":
                    return "AL"
                elif question_text == "Client code:":
                    return "ABC: Some Client"  # Simulate selecting from list
                else:
                    return "Default"  # Fallback

        return MockAutocompleteResult()

    def mock_rawselect(*args, **kwargs):
        class MockRawselectResult:
            def __init__(self):
                self.call_count = 0
                self.question_text = args[0]

            def ask(self):
                self.call_count += 1
                if self.question_text == "Select base type:":
                    return "NEW"
                if (
                    self.question_text
                    == "Select product categories (Enter to toggle, [Done] to finish):"
                ):
                    if self.call_count == 1:
                        return "Biostimulants"  # Simulate first selection
                    elif self.call_count == 2:
                        return "Commercial Fertilizers"  # Simulate 2nd
                    elif self.call_count == 3:
                        return "__DONE__"  # Simulate exit.
                    else:
                        return "__DONE__"

        return MockRawselectResult()

    def mock_text(*args, **kwargs):
        class MockTextResult:
            def ask(self):
                # Simulate user input for the description
                return "test-description"

        return MockTextResult()

    monkeypatch.setattr(questionary, "autocomplete", mock_autocomplete)
    monkeypatch.setattr(questionary, "text", mock_text)
    monkeypatch.setattr(questionary, "rawselect", mock_rawselect)
    monkeypatch.setattr(
        Config,
        "get_client_choices_list",
        lambda: ["ABC: Some Client", "DEF: Other Client"],
    )


def test_prompt_handler(mock_questionary, setup_test_environment):
    """Test the prompting logic."""
    metadata = PromptHandler.prompt_for_metadata()
    assert metadata.state == "AL"
    assert metadata.client_code == "ABC"
    assert metadata.base_type == "NEW"
    assert metadata.description == "test-description"
    assert metadata.product_categories == ["Biostimulants", "Commercial Fertilizers"]

    # Test with existing data.
    existing_metadata = DocumentMetadata(
        state="CA",
        client_code="DEF",
        base_type="RENEW",
        description="old",
        expected_filename="old.pdf",
    )
    metadata2 = PromptHandler.prompt_for_metadata(existing_metadata)
    assert metadata2.state == "AL"  # Should still prompt.
    assert metadata2.client_code == "ABC"  # Should still prompt.


def test_document_labeler_integration(mock_questionary, setup_test_environment):
    """Integration test for the DocumentLabeler."""
    _, to_label_dir, labeled_dir, _, sample_pdf = setup_test_environment
    labeler = DocumentLabeler()
    labeler.label_documents([sample_pdf])

    # Check that the file was moved/copied.
    expected_filename = "AL-ABC-NEW-test-description.pdf"
    assert (labeled_dir / expected_filename).exists()

    # Check that metadata was saved.
    metadata = labeler.metadata_store.get(expected_filename)
    assert metadata.state == "AL"
    assert metadata.client_code == "ABC"
    assert metadata.base_type == "NEW"

    # Test batch mode processing
    sample_pdf2 = to_label_dir / "sample2.pdf"
    sample_pdf2.write_text("Another sample pdf")
    labeler.label_documents([])  # Process to_label directory.

    expected_filename2 = "AL-ABC-NEW-test-description.pdf"
    assert (labeled_dir / expected_filename2).exists()

    # Check list command (basic integration test)
    labeler.list_documents()  # Check it runs without errors
    # Check status command (basic integration test)
    labeler.show_status()  # Check it runs without error.
